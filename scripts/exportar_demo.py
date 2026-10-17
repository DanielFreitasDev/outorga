"""Exporta resultados reais de uma avaliação para a página de demonstração (JSON compacto embutido no HTML).

    uv run python scripts/exportar_demo.py avaliacoes/llm-completa1 saida.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTAQUES = ["C13", "C14", "C15", "C01", "C02", "C03", "C16", "C18", "C20", "C21", "C25", "C23", "C17", "C29", "C33", "C26",
             "C07", "C11"]


def compacto(r: dict, gab: dict) -> dict:
    def pessoas(a):
        return [p["nome"] for p in a["pessoas"]]

    achados = [a for a in ((r.get("caminho_escolhido") or {}).get("achados") or []) + r["achados"]
               if a["severidade"] in ("bloqueio", "alerta", "atencao", "ok")]
    vistos, ach = set(), []
    ordem = {"bloqueio": 0, "alerta": 1, "atencao": 2, "ok": 3}
    for a in sorted(achados, key=lambda a: ordem[a["severidade"]]):
        k = (a["codigo"], a["detalhe"])
        if k in vistos:
            continue
        vistos.add(k)
        f = next((f for f in a.get("fontes") or [] if f and f.get("trecho")), None)
        ach.append({"sev": a["severidade"], "titulo": a["titulo"], "detalhe": a["detalhe"], "fund": a.get("fundamento") or [],
                    "cit": (f["trecho"][:240] if f else None), "doc": (f["doc_titulo"] if f else None)})
    for b in r["caminhos_invalidos"]:
        motivos = [a["titulo"] for a in b["achados"] if a["severidade"] == "bloqueio"]
        ach.insert(0, {"sev": "bloqueio", "titulo": f"{' e '.join(pessoas(b))}: caminho inválido",
                       "detalhe": f"{b['descricao']}: {'; '.join(dict.fromkeys(motivos))}.", "fund": [], "cit": None, "doc": None})
    c = r["comprovacao_poderes"]
    regras = [{"escopo": g["escopo"], "aplicavel": g["aplicavel"], "motivo": g["motivo"], "decisiva": g["decisiva"],
               "trecho": (g["fonte"] or {}).get("trecho", "")[:220] if g.get("fonte") else "",
               "correcoes": [f"a IA leu “{v['valor_llm']}” → o texto indica “{v['valor_lexico']}”" for v in g["verificacoes"]
                             if v.get("divergiu")]}
              for g in r["regras"]]
    esp = gab.get("esperado_ce") or gab["esperado"]
    return {
        "id": gab["caso"], "titulo": gab["titulo"], "categoria": gab["categoria"], "objetivo": gab["objetivo"],
        "esperado": esp["veredito"], "faixas_esperadas": esp["faixas_aceitaveis"],
        "empresa": r["empresa"]["razao_social"], "cnpj": r["empresa"]["cnpj"], "tipo": r["empresa"]["tipo"],
        "veiculo": r["pedido"]["veiculo"]["descricao"], "placa": r["pedido"]["veiculo"]["placa"],
        "data": r["pedido"]["data_venda"], "valor": r["pedido"]["valor"],
        "assinantes": [a["nome"] for a in r["assinantes"]],
        "veredito": r["veredito"], "faixa": r["faixa"], "indice": r["indice"], "confianca": r["confianca"],
        "resumo": r["resumo"], "motivos": r["motivos_faixa"],
        "quem_pode": [{"pessoas": pessoas(a), "via": a["via"], "descricao": a["descricao"], "sev": a["severidade"]}
                      for a in r["quem_pode"]],
        "faltantes": [{"faltam": f["faltam_nomes"], "descricao": f["descricao"]} for f in r["faltantes"][:3]],
        "c7": {"status": c["status"], "outorgante": f"{c['outorgante']['nome']} — CNPJ {c['outorgante']['cnpj']}",
               "outorgado": [f"{o['nome']} · {o['qualidade']}" for o in c["outorgado"]],
               "poderes": c["poderes_conferidos"], "prazo": c["prazo_validade"], "revogacao": c["revogacao"]},
        "achados": ach[:9], "regras": regras, "grafo": r["grafo"],
        "documentos": [{"titulo": d["titulo"], "metodo": d["metodo"], "ocr": d["ocr_confianca"], "paginas": len(d["paginas"]),
                        "segundos": round(sum((t or {}).get("segundos") or 0 for t in (d.get("leitura") or {}).get("tarefas", {}).values()), 1)}
                       for d in r["documentos"]],
    }


DESTAQUES_ATPV = ["A04", "A10", "A09", "A11"]  # um lado só (o compacto mostra o lado verificado)


def _lote_pf(run: Path, r: dict) -> dict:
    spec = json.loads((RAIZ / "corpus" / "cenarios.json").read_text(encoding="utf-8"))
    por_id = {c["id"]: c for c in spec.get("casos_pf", [])}
    linhas = []
    for l in r["linhas"]:
        c = por_id[l["caso"]]
        res = json.loads((run / "casos" / f"{l['caso']}.json").read_text(encoding="utf-8"))
        lado = next(iter(res.get("lados") or {}), None)
        rr = (res.get("lados") or {}).get(lado) or res
        dono = c["crlv_proprietario"]
        dono_txt = (spec["empresas"][dono["empresa"]]["razao_social"] if dono["tipo"] == "PJ"
                    else spec["pessoas"][dono["pessoa"]]["nome"] + " (pessoa física)")
        cp = c.get("comprador")
        comprador_txt = (None if not cp else spec["empresas"][cp["empresa"]]["razao_social"] if "empresa" in cp
                         else spec["pessoas"][cp["pessoa"]]["nome"] + " (pessoa física)")
        linhas.append({"id": l["caso"], "titulo": l["titulo"], "papel": c["papel"], "dono": dono_txt, "comprador": comprador_txt,
                       "quem": spec["pessoas"][c["assinante"]]["nome"], "documentos": c["documentos"],
                       "esperado": l["esperado"], "previsto": l["previsto"], "faixa": l["faixa"], "indice": l["indice"],
                       "resumo": rr["resumo"], "pendencias": [pd["tipo"] for pd in res.get("pendencias") or []],
                       "ok": bool(l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False)})
    return {"resumo": r["resumo"], "linhas": linhas}


def _lote_atpv(run: Path, r: dict, nome: str) -> dict:
    spec = json.loads((RAIZ / "corpus" / "cenarios.json").read_text(encoding="utf-8"))
    por_id = {c["id"]: c for c in spec.get("casos_atpv", [])}

    def parte(x: dict) -> str:
        return (spec["empresas"][x["empresa"]]["razao_social"] if "empresa" in x
                else spec["pessoas"][x["pessoa"]]["nome"] + " (pessoa física)")

    linhas = []
    for l in r["linhas"]:
        c = por_id[l["caso"]]
        res = json.loads((run / "casos" / f"{l['caso']}.json").read_text(encoding="utf-8"))
        lados = {}
        for k, rr in (res.get("lados") or {}).items():
            lados[k] = {"empresa": rr["empresa"]["razao_social"], "tipo": rr["empresa"]["tipo"], "veredito": rr["veredito"],
                        "faixa": rr["faixa"], "indice": rr["indice"], "resumo": rr["resumo"],
                        "assinantes": [a["nome"] for a in rr["assinantes"]],
                        "quem_pode": [" + ".join(p["nome"] for p in a["pessoas"]) for a in rr["quem_pode"]]}
        linhas.append({"id": l["caso"], "titulo": l["titulo"], "categoria": l["categoria"], "objetivo": c["objetivo"],
                       "vendedor": parte(c["vendedor"]), "comprador": parte(c["comprador"]), "esperado": l["esperado"],
                       "previsto": l["previsto"], "faixa": l["faixa"], "indice": l["indice"], "lados": lados,
                       "ok": bool(l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False)})
    casos = {}
    for cid in DESTAQUES_ATPV:
        arq = run / "casos" / f"{cid}.json"
        if arq.exists():
            gab = json.loads((RAIZ / "corpus" / "casos" / cid / "gabarito.json").read_text(encoding="utf-8"))
            casos[cid] = compacto(json.loads(arq.read_text(encoding="utf-8")), gab)
    return {"run": nome, "resumo": r["resumo"], "linhas": linhas, "casos": casos}


def main() -> None:
    run = Path(sys.argv[1])
    saida = Path(sys.argv[2])
    extras = {}
    atpv = None
    for arg in sys.argv[3:]:  # nome=caminho (ex.: primeira=avaliacoes/llm-completa1 cega=avaliacoes/llm-cega-ce)
        nome, caminho = arg.split("=", 1)
        r = json.loads((Path(caminho) / "resultado.json").read_text(encoding="utf-8"))
        if nome == "atpv":  # lote ATPV-e: por lado, e alguns casos de um lado só para a demonstração
            atpv = _lote_atpv(Path(caminho), r, nome)
            continue
        if nome == "pf":  # consulta por CPF antes da ATPV-e
            extras["pf"] = _lote_pf(Path(caminho), r)
            continue
        extras[nome] = {"resumo": r["resumo"],
                        "linhas": [{"id": l["caso"], "titulo": l["titulo"], "esperado": l["esperado"], "previsto": l["previsto"],
                                    "faixa": l["faixa"], "ok": bool(l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False)}
                                   for l in r["linhas"]]}
    res = json.loads((run / "resultado.json").read_text(encoding="utf-8"))
    casos = {}
    for cid in DESTAQUES:
        arq = run / "casos" / f"{cid}.json"
        if arq.exists():
            gab = json.loads((RAIZ / "corpus" / "casos" / cid / "gabarito.json").read_text(encoding="utf-8"))
            casos[cid] = compacto(json.loads(arq.read_text(encoding="utf-8")), gab)
    pontos = [{"id": l["caso"], "titulo": l["titulo"], "categoria": l["categoria"], "indice": l["indice"], "previsto": l["previsto"],
               "esperado": l["esperado"], "faixa": l["faixa"], "faixas_ok": l["faixas_aceitaveis"]} for l in res["linhas"]]
    oraculo = RAIZ / "avaliacoes" / "oraculo-ce" / "resultado.json"
    dados = {"resumo": res["resumo"], "casos": casos, "pontos": pontos,
             "oraculo": json.loads(oraculo.read_text(encoding="utf-8"))["resumo"] if oraculo.exists() else None, **extras}
    if atpv:
        dados["atpv"] = atpv
        casos.update(atpv.pop("casos"))
    saida.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(casos)} casos, {len(pontos)} pontos, {saida.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
