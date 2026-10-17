"""API HTTP (FastAPI) + interface web.

    uv run outorga serve          # http://127.0.0.1:8765

Fila única de processamento (o LLM local atende uma requisição por vez); progresso do agente por SSE.
"""

from __future__ import annotations

import asyncio
import json
import os
import queue
import threading
import time
import traceback
import uuid
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from . import store
from .domain import Severidade
from .engine import Politica
from .extract import EXTENSOES, ler_arquivos
from .llm import provedor_padrao, rotulo_ia
from .parecer import html_parecer, pdf_parecer
from .pipeline import VERSAO, analisar_leituras, pedido_atpv_de_json
from .scoring import sugerir_limiares

# Demonstração pública (ex.: VPS sem GPU): bloqueia envio de documentos e mudanças de política/revisão.
MODO_DEMO = os.environ.get("OUTORGA_MODO", "").lower() in ("demonstracao", "demo")
AVISO_DEMO = ("Desativado na demonstração pública. Rode o Outorga na sua máquina para enviar documentos "
              "(github.com/DanielFreitasDev/outorga).")


def _bloquear_na_demo() -> None:
    if MODO_DEMO:
        raise HTTPException(403, AVISO_DEMO)

RAIZ = Path(__file__).resolve().parents[2]
CORPUS = RAIZ / "corpus"
WEB = RAIZ / "web" / "dist"
AVALIACOES = RAIZ / "avaliacoes"

app = FastAPI(title="Outorga — verificação de poderes para ATPV", version=VERSAO)


# --------------------------------------------------------------------------------- política
politica_atual = store.politica_atual


def politica_dict(p: Politica, perfil: str | None = None) -> dict:
    d = {k: (v.value if isinstance(v, Severidade) else v) for k, v in asdict(p).items()}
    d["perfil"] = perfil or ("ce" if p.uf == "CE" else "generica")
    return d


# ------------------------------------------------------------------------------------- jobs
class Job:
    def __init__(self, aid: str):
        self.id = aid
        self.eventos: list[dict] = []
        self.status = "na_fila"
        self.inicio = time.time()

    def emitir(self, tipo: str, dados: dict | None = None) -> None:
        self.eventos.append({"seq": len(self.eventos), "tipo": tipo, "t": round(time.time() - self.inicio, 1), **(dados or {})})


JOBS: dict[str, Job] = {}
FILA: "queue.Queue[tuple[Job, list[Path], dict, str | None]]" = queue.Queue()


def _trabalhador() -> None:
    while True:
        job, arquivos, pedido_d, caso = FILA.get()
        job.status = "processando"
        try:
            pol = politica_atual()
            prov = provedor_padrao()
            job.emitir("inicio", {"documentos": len(arquivos), "provedor": prov.nome, "modelo": prov.modelo, "politica": pol.nome})
            leituras = ler_arquivos(arquivos, prov, amostras=int(pedido_d.get("amostras") or 1),
                                    progresso=lambda tipo, dados: job.emitir(tipo, dados))
            store.salvar_leituras(job.id, leituras)
            job.emitir("consolidando", {})
            res = analisar_leituras(leituras, pedido_d, pol, {"provedor": prov.nome, "modelo": prov.modelo, "caso_demo": caso})
            corr = sum(1 for g in res["regras"] for v in g["verificacoes"] if v.get("divergiu"))
            job.emitir("conferencia", {"correcoes_lexicas": corr, "regras": len(res["regras"])})
            job.emitir("motor", {"veredito": res["veredito"], "alternativas": len(res["quem_pode"]),
                                 "invalidos": len(res["caminhos_invalidos"])})
            h = store.auditar("analise", job.id, {"hash_entrada": res["hash_entrada"], "veredito": res["veredito"],
                                                  "faixa": res["faixa"], "indice": res["indice"], "politica": pol.nome},
                              f"{res['empresa']['razao_social']} · {res['veredito']} · {res['faixa']}")
            res["auditoria"] = {"hash": h}
            store.concluir_analise(job.id, res, time.time() - job.inicio)
            job.status = "concluida"
            job.emitir("concluido", {"veredito": res["veredito"], "faixa": res["faixa"], "indice": res["indice"]})
        except Exception as e:  # noqa: BLE001
            job.status = "erro"
            store.falhar_analise(job.id, f"{type(e).__name__}: {e}")
            job.emitir("erro", {"mensagem": f"{type(e).__name__}: {e}", "detalhe": traceback.format_exc()[-1500:]})
        finally:
            FILA.task_done()


