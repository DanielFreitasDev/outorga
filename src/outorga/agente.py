"""Modo agente: verifica sozinho, na máquina local, os pedidos de ATPV-e que chegam numa pasta.

Cada pedido é uma subpasta (ou um .zip) dentro de ENTRADA com:
  - a ATPV-e (PDF/imagem): de onde saem veículo, vendedor, comprador, valor, data e assinaturas já feitas;
  - os documentos de cada empresa envolvida: ato constitutivo e alterações, atas, procurações,
    substabelecimentos, revogações e o CRLV;
  - opcionalmente, um pedido.json dizendo quem vai assinar por cada lado (formato da API). Sem ele, valem as
    assinaturas lidas da ATPV-e; se ainda não houver nenhuma, o parecer responde quem PODE assinar.

Uma subpasta é processada quando tem o arquivo PRONTO ou quando nenhum arquivo muda há `estabilidade` segundos
(evita pegar uma cópia pela metade). Para cada pedido o agente grava em SAIDA/<pedido>/ o resultado.json, o
parecer (PDF e HTML) e um resumo.txt; registra a análise e o hash na trilha de auditoria (a mesma da interface
web); e move a entrada para ENTRADA/processados/ (ou ENTRADA/com_erro/, com erro.txt). Se o servidor de IA local
estiver fora do ar, o pedido fica na fila e é tentado de novo.
"""

from __future__ import annotations

import json
import shutil
import signal
import time
import traceback
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from . import store
from .engine import Politica
from .extract import EXTENSOES, ler_arquivos
from .llm import provedor_padrao
from .parecer import html_parecer, pdf_parecer
from .pipeline import analisar_leituras, pedido_atpv_de_json

MARCADOR = "PRONTO"
RESERVADAS = {"processados", "com_erro"}
FAIXA = {"VERDE": "ACEITO", "AMARELO": "REVISÃO HUMANA", "VERMELHO": "RECUSADO"}
VEREDITO = {"PODE": "pode assinar", "NAO_PODE": "não pode assinar", "INDETERMINADO": "indeterminado"}


def _log(msg: str) -> None:
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def _destino_livre(base: Path) -> Path:
    if not base.exists():
        return base
    return base.with_name(f"{base.name}-{datetime.now():%Y%m%d-%H%M%S}")


def _desempacotar(zipf: Path) -> Path | None:
    """Extrai um .zip deixado na entrada para uma subpasta de mesmo nome (sem permitir caminhos fora dela)."""
    pasta = _destino_livre(zipf.with_suffix(""))
    try:
        with zipfile.ZipFile(zipf) as z:
            for info in z.infolist():
                alvo = (pasta / info.filename).resolve()
                if not alvo.is_relative_to(pasta.resolve()):
                    raise ValueError(f"caminho inválido no zip: {info.filename}")
            z.extractall(pasta)
    except (zipfile.BadZipFile, ValueError) as e:
        _log(f"zip ignorado ({zipf.name}): {e}")
        shutil.move(str(zipf), str(_destino_livre(zipf.parent / "com_erro" / zipf.name)))
        return None
    zipf.unlink()
    (pasta / MARCADOR).touch()  # o zip chegou inteiro
    return pasta


def _estado(pasta: Path) -> tuple:
    return tuple(sorted((str(f.relative_to(pasta)), f.stat().st_size, f.stat().st_mtime_ns)
                        for f in pasta.rglob("*") if f.is_file()))


def _arquivos(pasta: Path) -> list[Path]:
    return sorted(f for f in pasta.rglob("*")
                  if f.is_file() and f.suffix.lower() in EXTENSOES and not f.name.startswith("."))


def _moeda(v: float | None) -> str:
    if v is None:
        return "—"
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _data(s: str | None) -> str:
    try:
        return datetime.fromisoformat(s).strftime("%d/%m/%Y") if s else "—"
    except ValueError:
        return s or "—"


