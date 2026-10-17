"""Leitura dos documentos pelo LLM (extração estruturada) — o "agente" que lê como um advogado.

Para cada documento:
1. classifica (heurística pelo título; LLM só se precisar);
2. roda as tarefas do tipo (partes + regras, procuração, substabelecimento, ata...), com JSON Schema garantido;
3. opcional: N amostras por tarefa (autoconsistência) — escolhe a resposta modal e registra a concordância,
   que entra no score: se o modelo "muda de ideia" entre amostras, o caso vai para a faixa intermediária.
CRLV é lido por expressão regular (campos rotulados), com o LLM de reserva.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from . import prompts as pr
from . import schemas as sc
from .consolidate import LeituraDocumento
from .ids import normalizar_nome
from .ingest import Documento, carregar
from .lexicon import norm, parse_data
from .llm import ErroLLM, Provedor

Progresso = Callable[[str, dict], None]
RAIZ = Path(__file__).resolve().parents[2]
CACHE_DIR = Path(os.environ.get("OUTORGA_CACHE", RAIZ / ".cache" / "leituras"))
EXTENSOES = {".pdf", ".docx", ".txt", ".md", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
MAX_CHARS = 90_000  # ~25K tokens: cabe no contexto de 32K do perfil local

TIPOS_TITULO = [
    (r"substabelecimento", "substabelecimento", "Substabelecimento"),
    (r"revoga[cç][aã]o de procura|revogacao de procura|escritura publica de revogacao", "revogacao_procuracao", "Revogação de procuração"),
    (r"certificado de registro e licenciamento|crlv", "crlv", "CRLV"),
    (r"autorizacao para transferencia de propriedade", "atpv", "ATPV"),
    (r"ata da reuniao do conselho de administracao|ata de reuniao do conselho", "ata_conselho", "Ata do Conselho de Administração"),
    (r"ata da assembleia|ata de assembleia", "ata_assembleia", "Ata de Assembleia"),
    (r"ata da reuniao de socios|ata de reuniao de socios|ata de reuniao dos socios", "ata_reuniao_socios", "Ata de Reunião de Sócios"),
    (r"estatuto social", "estatuto_social", "Estatuto Social"),
    (r"requerimento de empresario|empresario individual|microempreendedor individual|\bccmei\b", "requerimento_empresario",
     "Requerimento de Empresário"),
    (r"alteracao.{0,40}consolida|consolidacao do contrato", "contrato_consolidado", "Alteração e Consolidação do Contrato Social"),
    (r"alteracao (do )?contrat|alteracao contratual", "alteracao_contratual", "Alteração Contratual"),
    (r"ato constitutivo|unipessoal", "ato_constitutivo_slu", "Ato Constitutivo (SLU)"),
    (r"contrato social", "contrato_social", "Contrato Social"),
    (r"procuracao|procurador", "procuracao", "Procuração"),
]


def classificar_heuristica(doc: Documento) -> sc.Classificacao | None:
    """Pelo título: primeiro os 600 primeiros caracteres (onde fica o título), depois 1.500."""
    for janela in (600, 1500):
        topo = norm(doc.texto[:janela])
        achados = []
        for ordem, (padrao, tipo, titulo) in enumerate(TIPOS_TITULO):
            m = re.search(padrao, topo)
            if m:
                achados.append((m.start(), ordem, tipo, titulo))
        if achados:
            _, _, tipo, titulo = min(achados)  # o que aparece primeiro é o título
            data = _data_fecho(doc.texto)
            return sc.Classificacao(tipo=tipo, titulo=titulo + (f" ({data[:4]})" if data else ""), data_documento=data,
                                    confianca=0.9 if janela == 600 else 0.75)
    return None


def _data_fecho(texto: str) -> str | None:
    """Última data por extenso do documento (o fecho), ignorando a chancela da Junta."""
    achados = re.findall(r"\b(\d{1,2})º? de (janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|"
                         r"novembro|dezembro) de (\d{4})", texto, re.I)
    if achados:
        d = parse_data(" de ".join(achados[-1]))
        return d.isoformat() if d else None
    return None


def texto_para_llm(doc: Documento) -> str:
    """Documento inteiro se couber; senão cabeçalho + cláusulas relevantes + fecho (sem truncar silenciosamente)."""
    t = doc.texto
    if len(t) <= MAX_CHARS:
        return t
    paragrafos = re.split(r"\n\s*\n", t)
    chave = re.compile(r"administra|represent|assina|procura|alien|vend|veicul|capital|socio|quota|poder|diretor|conselho|"
                       r"mandato|prazo|revoga|substabelec|conjunt|isolad", re.I)
    cab, fim = t[:6000], t[-4000:]
    meio = [p for p in paragrafos if chave.search(norm(p))]
    corpo = "\n\n".join(meio)
    return f"{cab}\n\n[... trechos sem relação com representação omitidos ...]\n\n{corpo[:MAX_CHARS - 10000]}\n\n{fim}"


# --------------------------------------------------------------------------------- CRLV (regex)
_ROTULOS_CRLV = {
    "placa": r"PLACA\s*\n\s*([A-Z]{3}-?\d[A-Z0-9]\d{2})",
    "renavam": r"RENAVAM\s*\n\s*(\d{9,11})",
    "chassi": r"CHASSI\s*\n\s*([A-HJ-NPR-Z0-9]{17})",
    "marca_modelo": r"MARCA\s*/\s*MODELO\s*/\s*VERS[ÃA]O\s*\n\s*(.+)",
    "proprietario_nome": r"\bNOME\s*\n\s*(.+)",
    "proprietario_documento": r"CPF\s*/\s*CNPJ\s*\n\s*([\d./-]{11,18})",
    "ano_fabricacao": r"ANO FABRICA[ÇC][ÃA]O\s*\n\s*(\d{4})",
    "ano_modelo": r"ANO MODELO\s*\n\s*(\d{4})",
}


def _rotulo(t: str, rotulo: str, valor: str = r"(.+)") -> str | None:
    m = re.search(rotulo + r"\s*[:\n]\s*" + valor, t, re.I)
    return m.group(1).strip() if m else None


def atpv_por_regex(doc: Documento) -> sc.ExtracaoATPV | None:
    """ATPV-e com campos rotulados (VENDEDOR / COMPRADOR em blocos)."""
    t = doc.texto
    bloco_v = (re.search(r"IDENTIFICA[ÇC][ÃA]O DO VENDEDOR[^\n]*\n(.*?)(?=IDENTIFICA[ÇC][ÃA]O DO COMPRADOR)", t, re.S | re.I)
               or re.search(r"VENDEDOR[^\n]*\n(.*?)(?=COMPRADOR)", t, re.S | re.I))
    bloco_c = (re.search(r"IDENTIFICA[ÇC][ÃA]O DO COMPRADOR[^\n]*\n(.*?)(?=DADOS DA VENDA|ASSINATURA|$)", t, re.S | re.I)
               or re.search(r"COMPRADOR[^\n]*\n(.*?)(?=ASSINATURA|$)", t, re.S | re.I))
    if not (bloco_v and bloco_c):
        return None

    def parte(b: str) -> sc.ParteATPV | None:
        # nome longo quebra em mais de uma linha no PDF: vai até o rótulo seguinte
        m = re.search(r"Nome(?: / Raz[ãa]o social)?\s*[:\n]\s*(.+?)\s*(?=\n\s*(?:CPF\s*/\s*CNPJ|Munic[íi]pio|Endere[çc]o)|$)", b, re.S | re.I)
        nome = re.sub(r"\s*\n\s*", " ", m.group(1)).strip() if m else None
        doc_ = _rotulo(b, r"CPF\s*/\s*CNPJ", r"([\d./-]{11,18})")
        if not nome:
            return None
        from .ids import so_digitos
        return sc.ParteATPV(tipo="PJ" if len(so_digitos(doc_)) == 14 else "PF", nome=nome, documento=doc_)

    v, c = parte(bloco_v.group(1)), parte(bloco_c.group(1))
    if not (v and c):
        return None
    valor = _rotulo(t, r"Valor(?: declarado)?(?: da venda)?", r"R\$\s*([\d.,]+)")
    data = _rotulo(t, r"Data da venda", r"(\d{2}/\d{2}/\d{4})")
    d = parse_data(data) if data else None
    return sc.ExtracaoATPV(numero=_rotulo(t, r"N[úu]mero da ATPV-e"), placa=_rotulo(t, r"Placa", r"([A-Z]{3}-?\d[A-Z0-9]\d{2})"),
                           renavam=_rotulo(t, r"RENAVAM", r"(\d{9,11})"), chassi=_rotulo(t, r"Chassi", r"([A-HJ-NPR-Z0-9]{17})"),
                           marca_modelo=_rotulo(t, r"Marca\s*/\s*Modelo"),
                           valor=float(valor.replace(".", "").replace(",", ".")) if valor else None,
                           data=d.isoformat() if d else None, vendedor=v, comprador=c, assinaturas=_assinaturas_atpv(t))


def _assinaturas_atpv(t: str) -> list[sc.AssinaturaATPV]:
    """Assinaturas eletrônicas já registradas: 'Pelo vendedor: NOME (CPF ...)' ou 'Assinado ... por NOME (CPF ...) ... comprador'."""
    m = re.search(r"ASSINATURAS?[^\n]*\n(.*)", t, re.S | re.I)
    if not m:
        return []
    out = []
    for linha in m.group(1).splitlines():
        a = re.search(r"pel[oa]\s+(vendedor|comprador)\s*:\s*([^\n(]+?)\s*\(\s*CPF\s*:?\s*([\d.\-]{11,14})\s*\)", linha, re.I)
        if not a:
            b = re.search(r"assinad[oa] (?:eletronicamente|digitalmente) por\s+([^\n(,]+?)\s*[(,]\s*CPF\s*:?\s*([\d.\-]{11,14})"
                          r".*?(vendedor|comprador)", linha, re.I)
            if b:
                out.append(sc.AssinaturaATPV(nome=b.group(1).strip(), cpf=b.group(2), lado=b.group(3).lower()))
            continue
        if "pendente" not in a.group(2).lower():
            out.append(sc.AssinaturaATPV(nome=a.group(2).strip(), cpf=a.group(3), lado=a.group(1).lower()))
    return out


def crlv_por_regex(doc: Documento) -> sc.ExtracaoCRLV | None:
    t = doc.texto
    v = {}
    for campo, padrao in _ROTULOS_CRLV.items():
        m = re.search(padrao, t, re.I)
        v[campo] = m.group(1).strip() if m else None
    if not (v["placa"] and v["proprietario_nome"]):
        return None
    for k in ("ano_fabricacao", "ano_modelo"):
        v[k] = int(v[k]) if v[k] else None
    return sc.ExtracaoCRLV(**v)


# ------------------------------------------------------------------------------ autoconsistência
def _assinatura(tarefa: str, obj: dict) -> str:
    def nomes(lst):
        return tuple(sorted(normalizar_nome(x if isinstance(x, str) else x.get("nome", "")) for x in lst or []))

    if tarefa == "regras":
        return json.dumps(sorted([(r.get("escopo"), r.get("modo"), nomes(r.get("pessoas")), r.get("valor_acima_de"),
                                   bool(r.get("exige_aprovacao_socios")), (r.get("veiculo") or {}).get("placa"))
                                  for r in obj.get("regras", [])], key=str), default=str)
    if tarefa == "partes":
        return json.dumps([nomes(obj.get("administradores")),
                           sorted((normalizar_nome(s.get("nome")), round(s.get("percentual") or 0)) for s in obj.get("socios", []))],
                          default=str)
    if tarefa == "procuracao":
        o, p, v = obj.get("outorgante", {}), obj.get("poderes", {}), obj.get("validade", {})
        return json.dumps([o.get("tipo"), nomes(o.get("representantes")), nomes(obj.get("outorgados")), p.get("alienar_veiculos"),
                           p.get("apenas_administracao_geral"), p.get("abrangencia"), p.get("exige_conjunto_com"),
                           v.get("data_fim"), obj.get("substabelecimento", {}).get("regra"), obj.get("atuacao_outorgados")],
                          default=str)
    if tarefa == "substabelecimento":
        return json.dumps([normalizar_nome(obj.get("substabelecente", {}).get("nome")), nomes(obj.get("substabelecidos")),
                           obj.get("reserva"), obj.get("todos_os_poderes"), obj.get("alienar_veiculos")], default=str)
    return json.dumps(obj, sort_keys=True, default=str)


TAREFAS: dict[str, tuple[str, type[BaseModel]]] = {
    "partes": (pr.PARTES, sc.ExtracaoPartes),
    "regras": (pr.REGRAS, sc.ExtracaoRegras),
    "ata": (pr.ATA, sc.ExtracaoAta),
    "procuracao": (pr.PROCURACAO, sc.ExtracaoProcuracao),
    "substabelecimento": (pr.SUBSTABELECIMENTO, sc.ExtracaoSubstabelecimento),
    "revogacao": (pr.REVOGACAO, sc.ExtracaoRevogacao),
    "crlv": (pr.CRLV, sc.ExtracaoCRLV),
    "atpv": (pr.ATPV, sc.ExtracaoATPV),
    "classificar": (pr.CLASSIFICAR, sc.Classificacao),
}
POR_TIPO = {
    "contrato_social": ["partes", "regras"], "alteracao_contratual": ["partes", "regras"],
    "contrato_consolidado": ["partes", "regras"], "estatuto_social": ["partes", "regras"],
    "ato_constitutivo_slu": ["partes", "regras"], "requerimento_empresario": ["partes"],
    "ata_reuniao_socios": ["ata"], "ata_assembleia": ["ata"], "ata_conselho": ["ata"],
    "procuracao": ["procuracao"], "substabelecimento": ["substabelecimento"], "revogacao_procuracao": ["revogacao"],
    "crlv": ["crlv"], "atpv": ["atpv"],
}


def _chamar(provedor: Provedor, doc_texto: str, tarefa: str, instrucao: str, schema: dict, i: int, temp: float,
            usar_cache: bool) -> tuple[dict, dict]:
    """Chamada ao LLM com cache em disco (chave = provedor, modelo, prompts, schema, texto, amostra)."""
    chave = hashlib.sha256(json.dumps([provedor.nome, provedor.modelo, pr.SISTEMA, instrucao, schema, doc_texto, i, temp],
                                      sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    arq = CACHE_DIR / f"{chave[:2]}" / f"{chave}.json"
    if usar_cache and arq.exists():
        salvo = json.loads(arq.read_text(encoding="utf-8"))
        return salvo["dados"], {**salvo["meta"], "cache": True}
    dados, meta = provedor.json(pr.SISTEMA, doc_texto, instrucao, schema, tarefa, temperatura=temp)
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps({"dados": dados, "meta": meta, "tarefa": tarefa}, ensure_ascii=False), encoding="utf-8")
    return dados, meta


def rodar_tarefa(provedor: Provedor, doc_texto: str, tarefa: str, amostras: int = 1,
                 progresso: Progresso | None = None, usar_cache: bool = True) -> tuple[BaseModel, float, list[dict]]:
    instrucao, modelo = TAREFAS[tarefa]
    schema = sc.schema_plano(modelo)
    respostas, metas = [], []
    for i in range(max(1, amostras)):
        temp = 0.2 if amostras == 1 or i == 0 else 0.8
        dados, meta = _chamar(provedor, doc_texto, tarefa, instrucao, schema, i, temp, usar_cache)
        try:
            obj = modelo.model_validate(dados)
        except ValidationError as e:
            meta["erro_validacao"] = str(e)[:500]
            continue
        respostas.append((obj, _assinatura(tarefa, dados)))
        metas.append(meta)
        if progresso:
            progresso("amostra", {"tarefa": tarefa, "i": i + 1, "n": amostras, "segundos": meta.get("segundos")})
    if not respostas:
        raise ErroLLM(f"nenhuma resposta válida para a tarefa {tarefa}")
    contagem = Counter(a for _, a in respostas)
    modal, votos = contagem.most_common(1)[0]
    escolhida = next(o for o, a in respostas if a == modal)
    return escolhida, votos / len(respostas), metas


def ler_documento(doc: Documento, provedor: Provedor, amostras: int = 1, progresso: Progresso | None = None) -> LeituraDocumento:
    def ev(nome, dados):
        if progresso:
            progresso(nome, {"doc": doc.id, "nome": doc.nome, **dados})

    texto = texto_para_llm(doc)
    cl = classificar_heuristica(doc)
    if cl is None:
        ev("tarefa_inicio", {"tarefa": "classificar"})
        cl, _, _ = rodar_tarefa(provedor, texto, "classificar")
    ev("classificado", {"tipo": cl.tipo, "titulo": cl.titulo, "data": cl.data_documento, "metodo": doc.metodo,
                        "ocr_confianca": doc.ocr_confianca, "paginas": len(doc.paginas)})
    leitura = LeituraDocumento(doc, cl)
    leitura.meta = {"tarefas": {}, "texto_truncado": len(texto) < len(doc.texto)}
    if cl.tipo == "crlv":
        c = crlv_por_regex(doc)
        if c:
            leitura.crlv = c
            leitura.meta["tarefas"]["crlv"] = {"metodo": "regex"}
            ev("tarefa_fim", {"tarefa": "crlv", "metodo": "regex"})
            return leitura
    if cl.tipo == "atpv":
        a = atpv_por_regex(doc)
        if a:
            leitura.atpv = a
            leitura.meta["tarefas"]["atpv"] = {"metodo": "regex"}
            ev("tarefa_fim", {"tarefa": "atpv", "metodo": "regex",
                              "resumo": f"vendedor {a.vendedor.nome} → comprador {a.comprador.nome} · {a.placa}"})
            return leitura
    for tarefa in POR_TIPO.get(cl.tipo, []):
        ev("tarefa_inicio", {"tarefa": tarefa})
        obj, concordancia, metas = rodar_tarefa(provedor, texto, tarefa, amostras, progresso)
        setattr(leitura, {"crlv": "crlv"}.get(tarefa, tarefa), obj)
        chave = {"procuracao": "poderes"}.get(tarefa, tarefa)
        leitura.consistencia[chave] = concordancia
        if tarefa == "procuracao":
            leitura.consistencia["outorgante"] = concordancia
        leitura.meta["tarefas"][tarefa] = {"amostras": len(metas), "concordancia": concordancia,
                                           "segundos": round(sum(m.get("segundos") or 0 for m in metas), 1),
                                           "tokens_saida": sum(m.get("tokens_saida") or 0 for m in metas),
                                           "modelo": metas[0].get("modelo") if metas else None}
        ev("tarefa_fim", {"tarefa": tarefa, "concordancia": concordancia, **leitura.meta["tarefas"][tarefa],
                          "resumo": resumo_extracao(tarefa, obj)})
    return leitura


def resumo_extracao(tarefa: str, obj: Any) -> str:
    """Uma linha legível do que foi lido (para o painel do agente)."""
    try:
        if tarefa == "partes":
            adm = ", ".join(a.nome.title() for a in obj.administradores) or "—"
            return f"{obj.empresa.razao_social} · administradores: {adm}"
        if tarefa == "regras":
            return f"{len(obj.regras)} regra(s): " + "; ".join(f"{r.escopo}/{r.modo}" for r in obj.regras[:5])
        if tarefa == "procuracao":
            p = obj.poderes
            return (f"{obj.outorgante.tipo} → {', '.join(o.nome.title() for o in obj.outorgados)} · "
                    f"{'vender' if p.alienar_veiculos else 'sem poder de venda'} · validade {obj.validade.tipo}"
                    f"{' até ' + obj.validade.data_fim if obj.validade.data_fim else ''} · substab. {obj.substabelecimento.regra}")
        if tarefa == "substabelecimento":
            return f"{obj.substabelecente.nome.title()} → {', '.join(s.nome.title() for s in obj.substabelecidos)} ({obj.reserva})"
        if tarefa == "revogacao":
            return f"revoga procuração de {obj.procuracao_revogada.data or '?'}"
        if tarefa == "atpv":
            return f"vendedor {obj.vendedor.nome} → comprador {obj.comprador.nome} · {obj.placa}"
        if tarefa == "ata":
            return "; ".join(f"{d.tipo}" for d in obj.deliberacoes)
    except Exception:  # noqa: BLE001 — resumo é cosmético
        pass
    return ""


def ler_pasta(pasta: str | Path, provedor: Provedor, amostras: int = 1, progresso: Progresso | None = None) -> list[LeituraDocumento]:
    arquivos = sorted(p for p in Path(pasta).iterdir() if p.suffix.lower() in EXTENSOES)
    return ler_arquivos(arquivos, provedor, amostras, progresso)


def ler_arquivos(arquivos: list[Path], provedor: Provedor, amostras: int = 1, progresso: Progresso | None = None) -> list[LeituraDocumento]:
    leituras = []
    for i, arq in enumerate(arquivos):
        if progresso:
            progresso("documento_inicio", {"doc": arq.stem, "nome": arq.name, "i": i + 1, "n": len(arquivos)})
        doc = carregar(arq)
        leituras.append(ler_documento(doc, provedor, amostras, progresso))
    return leituras