threading.Thread(target=_trabalhador, daemon=True).start()


def _enfileirar(arquivos: list[Path], pedido: dict, origem: str, caso: str | None = None) -> str:
    aid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    prov = provedor_padrao()
    store.criar_analise(aid, origem, pedido, f"{prov.nome}:{prov.modelo}", politica_atual().nome, caso)
    job = Job(aid)
    JOBS[aid] = job
    job.emitir("na_fila", {"posicao": FILA.qsize() + 1})
    FILA.put((job, arquivos, pedido, caso))
    return aid


# ------------------------------------------------------------------------------------- rotas
@app.get("/api/saude")
def saude() -> dict:
    prov = provedor_padrao()
    disponivel = getattr(prov, "disponivel", lambda: True)()
    return {"versao": VERSAO, "provedor": prov.nome, "modelo": prov.modelo, "llm_disponivel": disponivel,
            "rotulo_ia": rotulo_ia(prov), "demonstracao": MODO_DEMO,
            "fila": FILA.qsize(), "politica": politica_dict(politica_atual())}


@app.get("/api/demo")
def demo_lista() -> list[dict]:
    spec = json.loads((CORPUS / "cenarios.json").read_text(encoding="utf-8"))
    run = _ultimo_run_llm()
    out = []
    for c in spec["casos"] + spec.get("casos_holdout", []):
        if not (CORPUS / "casos" / c["id"] / "gabarito.json").exists():
            continue
        gab = json.loads((CORPUS / "casos" / c["id"] / "gabarito.json").read_text(encoding="utf-8"))
        pre = run and (run / "casos" / f"{c['id']}.json").exists()
        out.append({"id": c["id"], "titulo": c["titulo"],
                    "categoria": "validacao_cega" if c["id"].startswith("H") else c["categoria"], "objetivo": c["objetivo"],
                    "empresa": spec["empresas"][c["empresa"]]["razao_social"], "documentos": c["documentos"],
                    "esperado": gab["esperado"], "esperado_ce": gab.get("esperado_ce"), "precalculado": bool(pre)})
    for pasta in sorted((CORPUS / "casos").glob("I[0-9]*")):  # casos do autor independente
        if not (pasta / "gabarito.json").exists():
            continue
        gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
        ped = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
        indep = sorted(AVALIACOES.glob("llm-independente*/casos"), key=lambda p: p.stat().st_mtime)
        out.append({"id": pasta.name, "titulo": gab.get("titulo", pasta.name), "categoria": "validacao_independente",
                    "objetivo": gab.get("objetivo", ""), "empresa": (ped.get("vendedor") or {}).get("razao_social", ""),
                    "documentos": [p.stem for p in sorted((pasta / "docs").glob("*.pdf")) if p.stem != "CRLV"],
                    "esperado": gab["esperado"], "esperado_ce": gab.get("esperado_ce"),
                    "precalculado": bool(indep and (indep[-1] / f"{pasta.name}.json").exists())})
    for c in spec.get("casos_atpv", []):  # lote ATPV-e: vendendo ou comprando, todos os tipos de PJ
        pasta = CORPUS / "casos" / c["id"]
        if not (pasta / "gabarito.json").exists():
            continue
        gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
        partes = [spec["empresas"][x["empresa"]]["razao_social"] for x in (c["vendedor"], c["comprador"]) if "empresa" in x]
        out.append({"id": c["id"], "titulo": c["titulo"], "categoria": c["categoria"], "objetivo": c["objetivo"],
                    "empresa": " → ".join(partes), "documentos": c["documentos"] + ["ATPV-e"], "esperado": gab["esperado"],
                    "esperado_ce": None, "esperado_lados": gab.get("esperado_lados"),
                    "precalculado": _run_atpv(c["id"]) is not None})
    for c in spec.get("casos_pf", []):  # consulta por CPF antes da ATPV-e (dono pela base veicular)
        pasta = CORPUS / "casos" / c["id"]
        if not (pasta / "gabarito.json").exists():
            continue
        gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
        dono = c["crlv_proprietario"]
        out.append({"id": c["id"], "titulo": c["titulo"], "categoria": c["categoria"], "objetivo": c["objetivo"],
                    "empresa": (spec["empresas"][dono["empresa"]]["razao_social"] if dono["tipo"] == "PJ"
                                else spec["pessoas"][dono["pessoa"]]["nome"] + " (pessoa física)"),
                    "documentos": c["documentos"], "esperado": gab["esperado"], "esperado_ce": gab.get("esperado_ce"),
                    "esperado_lados": gab.get("esperado_lados_ce") or gab.get("esperado_lados"),
                    "precalculado": _run_atpv(c["id"]) is not None})
    return out