def resumo_texto(res: dict, nome: str) -> str:
    """Resumo em texto puro para quem opera o agente (o parecer completo vai no PDF)."""
    pa = res.get("pedido_atpv") or {}
    v = pa.get("veiculo") or {}
    linhas = [
        "OUTORGA · verificação de poderes de quem assina a ATPV-e (vendendo ou comprando)",
        f"Pedido: {nome} · analisado em {datetime.now():%d/%m/%Y %H:%M} · política {res.get('meta', {}).get('politica')}",
        f"Veículo: {v.get('placa') or '—'} {('(' + v['descricao'] + ')') if v.get('descricao') else ''} · "
        f"venda em {_data(pa.get('data_venda'))} · {_moeda(pa.get('valor'))}",
        "",
        f"RESULTADO: {FAIXA[res['faixa']]} · índice de aceitação {res['indice']:.0f}/100 · {VEREDITO[res['veredito']]}",
    ]
    lados = res.get("lados") or {res.get("lado", "vendedor"): res}
    for lado in ("vendedor", "comprador"):
        parte = pa.get(lado) or {}
        r = lados.get(lado)
        titulo = "VENDEDOR (antigo proprietário)" if lado == "vendedor" else "COMPRADOR (novo proprietário)"
        linhas += ["", f"{titulo}"]
        if r is None:
            if parte.get("tipo") == "PF":
                linhas.append(f"  {parte.get('nome') or '—'} · pessoa física: assina em nome próprio (fora do escopo).")
            else:
                linhas.append(f"  {parte.get('nome') or '—'} · sem verificação.")
            continue
        emp = r["empresa"]
        ident = f"CPF {emp.get('cpf') or '—'} (pessoa física)" if emp.get("tipo") == "PF" else f"CNPJ {emp.get('cnpj') or '—'}"
        linhas.append(f"  {emp.get('razao_social')} · {ident}")
        linhas.append(f"  {FAIXA[r['faixa']]} · índice {r['indice']:.0f} · {VEREDITO[r['veredito']]}")
        linhas.append(f"  {r['resumo']}")
        if r.get("assinantes"):
            linhas.append("  Vão assinar: " + ", ".join(a["nome"] if isinstance(a, dict) else str(a) for a in r["assinantes"]))
        if r.get("quem_pode"):
            linhas.append("  Quem pode assinar:")
            for alt in r["quem_pode"]:
                linhas.append("    - " + " + ".join(p["nome"] for p in alt["pessoas"]) + f" ({alt['descricao']})")
        conferir = [a for a in r.get("achados", []) if a.get("severidade") in ("bloqueio", "alerta")]
        if conferir:
            linhas.append("  Conferir:")
            for a in conferir:
                linhas.append(f"    [{a['severidade'].upper()}] {a['titulo']}: {a['detalhe']}")
    for pd in res.get("pendencias") or []:
        linhas.append(f"\nPENDÊNCIA ({pd['lado']}): {pd['mensagem']}")
    for a in res.get("avisos") or []:
        linhas.append(f"\nAviso: {a}")
    linhas += ["", f"Hash da entrada: {res.get('hash_entrada')}",
               f"Registro na trilha de auditoria: {(res.get('auditoria') or {}).get('hash')}",
               "Análise automatizada de apoio à decisão; casos fora da faixa de aceite devem ser revisados por servidor."]
    return "\n".join(linhas) + "\n"


