"""Avaliação contra o gabarito do corpus.

    uv run python -m outorga.avaliacao oraculo            # motor com leitura perfeita (gabarito)
    uv run python -m outorga.avaliacao llm --casos C01 C13 # leitura pelo LLM configurado

Métricas:
- veredito correto; faixa dentro das aceitáveis; "quem pode assinar" igual ao gabarito;
- ERRO PERIGOSO: faixa VERDE (aceite automático) quando o gabarito diz que não pode;
- ERRO CARO: faixa VERMELHA (recusa automática) quando o gabarito diz que pode;
- cobertura: % de casos decididos automaticamente (VERDE/VERMELHO).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from .engine import Politica
from .ids import so_digitos
from .pipeline import analisar_leituras

RAIZ = Path(__file__).resolve().parents[2]
CORPUS = RAIZ / "corpus"
RESULTADOS = RAIZ / "avaliacoes"


def esperado_para(gab: dict, politica: Politica) -> dict:
    if politica.uf == "CE" and gab.get("esperado_ce"):
        return gab["esperado_ce"]
    return gab["esperado"]


def comparar(res: dict, gab: dict, politica: Politica | None = None) -> dict:
    esp = esperado_para(gab, politica or Politica())
    ok_v = res["veredito"] == esp["veredito"]
    ok_f = res["faixa"] in esp["faixas_aceitaveis"]
    def _conj(r: dict, e: dict) -> bool | None:
        if e.get("conjuntos_minimos_cpf") is None:
            return None
        esperado = {frozenset(so_digitos(c) for c in s) for s in e["conjuntos_minimos_cpf"]}
        obtido = {frozenset(so_digitos(r["pessoas"].get(p["chave"], {}).get("cpf") or p["chave"]) for p in a["pessoas"])
                  for a in r["quem_pode"]}
        return esperado == obtido

    conj_ok = _conj(res, esp)
    lados_ok = {}
    esp_lados = (gab.get("esperado_lados_ce") if (politica or Politica()).uf == "CE" and gab.get("esperado_lados_ce")
                 else gab.get("esperado_lados")) or {}
    for lado, e in esp_lados.items():  # lote ATPV-e / consulta por CPF: confere cada lado verificado
        r = (res.get("lados") or {}).get(lado)
        v_ok = r is not None and r["veredito"] == e["veredito"]
        f_ok = r is not None and r["faixa"] in e["faixas_aceitaveis"]
        c = _conj(r, e) if r is not None else False
        lados_ok[lado] = v_ok and f_ok and c is not False
        ok_v, ok_f = ok_v and v_ok, ok_f and f_ok
        conj_ok = c if conj_ok is None else (conj_ok and c is not False)
    if esp_lados:
        ok_v = ok_v and not (set(res.get("lados") or {}) - set(esp_lados))  # lado a mais = leitura errada
    perigoso = res["faixa"] == "VERDE" and esp["veredito"] != "PODE"
    caro = res["faixa"] == "VERMELHO" and esp["veredito"] == "PODE"
    return {"veredito_ok": ok_v, "faixa_ok": ok_f, "conjuntos_ok": conj_ok, "erro_perigoso": perigoso, "erro_caro": caro,
            **({"lados_ok": lados_ok} if lados_ok else {})}


def casos_do_conjunto(conjunto: str) -> list[str]:
    spec = json.loads((CORPUS / "cenarios.json").read_text(encoding="utf-8"))
    independentes = [{"id": p.name} for p in sorted((CORPUS / "casos").glob("I[0-9]*")) if (p / "gabarito.json").exists()]
    grupos = {"principal": spec["casos"], "cega": spec.get("casos_holdout", []), "independente": independentes,
              "atpv": spec.get("casos_atpv", []), "pf": spec.get("casos_pf", []),
              "todos": spec["casos"] + spec.get("casos_holdout", []) + independentes + spec.get("casos_atpv", [])
              + spec.get("casos_pf", []),
              # comparação de modelos: os lotes em que o motor menos aprendeu com as leituras do Qwen3.8-27B
              "triagem": spec.get("casos_holdout", []) + independentes + spec.get("casos_pf", [])}
    return [c["id"] for c in grupos[conjunto]]


def rodar(modo: str, casos: list[str] | None, politica: Politica, provedor=None, amostras: int = 1, saida: Path | None = None,
          verbose: bool = True, conjunto: str = "principal") -> dict:
    ids = casos or casos_do_conjunto(conjunto)
    linhas = []
    t0 = time.time()
    for cid in ids:
        pasta = CORPUS / "casos" / cid
        gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
        pedido = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
        t = time.time()
        meta = {"provedor": provedor.nome, "modelo": provedor.modelo} if provedor is not None else {"provedor": "gabarito"}
        try:
            if modo == "oraculo":
                sys.path.insert(0, str(CORPUS))
                from gold import leituras_gold  # noqa: E402
                leituras = leituras_gold(cid)
            else:
                from .extract import ler_pasta
                leituras = ler_pasta(pasta / "docs", provedor, amostras=amostras)
            res = analisar_leituras(leituras, pedido, politica, meta)
        except Exception as e:  # noqa: BLE001 — leitura que falhou (ex.: JSON inválido do modelo) conta como erro do caso
            res = {"veredito": "ERRO", "faixa": "AMARELO", "indice": 50.0, "confianca": 0.0, "resumo": f"{type(e).__name__}: {e}",
                   "motivos_faixa": ["erro na leitura"], "quem_pode": [], "pessoas": {}, "lados": {}, "erro": True}
        cmp = comparar(res, gab, politica)
        esp = esperado_para(gab, politica)
        linha = {"caso": cid, "titulo": gab["titulo"], "categoria": gab["categoria"], "esperado": esp["veredito"],
                 "faixas_aceitaveis": esp["faixas_aceitaveis"], "previsto": res["veredito"], "faixa": res["faixa"],
                 "indice": res["indice"], "confianca": res["confianca"], "segundos": round(time.time() - t, 1),
                 "resumo": res["resumo"], "motivos_faixa": res["motivos_faixa"],
                 "lados": {k: {"veredito": r["veredito"], "faixa": r["faixa"], "indice": r["indice"]}
                           for k, r in (res.get("lados") or {}).items()},
                 "forcado": res["faixa"] == "AMARELO" and any(m.startswith(("alerta", "indeterminado")) or "ancorada" in m
                                                              for m in res["motivos_faixa"]), **cmp}
        linhas.append(linha)
        if saida:
            (saida / "casos").mkdir(parents=True, exist_ok=True)
            (saida / "casos" / f"{cid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        if verbose:
            marca = "✓" if cmp["veredito_ok"] and cmp["faixa_ok"] and cmp["conjuntos_ok"] is not False else "✗"
            alerta = " ⚠ PERIGOSO" if cmp["erro_perigoso"] else (" ⚠ caro" if cmp["erro_caro"] else "")
            print(f"{marca} {cid} {gab['titulo'][:58]:58} esp={linha['esperado']:13} prev={linha['previsto']:13} "
                  f"{linha['faixa']:8} idx={linha['indice']:5.1f} quem={'ok' if cmp['conjuntos_ok'] else ('—' if cmp['conjuntos_ok'] is None else 'X')}"
                  f" {linha['segundos']:5.1f}s{alerta}", flush=True)
    n = len(linhas)
    auto = [l for l in linhas if l["faixa"] in ("VERDE", "VERMELHO")]
    resumo = {
        "modo": modo, "conjunto": conjunto, "casos": n, "duracao_s": round(time.time() - t0, 1), "data": datetime.now().isoformat(timespec="seconds"),
        "veredito_correto": sum(l["veredito_ok"] for l in linhas),
        "faixa_aceitavel": sum(l["faixa_ok"] for l in linhas),
        "quem_pode_correto": sum(1 for l in linhas if l["conjuntos_ok"]),
        "quem_pode_avaliados": sum(1 for l in linhas if l["conjuntos_ok"] is not None),
        "erros_perigosos": sum(l["erro_perigoso"] for l in linhas),
        "erros_caros": sum(l["erro_caro"] for l in linhas),
        "cobertura_automatica": round(len(auto) / n, 3) if n else 0,
        "acerto_na_faixa_automatica": round(sum(1 for l in auto if l["veredito_ok"]) / len(auto), 3) if auto else None,
        "politica": {"nome": politica.nome, "limiar_aceite": politica.limiar_aceite, "limiar_recusa": politica.limiar_recusa},
    }
    out = {"resumo": resumo, "linhas": linhas}
    if saida:
        saida.mkdir(parents=True, exist_ok=True)
        (saida / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    if verbose:
        r = resumo
        print(f"\nveredito {r['veredito_correto']}/{n} · faixa aceitável {r['faixa_aceitavel']}/{n} · quem pode "
              f"{r['quem_pode_correto']}/{r['quem_pode_avaliados']} · perigosos {r['erros_perigosos']} · caros {r['erros_caros']} · "
              f"automático {r['cobertura_automatica']:.0%} · {r['duracao_s']}s")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["oraculo", "llm"])
    ap.add_argument("--casos", nargs="*")
    ap.add_argument("--amostras", type=int, default=1)
    ap.add_argument("--provedor", default=None, help="llamacpp | anthropic | openai (padrão: config)")
    ap.add_argument("--saida", default=None)
    ap.add_argument("--politica", default="ce", help="ce (DETRAN-CE, padrão) | generica (só Código Civil)")
    ap.add_argument("--conjunto", default="principal", choices=["principal", "cega", "independente", "atpv", "pf", "todos", "triagem"])
    a = ap.parse_args()
    prov = None
    if a.modo == "llm":
        from .llm import provedor_padrao
        prov = provedor_padrao(a.provedor)
    saida = Path(a.saida) if a.saida else RESULTADOS / f"{a.modo}-{datetime.now():%Y%m%d-%H%M%S}"
    rodar(a.modo, a.casos, Politica.por_nome(a.politica), prov, a.amostras, saida, conjunto=a.conjunto)


if __name__ == "__main__":
    main()