def _run_atpv(caso: str) -> Path | None:
    """Resultado mais recente do lote ATPV-e ou da consulta por CPF (IA local; na falta, o oráculo)."""
    for padrao in (("llm-pf*/casos", "oraculo-pf*/casos") if caso.startswith("P") else ("llm-atpv*/casos", "oraculo-atpv*/casos")):
        runs = sorted((p for p in AVALIACOES.glob(padrao) if (p / f"{caso}.json").exists()), key=lambda p: p.stat().st_mtime)
        if runs:
            return runs[-1] / f"{caso}.json"
    return None


def _ultimo_run_llm() -> Path | None:
    escolhido = store.config_get("run_demo")
    if escolhido and (AVALIACOES / escolhido / "casos").exists():
        return AVALIACOES / escolhido
    def resumo(p: Path) -> dict:
        return json.loads((p / "resultado.json").read_text(encoding="utf-8"))["resumo"]

    runs = sorted([p for p in AVALIACOES.glob("llm-*") if (p / "resultado.json").exists() and resumo(p)["casos"] >= 30],
                  key=lambda p: (p / "resultado.json").stat().st_mtime)
    pol = politica_atual().nome
    mesma = [p for p in runs if (resumo(p).get("politica") or {}).get("nome") == pol]
    if mesma or runs:
        return (mesma or runs)[-1]
    oraculo = AVALIACOES / "oraculo-ce"
    return oraculo if (oraculo / "resultado.json").exists() else None


@app.get("/api/demo/{caso}/precalculado")
def demo_precalculado(caso: str) -> dict:
    if caso[:1] in ("A", "P"):
        arq = _run_atpv(caso)
        if not arq:
            raise HTTPException(404, "sem resultado pré-calculado para este caso")
        return {"run": arq.parent.parent.name, "resultado": json.loads(arq.read_text(encoding="utf-8"))}
    run = _ultimo_run_llm()
    arq = run / "casos" / f"{caso}.json" if run else None
    if (not arq or not arq.exists()) and caso[:1] in ("H", "I"):
        padrao = "llm-cega*/casos" if caso.startswith("H") else "llm-independente*/casos"
        cega = sorted(AVALIACOES.glob(padrao), key=lambda p: p.stat().st_mtime)
        if cega:
            run, arq = cega[-1].parent, cega[-1] / f"{caso}.json"
    if not arq or not arq.exists():
        raise HTTPException(404, "sem resultado pré-calculado para este caso")
    return {"run": run.name, "resultado": json.loads(arq.read_text(encoding="utf-8"))}


@app.post("/api/demo/{caso}/analisar")
def demo_analisar(caso: str, amostras: int = 1) -> dict:
    pasta = CORPUS / "casos" / caso
    if not pasta.exists():
        raise HTTPException(404, "caso não encontrado")
    pedido = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
    pedido["amostras"] = amostras
    arquivos = sorted(p for p in (pasta / "docs").iterdir() if p.suffix.lower() in EXTENSOES)
    return {"id": _enfileirar(arquivos, pedido, "demo", caso)}