class Agente:
    def __init__(self, entrada: Path, saida: Path, politica: Politica | None = None, intervalo: float = 5,
                 estabilidade: float = 10, amostras: int = 1):
        self.entrada, self.saida = Path(entrada), Path(saida)
        self.politica_fixa = politica
        self.intervalo, self.estabilidade, self.amostras = intervalo, estabilidade, amostras
        self.vistos: dict[str, tuple[tuple, float]] = {}
        self.parar = False
        self.status: dict[str, Any] = {"iniciado_em": store.agora(), "processados": 0, "erros": 0, "em_andamento": None}
        for p in (self.entrada, self.saida, self.entrada / "processados", self.entrada / "com_erro"):
            p.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ fila
    def _pronta(self, pasta: Path, imediato: bool) -> bool:
        if imediato or (pasta / MARCADOR).exists():
            return True
        est = _estado(pasta)
        if not est:
            return False
        ant = self.vistos.get(pasta.name)
        agora = time.monotonic()
        if ant is None or ant[0] != est:
            self.vistos[pasta.name] = (est, agora)
            return False
        return agora - ant[1] >= self.estabilidade

    def pendentes(self, imediato: bool = False) -> list[Path]:
        for z in sorted(self.entrada.glob("*.zip")):
            _desempacotar(z)
        return [p for p in sorted(self.entrada.iterdir())
                if p.is_dir() and p.name not in RESERVADAS and not p.name.startswith(".") and self._pronta(p, imediato)]

    def _gravar_status(self, prov=None) -> None:
        self.status["ultima_varredura"] = store.agora()
        if prov is not None:
            self.status["llm"] = {"provedor": prov.nome, "modelo": prov.modelo}
        (self.saida / "agente_status.json").write_text(json.dumps(self.status, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------------- um pedido
    def processar(self, pasta: Path) -> dict:
        t0 = time.time()
        pol = self.politica_fixa or store.politica_atual()
        prov = provedor_padrao()
        arq_pedido = next((f for f in (pasta / "pedido.json", pasta / "pedido.JSON") if f.exists()), None)
        pedido_d = json.loads(arq_pedido.read_text(encoding="utf-8")) if arq_pedido else {}
        pedido_atpv_de_json(pedido_d)  # valida antes de gastar tempo com a leitura
        arquivos = _arquivos(pasta)
        consulta_cpf = bool(pedido_d.get("cpf") and pedido_d.get("papel"))
        if not arquivos and not consulta_cpf:  # na consulta por CPF, o próprio dono pessoa física não precisa de documento
            raise ValueError("nenhum documento (PDF/imagem/DOCX/TXT) na pasta do pedido")
        _log(f"{pasta.name}: {len(arquivos)} documento(s) · política {pol.nome} · IA {prov.nome}/{prov.modelo}")

        def progresso(tipo: str, d: dict) -> None:
            if tipo == "classificado":
                _log(f"  · {d.get('nome')}: {d.get('titulo') or d.get('tipo')}")

        leituras = ler_arquivos(arquivos, prov, self.amostras, progresso) if arquivos else []
        aid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        res = analisar_leituras(leituras, pedido_d, pol, {"provedor": prov.nome, "modelo": prov.modelo,
                                                          "origem": "agente", "pedido_agente": pasta.name})
        store.criar_analise(aid, "agente", res["pedido_atpv"], f"{prov.nome}:{prov.modelo}", pol.nome)
        store.salvar_leituras(aid, leituras)
        h = store.auditar("analise", aid, {"hash_entrada": res["hash_entrada"], "veredito": res["veredito"],
                                           "faixa": res["faixa"], "indice": res["indice"], "politica": pol.nome},
                          f"agente · {pasta.name} · {res['veredito']} · {res['faixa']}")
        res["auditoria"] = {"hash": h}
        res["id"] = aid
        store.concluir_analise(aid, res, time.time() - t0)

        destino = _destino_livre(self.saida / pasta.name)
        destino.mkdir(parents=True)
        (destino / "resultado.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        (destino / "parecer.html").write_text(html_parecer(res, res["auditoria"]), encoding="utf-8")
        (destino / "parecer.pdf").write_bytes(pdf_parecer(res, res["auditoria"]))
        (destino / "resumo.txt").write_text(resumo_texto(res, pasta.name), encoding="utf-8")
        _log(f"{pasta.name}: {FAIXA[res['faixa']]} · índice {res['indice']:.0f} · {VEREDITO[res['veredito']]} "
             f"({time.time() - t0:.0f}s) → {destino}")
        return res

    def _concluir(self, pasta: Path, ok: bool, erro: str | None = None) -> None:
        if erro:
            (pasta / "erro.txt").write_text(erro, encoding="utf-8")
        (pasta / MARCADOR).unlink(missing_ok=True)
        shutil.move(str(pasta), str(_destino_livre(self.entrada / ("processados" if ok else "com_erro") / pasta.name)))
        self.vistos.pop(pasta.name, None)

    # ----------------------------------------------------------------- laço
    def rodar(self, uma_vez: bool = False) -> int:
        def _sinal(*_):
            self.parar = True
            _log("sinal recebido: encerrando depois do pedido atual")

        signal.signal(signal.SIGTERM, _sinal)
        signal.signal(signal.SIGINT, _sinal)
        prov = provedor_padrao()
        _log(f"agente pronto · entrada {self.entrada} · saída {self.saida} · política "
             f"{(self.politica_fixa or store.politica_atual()).nome} · IA {prov.nome}/{prov.modelo}")
        espera_llm = 0.0
        while not self.parar:
            pend = self.pendentes(imediato=uma_vez)
            disponivel = getattr(prov, "disponivel", lambda: True)
            if pend and not disponivel():
                espera_llm = min(max(espera_llm * 2, 15), 300)
                _log(f"servidor de IA indisponível; {len(pend)} pedido(s) aguardando · nova tentativa em {espera_llm:.0f}s")
                self.status["llm_indisponivel_desde"] = self.status.get("llm_indisponivel_desde") or store.agora()
                self._gravar_status(prov)
                if uma_vez:
                    return 2
                time.sleep(espera_llm)
                continue
            espera_llm = 0.0
            self.status.pop("llm_indisponivel_desde", None)
            for pasta in pend:
                if self.parar:
                    break
                self.status["em_andamento"] = pasta.name
                self._gravar_status(prov)
                try:
                    self.processar(pasta)
                    self.status["processados"] += 1
                    self._concluir(pasta, True)
                except Exception as e:  # noqa: BLE001
                    if not disponivel():  # o servidor caiu no meio: tenta de novo depois
                        _log(f"{pasta.name}: servidor de IA caiu durante a leitura; o pedido volta para a fila")
                        break
                    self.status["erros"] += 1
                    _log(f"{pasta.name}: ERRO {type(e).__name__}: {e}")
                    self._concluir(pasta, False, f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}")
                finally:
                    self.status["em_andamento"] = None
            self._gravar_status(prov)
            if uma_vez:
                break
            time.sleep(self.intervalo)
        _log("agente encerrado")
        return 0
