"""Comprovação de poderes no formato da Res. CONTRAN nº 1.027/2026, art. 28, § 7º, e o parecer em HTML/PDF.

§ 7º: "Quando o antigo ou o novo proprietário for pessoa jurídica, a assinatura será admitida mediante comprovação
eletrônica dos poderes do signatário, por consulta a bases oficiais ou por instrumento de outorga verificável, com
identificação do outorgante, do outorgado, dos poderes conferidos, do prazo de validade e de eventual revogação [...]"
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .domain import Severidade, Veredito, para_json
from .engine import Alternativa, Motor, Resultado, _fmt_data
from .ids import formatar_documento

NORMA_7 = "Resolução CONTRAN nº 1.027/2026, art. 28, § 7º"
TEMPLATES = Path(__file__).parent / "templates"


def _qualidade(motor: Motor, chave: str, alt: Alternativa | None) -> str:
    reg = None
    for a in (motor.kb.atos or []):
        for adm in a.administradores:
            if adm.pessoa == chave:
                reg = adm
    if alt and alt.via == "procuracao":
        return "procurador(a)" if chave in _outorgados(motor, alt) else (reg.cargo if reg else "assinatura conjunta exigida")
    if alt and alt.via == "substabelecimento":
        return "substabelecido(a)" if chave in _substabelecidos(motor, alt) else (reg.cargo if reg else "assinatura conjunta")
    if reg:
        return reg.cargo
    poa = next((p for p in motor.kb.procuracoes if chave in p.outorgados), None)
    if poa:
        return f"procurador(a) pela procuração de {_fmt_data(poa.data)}"
    sub = next((s for s in motor.kb.substabelecimentos if chave in s.substabelecidos), None)
    if sub:
        return f"substabelecido(a) em {_fmt_data(sub.data)}"
    return "sócio(a) sem poder de administração" if any(chave in a.socios for a in motor.kb.atos) else "sem vínculo nos documentos"


def _outorgados(motor: Motor, alt: Alternativa) -> set[str]:
    return set().union(*[set(p.outorgados) for p in motor.kb.procuracoes if p.id in alt.cadeia]) if alt.cadeia else set()


def _substabelecidos(motor: Motor, alt: Alternativa) -> set[str]:
    return set().union(*[set(s.substabelecidos) for s in motor.kb.substabelecimentos if s.id in alt.cadeia]) if alt.cadeia else set()


def comprovacao_poderes(res: Resultado, motor: Motor, pedido) -> dict[str, Any]:
    kb = motor.kb
    emp = kb.empresa
    esc = res.escolhida
    status = {Veredito.PODE: "comprovada", Veredito.INDETERMINADO: "pendente", Veredito.NAO_PODE: "não comprovada"}[res.veredito]
    outorgados = []
    for a in res.assinantes:
        ch = a["chave"]
        outorgados.append({"nome": a["nome"], "cpf": a.get("cpf"), "identificacao": a["criterio"],
                           "qualidade": _qualidade(motor, ch, esc) if not ch.startswith("?") else "não consta nos documentos"})
    poderes, prazo, revogacao, fontes = [], [], [], []
    pf = emp.tipo == "PF"
    titular = [a.pessoa for ato in kb.atos for a in ato.administradores][:1] if pf else []
    cpf_titular = formatar_documento(kb.pessoas[titular[0]].cpf) if titular and kb.pessoas.get(titular[0]) else None
    if pf and esc and esc.via == "contrato":  # o próprio titular assina
        poderes.append("Assinatura do próprio " + ("proprietário" if pedido.lado == "vendedor" else "comprador")
                       + " (pessoa física): não há poderes a comprovar além da identidade (CPF).")
        prazo.append("Não se aplica (não há outorga).")
        revogacao.append("Não se aplica (não há outorga).")
        fontes += [a.fonte for ato in kb.atos for a in ato.administradores]
    elif not res.assinantes:  # consulta: todos os caminhos válidos, com prazo de cada procuração
        for a in res.alternativas:
            poderes.append(f"{motor.nomes(a.pessoas)} — {a.descricao}")
            for doc_id in a.cadeia:
                pr = next((x for x in kb.procuracoes if x.id == doc_id), None)
                if pr:
                    fim = motor._fim_procuracao(pr)
                    prazo.append(f"{motor.nomes(pr.outorgados)}: procuração válida até {_fmt_data(fim)}" if fim else
                                 f"{motor.nomes(pr.outorgados)}: procuração sem prazo final (expedida em {_fmt_data(pr.data)})")
        if not poderes:
            poderes.append("Nenhuma combinação válida com os documentos apresentados.")
        prazo = prazo or ["Administradores: ver mandatos no ato societário vigente."]
        revogacao.append("Confirmar com certidão atualizada do cartório (procurações) e " + _certidao(kb.empresa)
                         + " (atos societários) no momento da assinatura.")
    elif esc and esc.via == "contrato":
        for r in res.formula.regras:
            poderes.append(f"{r.fonte.doc_titulo}, {r.fonte.clausula or 'cláusula de administração'}: "
                           f"{_regra_txt(r, len(esc.pessoas))}")
            fontes.append(r.fonte)
        if not res.formula.regras:
            poderes.append("Regra supletiva do Código Civil (o ato constitutivo não define a forma de assinar).")
        for adm in res.regime.administradores:
            if adm.pessoa in esc.pessoas:
                fim = adm.termino or motor._termino_mandato(adm, res.regime.atos)
                prazo.append(f"{motor.nome(adm.pessoa)} ({adm.cargo}): "
                             + (f"mandato até {_fmt_data(fim)}" if fim else "mandato por prazo indeterminado"))
                fontes.append(adm.fonte)
        revogacao.append("Poder decorre do ato constitutivo vigente na data da venda; recomenda-se "
                         + _certidao(kb.empresa) + " para afastar alteração posterior ainda não apresentada.")
    elif esc:
        for doc_id in esc.cadeia:
            p = next((x for x in kb.procuracoes if x.id == doc_id), None)
            s = next((x for x in kb.substabelecimentos if x.id == doc_id), None)
            if p:
                forma = "Procuração pública" if p.forma == "publica" else "Procuração particular"
                local = ", ".join(filter(None, [p.cartorio, f"livro {p.livro}" if p.livro else None,
                                                f"folhas {p.folhas}" if p.folhas else None]))
                quem_outorgou = (f"{p.outorgante_nome} (pessoa física)" if p.outorgante_tipo == "PF" else
                                 f"{p.outorgante_nome} (repr. {motor.nomes(p.representantes)})")
                poder_txt = ("poderes especiais e expressos para comprar veículos" if pedido.lado == "comprador" and p.adquirir_veiculos
                             else "poderes especiais e expressos para vender veículos" if p.alienar_veiculos else "sem poder de venda")
                poderes.append(f"{forma} de {_fmt_data(p.data)}{' (' + local + ')' if local else ''}, outorgada por "
                               f"{quem_outorgou}: "
                               + poder_txt
                               + (" e assinar a ATPV/ATPV-e" if p.assinar_atpv else "")
                               + (f"; somente em conjunto com {p.exige_conjunto_com}" if p.exige_conjunto_com not in ("nenhum", "outro") else ""))
                fim = motor._fim_procuracao(p)
                prazo.append(f"{forma} válida até {_fmt_data(fim)}" if fim else f"{forma} sem prazo final (expedida em {_fmt_data(p.data)})")
                revs = [r for r in kb.revogacoes if p.id in r.procuracao_ids]
                revogacao.append(("Revogada em " + _fmt_data(revs[0].data)) if revs else
                                 "Nenhuma revogação nos documentos apresentados; a revogação fica anotada na serventia de "
                                 "origem — confirmar com certidão atualizada do cartório.")
                fontes += [f for f in (p.fontes.get("poderes"), p.fontes.get("validade")) if f]
            if s:
                poderes.append(f"Substabelecimento {s.reserva.replace('_', ' ')} de {_fmt_data(s.data)}: "
                               f"{motor.nome(s.substabelecente)} → {motor.nomes(s.substabelecidos)}")
                fontes.append(s.fonte)
    else:
        for b in res.bloqueadas:
            if b.pessoas & frozenset(a["chave"] for a in res.assinantes):
                motivos = [x.titulo for x in b.achados if x.severidade == Severidade.BLOQUEIO]
                poderes.append(f"{b.descricao}: não comprova poderes ({'; '.join(dict.fromkeys(motivos))}).")
        if not poderes and pf:
            poderes.append(f"Titular: {emp.razao_social} (CPF {cpf_titular or '—'}). Só ele assina, ou procurador com "
                           f"poderes para {'vender' if pedido.lado == 'vendedor' else 'comprar'} este veículo.")
            nomes_ass = ", ".join(a["nome"] for a in res.assinantes)
            poderes.append(f"Quem vai assinar ({nomes_ass}) não é o titular e não apresentou procuração válida.")
        if not poderes:
            exig = " ou ".join(motor.nomes(a) for a in res.formula.alternativas[:5]) or "regularização da administração"
            for r in res.formula.regras:
                poderes.append(f"{r.fonte.doc_titulo}{', ' + r.fonte.clausula if r.fonte.clausula else ''}: para este veículo, "
                               f"exige {exig}.")
                fontes.append(r.fonte)
            nomes_ass = ", ".join(a["nome"] for a in res.assinantes)
            poderes.append(f"Assinantes informados ({nomes_ass}) não atendem a essa exigência." if res.formula.regras else
                           f"Os assinantes informados ({nomes_ass}) não satisfazem nenhuma combinação de assinatura prevista.")
        prazo.append("—")
        revogacao.append("—")
    return {
        "norma": NORMA_7,
        "status": status,
        "outorgante": {"nome": emp.razao_social, "cnpj": emp.cnpj, "tipo": emp.tipo, "cpf": cpf_titular,
                       "documento": emp.cnpj or cpf_titular,
                       "atos_vigentes": [] if pf else [{"titulo": a.titulo, "doc": a.doc_id,
                                                        "efeito": a.data_efeito.isoformat() if a.data_efeito else None}
                                                       for a in res.regime.atos],
                       "titularidade": (kb.atos[0].administradores[0].fonte.doc_titulo if pf and kb.atos else None)},
        "outorgado": outorgados,
        "poderes_conferidos": poderes,
        "prazo_validade": prazo,
        "revogacao": revogacao,
        "fontes": [para_json(f) for f in fontes],
        "documentos_verificaveis": [{"id": d.id, "titulo": d.titulo, "arquivo": Path(d.arquivo).name} for d in kb.documentos.values()],
    }


def _certidao(emp) -> str:
    """Associação e sociedade simples registram os atos no RCPJ; as demais, na Junta Comercial."""
    if emp.tipo in ("ASSOCIACAO", "SS") or getattr(emp, "subtipo", None) in ("ASSOCIACAO", "SS"):
        return "certidão atualizada do Registro Civil das Pessoas Jurídicas"
    return "certidão simplificada atualizada da Junta Comercial"


def _regra_txt(r, n: int) -> str:
    """Cláusula com cargos ('o Presidente', 'o Diretor-Presidente em conjunto com o Diretor Financeiro') diz o cargo."""
    cargos = [p.split(":", 1)[1] for p in r.pessoas if p.startswith("@cargo:")]
    if cargos and len(cargos) == len(r.pessoas):
        if r.modo == "conjunto" and len(cargos) > 1:
            return "assinam em conjunto: " + " e ".join(cargos)
        return ("assina: " if len(cargos) == 1 else "assina qualquer um destes: ") + " ou ".join(cargos) + \
            (" (sozinho)" if r.modo in ("isolado", "nao_especificado") else "")
    return _modo_txt(r.modo, n)


def _modo_txt(modo: str, n: int) -> str:
    return {"isolado": "qualquer administrador designado assina sozinho",
            "conjunto": "assinatura conjunta exigida",
            "quantidade_minima": "número mínimo de assinaturas exigido",
            "misto": "combinações alternativas de assinatura",
            "nao_especificado": "forma de atuação não especificada (regra supletiva: atuação separada)"}.get(modo, modo) + \
        (" — exigida a assinatura indicada na cláusula específica" if n == 1 and modo == "isolado" else "")


# ------------------------------------------------------------------------------------- parecer
_env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))


def _fmt_data_iso(s: str | None) -> str:
    if not s:
        return "—"
    try:
        return date.fromisoformat(s[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return s


_env.filters["data"] = _fmt_data_iso
_env.filters["moeda"] = lambda v: "—" if v in (None, "") else "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


ORDEM = {"bloqueio": 0, "alerta": 1, "atencao": 2, "info": 3, "ok": 4}


def itens_verificacao(resultado: dict) -> list[dict]:
    """Achados do caminho escolhido + globais, sem repetição, do mais grave ao OK."""
    brutos = ((resultado.get("caminho_escolhido") or {}).get("achados") or []) + (resultado.get("achados") or [])
    vistos, out = set(), []
    for a in brutos:
        k = (a["codigo"], a["detalhe"])
        if k not in vistos:
            vistos.add(k)
            out.append(a)
    return sorted(out, key=lambda a: ORDEM.get(a["severidade"], 5))


def html_parecer(resultado: dict, auditoria: dict | None = None) -> str:
    lados = resultado.get("lados") or {resultado.get("lado", "vendedor"): resultado}
    documentos, vistos = [], set()
    for rr in lados.values():
        for d in rr.get("documentos", []):
            if d["id"] not in vistos:
                vistos.add(d["id"])
                documentos.append(d)
    return _env.get_template("parecer.html").render(
        r=resultado, a=auditoria or {}, lados=lados, documentos=documentos,
        itens_lados={k: itens_verificacao(v) for k, v in lados.items()})


def pdf_parecer(resultado: dict, auditoria: dict | None = None) -> bytes:
    from weasyprint import HTML

    return HTML(string=html_parecer(resultado, auditoria)).write_pdf()