@app.get("/api/demo/{caso}/arquivo/{nome}")
def demo_arquivo(caso: str, nome: str):
    arq = (CORPUS / "casos" / caso / "docs" / nome).resolve()
    if not str(arq).startswith(str((CORPUS / "casos").resolve())) or not arq.exists():
        raise HTTPException(404)
    return FileResponse(arq)


@app.post("/api/analises")
async def nova_analise(pedido: str = Form(...), arquivos: list[UploadFile] | None = File(None)) -> dict:
    """Documentos são opcionais: na consulta por CPF, o próprio dono pessoa física assinando não precisa de nenhum."""
    arquivos = arquivos or []
    if arquivos:
        _bloquear_na_demo()
    try:
        pedido_d = json.loads(pedido)
        pedido_atpv_de_json(pedido_d)  # valida
    except Exception as e:  # noqa: BLE001
        raise HTTPException(422, f"pedido inválido: {e}") from e
    tmp_id = uuid.uuid4().hex[:8]
    pasta = store.DADOS / "uploads" / tmp_id
    if arquivos:
        pasta.mkdir(parents=True, exist_ok=True)
    salvos = []
    for up in arquivos:
        nome = Path(up.filename or "documento").name
        if Path(nome).suffix.lower() not in EXTENSOES:
            raise HTTPException(422, f"tipo de arquivo não suportado: {nome}")
        destino = pasta / nome
        destino.write_bytes(await up.read())
        salvos.append(destino)
    return {"id": _enfileirar(salvos, pedido_d, "upload")}


@app.get("/api/veiculo")
def consultar_veiculo(placa: str | None = None, renavam: str | None = None) -> dict:
    """Quem é o proprietário (base veicular; no protótipo, simulada) — a tela decide o que pedir: contrato social (PJ)
    ou, se o CPF não for o do dono (PF), a procuração."""
    from . import base_veicular

    if not (placa or renavam):
        raise HTTPException(422, "informe a placa ou o RENAVAM")
    v = base_veicular.consultar(placa, renavam)
    if v is None:
        raise HTTPException(404, "veículo não encontrado na base (no protótipo, a base é simulada): anexe o CRLV")
    return v


@app.post("/api/atpv/ler")
async def ler_atpv(arquivo: UploadFile = File(...)) -> dict:
    """Lê uma ATPV-e (PDF/imagem) e devolve veículo, vendedor, comprador, valor e data para pré-preencher o pedido."""
    _bloquear_na_demo()
    from .extract import atpv_por_regex, rodar_tarefa, texto_para_llm
    from .ingest import carregar

    pasta = store.DADOS / "uploads" / ("atpv-" + uuid.uuid4().hex[:8])
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / Path(arquivo.filename or "atpv.pdf").name
    destino.write_bytes(await arquivo.read())
    doc = carregar(destino)
    a = atpv_por_regex(doc)
    metodo = "regex"
    if a is None:
        prov = provedor_padrao()
        if not getattr(prov, "disponivel", lambda: True)():
            raise HTTPException(422, "Não reconheci o layout desta ATPV-e e a IA local está desligada: preencha o pedido à mão.")
        try:
            a, _, _ = rodar_tarefa(prov, texto_para_llm(doc), "atpv")
        except Exception as e:  # noqa: BLE001
            raise HTTPException(422, f"Não foi possível ler a ATPV-e: {type(e).__name__}: {e}") from e
        metodo = "llm"
    return {"metodo": metodo, "atpv": a.model_dump()}


@app.get("/api/analises")
def analises() -> list[dict]:
    return store.listar_analises()


@app.get("/api/analises/{aid}")
def analise(aid: str) -> dict:
    a = store.obter_analise(aid)
    if not a:
        raise HTTPException(404)
    job = JOBS.get(aid)
    a["eventos"] = job.eventos if job else []
    return a


@app.get("/api/analises/{aid}/eventos")
async def eventos(aid: str):
    async def gerar():
        enviado = 0
        while True:
            job = JOBS.get(aid)
            if job is None:
                a = store.obter_analise(aid)
                yield {"event": "fim", "data": json.dumps({"status": a["status"] if a else "desconhecido"})}
                return
            while enviado < len(job.eventos):
                yield {"event": "progresso", "data": json.dumps(job.eventos[enviado], ensure_ascii=False, default=str)}
                enviado += 1
            if job.status in ("concluida", "erro") and enviado >= len(job.eventos):
                yield {"event": "fim", "data": json.dumps({"status": job.status})}
                return
            await asyncio.sleep(0.25)

    return EventSourceResponse(gerar())


@app.post("/api/analises/{aid}/reprocessar")
def reprocessar(aid: str) -> dict:
    """Reaplica o motor com a política atual sobre as leituras já feitas (instantâneo, sem LLM)."""
    a = store.obter_analise(aid)
    leituras = store.carregar_leituras(aid)
    if not a or leituras is None:
        raise HTTPException(404, "análise sem leituras salvas")
    pol = politica_atual()
    res = analisar_leituras(leituras, a["pedido"], pol, (a["resultado"] or {}).get("meta"))
    res["auditoria"] = {"hash": store.auditar("reprocessamento", aid, {"politica": pol.nome, "faixa": res["faixa"],
                                                                         "indice": res["indice"]}, f"reprocessado · {res['faixa']}")}
    store.concluir_analise(aid, res, a.get("duracao_s") or 0)
    return res


@app.post("/api/analises/{aid}/simular")
def simular(aid: str, corpo: dict) -> dict:
    """'E se…?': reaplica o motor com outros assinantes/valor/data sobre as leituras salvas (instantâneo, não grava)."""
    a = store.obter_analise(aid)
    leituras = store.carregar_leituras(aid)
    if not a or leituras is None:
        raise HTTPException(404, "análise sem leituras salvas")
    pedido = json.loads(json.dumps(a["pedido"]))
    if pedido.get("cpf") and pedido.get("papel") and (a["resultado"] or {}).get("pedido_atpv"):
        # consulta por CPF: simula sobre o pedido já resolvido (dono da base veicular, lado consultado)
        pedido = json.loads(json.dumps(a["resultado"]["pedido_atpv"]))
        corpo = {"lado": pedido.get("alvo") or "vendedor", **corpo}
    pedido.update({k: v for k, v in corpo.items() if k in ("valor", "data_venda")})
    if "assinantes" in corpo:  # por lado (padrão: vendedor; formato antigo continua aceito)
        lado = corpo.get("lado", "vendedor")
        parte = pedido.get(lado) if isinstance(pedido.get(lado), dict) else {}
        pedido[lado] = {**parte, "assinantes": corpo["assinantes"]}
        if lado == "vendedor":
            pedido.pop("assinantes", None)
    res = analisar_leituras(leituras, pedido, politica_atual(), (a["resultado"] or {}).get("meta"))
    campos = ("veredito", "faixa", "indice", "resumo", "assinantes", "quem_pode", "faltantes", "caminho_escolhido",
              "comprovacao_poderes", "motivos_faixa", "achados", "caminhos_invalidos", "lado")
    out = {k: res.get(k) for k in campos}
    out["geral"] = res.get("geral")
    out["lados"] = {k: {c: v.get(c) for c in campos} for k, v in (res.get("lados") or {}).items()}
    return out


@app.post("/api/analises/{aid}/revisao")
def revisao(aid: str, corpo: dict) -> dict:
    _bloquear_na_demo()
    if corpo.get("decisao") not in ("aprovar", "recusar"):
        raise HTTPException(422, "decisao deve ser 'aprovar' ou 'recusar'")
    if not store.obter_analise(aid):
        raise HTTPException(404)
    return store.registrar_revisao(aid, corpo.get("revisor") or "servidor", corpo["decisao"], corpo.get("justificativa") or "")


@app.get("/api/analises/{aid}/parecer.html", response_class=HTMLResponse)
def parecer_html(aid: str):
    a = store.obter_analise(aid)
    if not a or not a["resultado"]:
        raise HTTPException(404)
    return html_parecer(a["resultado"], a["resultado"].get("auditoria"))


@app.get("/api/analises/{aid}/parecer.pdf")
def parecer_pdf(aid: str):
    a = store.obter_analise(aid)
    if not a or not a["resultado"]:
        raise HTTPException(404)
    return Response(pdf_parecer(a["resultado"], a["resultado"].get("auditoria")), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="parecer-{aid}.pdf"'})


@app.post("/api/parecer")
def parecer_de_resultado(corpo: dict, formato: str = "pdf"):
    """Gera o parecer de um resultado já calculado (ex.: pré-calculado da demonstração)."""
    if formato == "html":
        return HTMLResponse(html_parecer(corpo))
    return Response(pdf_parecer(corpo), media_type="application/pdf")


@app.get("/api/politica")
def get_politica() -> dict:
    return politica_dict(politica_atual())


@app.put("/api/politica")
def put_politica(corpo: dict) -> dict:
    _bloquear_na_demo()
    perfil = corpo.get("perfil", "ce")
    base = politica_dict(Politica.por_nome(perfil), perfil)
    novo = {**base, **{k: v for k, v in corpo.items() if k in base and k not in ("nome", "uf")}}
    if not (0 <= novo["limiar_recusa"] < novo["limiar_aceite"] <= 100):
        raise HTTPException(422, "limiares inválidos: 0 ≤ recusa < aceite ≤ 100")
    store.config_set("politica", novo)
    store.auditar("politica", None, novo, f"política {novo['perfil']}: aceite≥{novo['limiar_aceite']}, recusa≤{novo['limiar_recusa']}")
    return politica_dict(politica_atual())


@app.get("/api/calibracao")
def calibracao(alfa: float = 0.05) -> dict:
    run = _ultimo_run_llm()
    itens = []
    if run:
        dados = json.loads((run / "resultado.json").read_text(encoding="utf-8"))
        for l in dados["linhas"]:
            forcado = l.get("forcado")
            if forcado is None:
                forcado = l["faixa"] == "AMARELO" and any(m.startswith(("alerta", "indeterminado")) or "ancorada" in m
                                                         for m in l.get("motivos_faixa", []))
            itens.append({"caso": l["caso"], "titulo": l["titulo"], "categoria": l["categoria"], "indice": l["indice"],
                          "previsto": l["previsto"], "esperado": l["esperado"], "faixa": l["faixa"], "forcado": forcado,
                          "fonte": "corpus"})
    itens += store.revisoes_rotuladas()
    pol = politica_atual()
    limiares_run = (dados["resumo"].get("politica") or {}) if run else {}
    return {"run": run.name if run else None, "itens": itens, "alfa": alfa,
            "limiares_da_avaliacao": {"limiar_aceite": limiares_run.get("limiar_aceite"),
                                      "limiar_recusa": limiares_run.get("limiar_recusa")},
            "sugestao": sugerir_limiares(itens, alfa) if itens else None,
            "sugestao_conservadora": sugerir_limiares(itens, alfa, usar_limite_superior=True) if itens else None,
            "atual": {"limiar_aceite": pol.limiar_aceite, "limiar_recusa": pol.limiar_recusa}}


@app.get("/api/auditoria")
def auditoria() -> dict:
    return {"cadeia": store.verificar_cadeia(), "registros": store.listar_auditoria()}


@app.get("/api/avaliacoes")
def avaliacoes() -> list[dict]:
    out = []
    for p in sorted(AVALIACOES.glob("*/resultado.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        r = json.loads(p.read_text(encoding="utf-8"))
        out.append({"run": p.parent.name, **r["resumo"]})
    return out


# ------------------------------------------------------------------------------- interface web
if WEB.exists():
    app.mount("/assets", StaticFiles(directory=WEB / "assets"), name="assets")


@app.get("/{caminho:path}", include_in_schema=False)
def spa(caminho: str):
    alvo = WEB / caminho
    if caminho and alvo.is_file():
        return FileResponse(alvo)
    indice = WEB / "index.html"
    if indice.exists():
        return FileResponse(indice)
    return JSONResponse({"mensagem": "interface web não compilada — rode `pnpm build` em web/", "api": "/docs"})
