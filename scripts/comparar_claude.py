"""Compara modelos Claude, e os níveis de esforço de cada um, na mesma avaliação dos outros testes (docs/MODELOS.md).

Cada configuração `modelo:esforço` roda num processo próprio, com cache de leituras próprio
(avaliacoes/claude/<config>/t<N>/cache). Primeiro lê em paralelo os documentos únicos de todos os casos, depois roda a
avaliação, que encontra tudo no cache. Mede acerto, tempo por caso, tokens e custo em dólares pela tabela oficial.
O fallback do servidor fica desligado, para medir só o modelo pedido.

    uv run python scripts/comparar_claude.py                        # matriz padrão, conjunto "todos" (85 casos)
    uv run python scripts/comparar_claude.py --configs claude-haiku-5-5:low claude-opus-5-5:medium
    uv run python scripts/comparar_claude.py --tabela               # só monta a tabela com o que já rodou
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "avaliacoes" / "claude"

# US$ por milhão de tokens, tabela oficial de 17/10/2026 (platform.claude.com/docs/en/about-claude/pricing):
# entrada, escrita de cache (5 min), leitura de cache, saída. A saída inclui o pensamento.
PRECOS = {
    "claude-opus-5-5": (4.0, 5.0, 0.20, 20.0),
    "claude-opus-5": (5.0, 6.25, 0.50, 25.0),
    "claude-sonnet-5-5": (2.0, 2.5, 0.10, 10.0),
    "claude-sonnet-5": (2.0, 2.5, 0.20, 10.0),
    "claude-haiku-5-5": (0.10, 0.125, 0.01, 0.50),  # prompts de até 100 mil tokens (os nossos têm ~5 mil)
    "claude-haiku-4-5": (1.0, 1.25, 0.10, 5.0),
}
# os três modelos atuais em todos os esforços (intercalados, para usar os limites de taxa de cada modelo ao mesmo tempo)
# e a geração anterior de cada linha no esforço padrão, como referência
MATRIZ = ([f"{m}:{e}" for e in ("low", "medium", "high", "xhigh", "max")
           for m in ("claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5")]
          + ["claude-opus-5:high", "claude-sonnet-5:high", "claude-haiku-4-5:padrao"])


def custo(meta: dict) -> float:
    p = PRECOS[meta["modelo_pedido"]]
    return ((meta.get("tokens_entrada") or 0) * p[0] + (meta.get("tokens_cache_escrita") or 0) * p[1]
            + (meta.get("tokens_cache") or 0) * p[2] + (meta.get("tokens_saida") or 0) * p[3]) / 1e6


def pasta(config: str, trial: int) -> Path:
    return SAIDA / config.replace(":", "-") / f"t{trial}"


def metas(cache: Path) -> list[dict]:
    out = []
    for c in cache.rglob("*.json"):
        try:
            out.append(json.loads(c.read_text(encoding="utf-8"))["meta"])
        except (OSError, ValueError, KeyError):  # arquivo sendo escrito por outro processo
            pass
    return out


def gasto() -> float:
    return sum(custo(m) for m in metas(SAIDA) if m.get("modelo_pedido") in PRECOS)


def rodar_um(config: str, conjunto: str, casos: list[str] | None, trial: int, workers: int) -> None:
    modelo, _, esforco = config.partition(":")
    dest = pasta(config, trial)
    dest.mkdir(parents=True, exist_ok=True)
    os.environ.update({"OUTORGA_CACHE": str(dest / "cache"), "OUTORGA_CLAUDE_FALLBACK": "0"})
    sys.path.insert(0, str(RAIZ / "src"))
    from outorga.avaliacao import CORPUS, casos_do_conjunto, rodar
    from outorga.engine import Politica
    from outorga.extract import EXTENSOES, ler_documento, texto_para_llm
    from outorga.ingest import carregar
    from outorga.llm_claude import Claude

    prov = Claude(modelo, esforco or "padrao")
    ids = casos or casos_do_conjunto(conjunto)
    docs_por_caso: dict[str, list[str]] = {}
    unicos: dict[str, object] = {}
    for cid in ids:
        hs = []
        for arq in sorted(p for p in (CORPUS / "casos" / cid / "docs").iterdir() if p.suffix.lower() in EXTENSOES):
            doc = carregar(arq)
            h = hashlib.sha256(texto_para_llm(doc).encode()).hexdigest()
            unicos.setdefault(h, doc)
            hs.append(h)
        docs_por_caso[cid] = hs

    tempos: dict[str, float] = {}
    erros: dict[str, str] = {}

    def ler(h: str) -> None:
        t = time.time()
        try:
            ler_documento(unicos[h], prov)
        except Exception as e:  # noqa: BLE001 — a avaliação tenta de novo e conta o erro no caso
            erros[h] = f"{type(e).__name__}: {e}"[:300]
        tempos[h] = time.time() - t

    inicio = datetime.now()
    print(f"{config}: {len(ids)} casos, {len(unicos)} documentos únicos, {workers} leituras simultâneas", flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(ler, unicos))
    print(f"pré-leitura: {(datetime.now() - inicio).total_seconds():.0f}s, {len(erros)} erro(s)", flush=True)
    r = rodar("llm", ids, Politica.por_nome("ce"), prov, 1, dest / conjunto, conjunto=conjunto)
    fim = datetime.now()

    ms = metas(dest / "cache")
    lat = [sum(tempos.get(h, 0.0) for h in hs) for hs in docs_por_caso.values()]
    soma = lambda k: sum(m.get(k) or 0 for m in ms)  # noqa: E731
    total = sum(custo(m) for m in ms)
    resumo = {
        "config": config, "modelo": modelo, "esforco": prov.esforco or "padrão do modelo", "conjunto": conjunto,
        "trial": trial, "inicio": inicio.isoformat(timespec="seconds"), "fim": fim.isoformat(timespec="seconds"),
        "duracao_min": round((fim - inicio).total_seconds() / 60, 1), "casos": len(ids),
        "documentos_unicos": len(unicos), "chamadas": len(ms),
        "tokens_entrada": soma("tokens_entrada"), "tokens_cache_escrita": soma("tokens_cache_escrita"),
        "tokens_cache_leitura": soma("tokens_cache"), "tokens_saida": soma("tokens_saida"),
        "saida_por_chamada": round(soma("tokens_saida") / len(ms)) if ms else None,
        "segundos_por_chamada": round(statistics.mean(m["segundos"] for m in ms), 1) if ms else None,
        "segundos_por_caso": round(statistics.mean(lat), 1) if lat else None,
        "segundos_por_caso_p90": round(statistics.quantiles(lat, n=10)[-1], 1) if len(lat) > 1 else None,
        "custo_usd": round(total, 4), "custo_por_caso_usd": round(total / len(ids), 5) if ids else None,
        "erros_de_leitura": sum(1 for x in r["linhas"] if x["previsto"] == "ERRO"),
        "recusas": sum("recusou" in e for e in erros.values()),
        "erros_pre_leitura": sorted(set(erros.values()))[:10],
        "resultado": r["resumo"],
    }
    (dest / f"resumo-{conjunto}.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    print("RESUMO " + json.dumps({k: resumo[k] for k in ("config", "custo_usd", "segundos_por_caso", "erros_de_leitura")},
                                 ensure_ascii=False), flush=True)


class _SoCache:
    """Mesma identidade (e chave de cache) do provedor Claude da rodada, mas só lê o cache: não chama a API."""

    def __init__(self, modelo: str, esforco: str):
        from outorga.llm_claude import ESFORCOS, SEM_ESFORCO

        self.nome, self.modelo = "anthropic", modelo
        esf = esforco if esforco in ESFORCOS and not modelo.startswith(SEM_ESFORCO) else None
        self.variante = f"esforco={esf}" if esf else None

    def json(self, *a, **k):
        from outorga.llm import ErroLLM

        raise ErroLLM("leitura fora do cache (a reavaliação não chama a API)")


def reavaliar(conjunto: str, trial: int) -> None:
    """Roda de novo a avaliação de cada configuração com as leituras guardadas e o motor atual (custo zero)."""
    sys.path.insert(0, str(RAIZ / "src"))
    from outorga import extract
    from outorga.avaliacao import rodar
    from outorga.engine import Politica

    for f in sorted(SAIDA.glob(f"*/t{trial}/resumo-{conjunto}.json")):
        s = json.loads(f.read_text(encoding="utf-8"))
        modelo, _, esforco = s["config"].partition(":")
        extract.CACHE_DIR = f.parent / "cache"
        r = rodar("llm", None, Politica.por_nome("ce"), _SoCache(modelo, esforco), 1, f.parent / f"{conjunto}-motor-atual",
                  verbose=False, conjunto=conjunto)["resumo"]
        a = s["resultado"]
        print(f"{s['config']:26} veredito {a['veredito_correto']}→{r['veredito_correto']}/{r['casos']} · faixa "
              f"{a['faixa_aceitavel']}→{r['faixa_aceitavel']} · perigosos {a['erros_perigosos']}→{r['erros_perigosos']} · "
              f"caros {a['erros_caros']}→{r['erros_caros']} · automático {a['cobertura_automatica']:.0%}→"
              f"{r['cobertura_automatica']:.0%}", flush=True)


# Divisão da entrada entre "sem cache", "escrita no cache" e "leitura do cache" medida na primeira rodada de um modelo
# (cache frio). O cache do servidor é compartilhado entre os níveis de esforço do mesmo modelo, então as configurações
# que rodaram depois pagaram menos escrita; o custo padronizado aplica a mesma divisão a todas.
DIVISAO_CACHE_FRIO = (0.1109, 0.3524, 0.5367)


def custo_padronizado(s: dict) -> float:
    p = PRECOS[s["modelo"]]
    entrada = s["tokens_entrada"] + s["tokens_cache_escrita"] + s["tokens_cache_leitura"]
    a, b, c = DIVISAO_CACHE_FRIO
    return (entrada * (a * p[0] + b * p[1] + c * p[2]) + s["tokens_saida"] * p[3]) / 1e6


def resultados(conjunto: str) -> list[dict]:
    """Uma linha por rodada, com o resultado da rodada cega e o do motor atual (quando reavaliado)."""
    out = []
    for f in sorted(SAIDA.glob(f"*/t*/resumo-{conjunto}.json")):
        s = json.loads(f.read_text(encoding="utf-8"))
        atual = f.parent / f"{conjunto}-motor-atual" / "resultado.json"
        r = json.loads(atual.read_text(encoding="utf-8"))["resumo"] if atual.exists() else s["resultado"]
        out.append({**s, "cega": s["resultado"], "atual": r, "custo_padronizado_usd": round(custo_padronizado(s), 4)})
    return out


def tabela(conjunto: str) -> str:
    linhas = sorted(resultados(conjunto), key=lambda s: (s["atual"]["erros_perigosos"], -s["atual"]["veredito_correto"],
                                                          s["custo_padronizado_usd"]))
    cab = ("| Modelo | Esforço | Rodada | Veredito | Faixa aceitável | Perigosos | Caros | Automático | "
           "Segundos por caso (média / p90) | Tokens de saída por chamada | US$ por caso (padronizado) | US$ pagos na rodada |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|---|")
    corpo = []
    for s in linhas:
        r, c = s["atual"], s["cega"]
        mudou = " (cega: {})".format(c["veredito_correto"]) if c["veredito_correto"] != r["veredito_correto"] else ""
        corpo.append(f"| {s['modelo']} | {s['esforco']} | {s['trial']} | {r['veredito_correto']}/{r['casos']}{mudou} | "
                     f"{r['faixa_aceitavel']}/{r['casos']} | {r['erros_perigosos']} | {r['erros_caros']} | "
                     f"{r['cobertura_automatica']:.0%} | {s['segundos_por_caso']} / {s['segundos_por_caso_p90']} | "
                     f"{s['saida_por_chamada']} | {s['custo_padronizado_usd'] / s['casos']:.4f} | {s['custo_usd']:.2f} |")
    return "\n".join([cab, *corpo])


NOMES = {"claude-opus-5-5": "Opus 5.5", "claude-sonnet-5-5": "Sonnet 5.5", "claude-haiku-5-5": "Haiku 5.5",
         "claude-opus-5": "Opus 5 (anterior)", "claude-sonnet-5": "Sonnet 5 (anterior)", "claude-haiku-4-5": "Haiku 4.5 (anterior)"}
ORDEM_ESFORCO = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4}


def _br(x: float, casas: int) -> str:
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def tabela_por_config(conjunto: str) -> str:
    """Junta as rodadas de cada configuração (acerto de cada rodada, erros somados, médias), agrupada por modelo."""
    grupos: dict[str, list[dict]] = {}
    for s in resultados(conjunto):
        grupos.setdefault(s["config"], []).append(s)
    ordem = list(NOMES)
    linhas = sorted(grupos.values(), key=lambda rs: (ordem.index(rs[0]["modelo"]) if rs[0]["modelo"] in ordem else 99,
                                                     ORDEM_ESFORCO.get(rs[0]["esforco"], 5)))
    cab = ("| Modelo | Esforço | Rodadas | Acertos em cada rodada (de 85) | Aceites indevidos | Recusas indevidas | "
           "Decididos sem revisão | Segundos por caso | US$ por caso | US$ por 1.000 casos |\n"
           "|---|---|---|---|---|---|---|---|---|---|")
    corpo = []
    for rs in linhas:
        rs.sort(key=lambda s: s["trial"])
        a = [s["atual"] for s in rs]
        n = rs[0]["casos"]
        custo = sum(s["custo_padronizado_usd"] for s in rs) / len(rs) / n
        corpo.append(f"| {NOMES.get(rs[0]['modelo'], rs[0]['modelo'])} | {rs[0]['esforco']} | {len(rs)} | "
                     f"{' · '.join(str(x['veredito_correto']) for x in a)} | {sum(x['erros_perigosos'] for x in a)} | "
                     f"{sum(x['erros_caros'] for x in a)} | {sum(x['cobertura_automatica'] for x in a) / len(a):.0%} | "
                     f"{sum(s['segundos_por_caso'] for s in rs) / len(rs):.0f} | {_br(custo, 4)} | {_br(1000 * custo, 2)} |")
    return "\n".join([cab, *corpo])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", nargs="*", default=MATRIZ, help="modelo:esforço (esforço 'padrao' = padrão do modelo)")
    ap.add_argument("--conjunto", default="todos")
    ap.add_argument("--casos", nargs="*")
    ap.add_argument("--trial", type=int, default=1, help="número da rodada (cada rodada tem cache próprio)")
    ap.add_argument("--paralelo", type=int, default=4, help="configurações rodando ao mesmo tempo")
    ap.add_argument("--workers", type=int, default=8, help="leituras simultâneas em cada configuração")
    ap.add_argument("--teto", type=float, default=150.0, help="não inicia nova configuração se o gasto passar disto (US$)")
    ap.add_argument("--tabela", action="store_true", help="só imprime a tabela do que já rodou")
    ap.add_argument("--por-config", action="store_true", help="tabela que junta as rodadas de cada configuração")
    ap.add_argument("--reavaliar", action="store_true", help="reavalia as leituras guardadas com o motor atual (sem API)")
    ap.add_argument("--um", help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.um:
        return rodar_um(a.um, a.conjunto, a.casos, a.trial, a.workers)
    if a.tabela:
        return print(tabela(a.conjunto))
    if a.por_config:
        return print(tabela_por_config(a.conjunto))
    if a.reavaliar:
        return reavaliar(a.conjunto, a.trial)

    fila = [c for c in a.configs if not (pasta(c, a.trial) / f"resumo-{a.conjunto}.json").exists()]
    rodando: dict[str, subprocess.Popen] = {}
    print(f"{len(fila)} configuração(ões) na fila; gasto até agora US$ {gasto():.2f}", flush=True)
    while fila or rodando:
        for c, p in list(rodando.items()):
            if p.poll() is not None:
                del rodando[c]
                f = pasta(c, a.trial) / f"resumo-{a.conjunto}.json"
                if f.exists():
                    s = json.loads(f.read_text(encoding="utf-8"))
                    r = s["resultado"]
                    print(f"FIM {c}: veredito {r['veredito_correto']}/{r['casos']} · perigosos {r['erros_perigosos']} · "
                          f"caros {r['erros_caros']} · erros {s['erros_de_leitura']} · {s['segundos_por_caso']}s/caso · "
                          f"US$ {s['custo_usd']:.2f} · gasto total US$ {gasto():.2f}", flush=True)
                else:
                    print(f"FALHOU {c} (código {p.returncode}): veja {pasta(c, a.trial) / 'log.txt'}", flush=True)
        while fila and len(rodando) < a.paralelo:
            if gasto() > a.teto:
                print(f"TETO: gasto US$ {gasto():.2f} passou de US$ {a.teto:.2f}; não inicio {', '.join(fila)}", flush=True)
                fila.clear()
                break
            c = fila.pop(0)
            dest = pasta(c, a.trial)
            dest.mkdir(parents=True, exist_ok=True)
            cmd = [sys.executable, __file__, "--um", c, "--conjunto", a.conjunto, "--trial", str(a.trial),
                   "--workers", str(a.workers), *(["--casos", *a.casos] if a.casos else [])]
            rodando[c] = subprocess.Popen(cmd, stdout=open(dest / "log.txt", "w"), stderr=subprocess.STDOUT, cwd=RAIZ)
            print(f"INÍCIO {c}", flush=True)
        time.sleep(5)
    print(f"FIM GERAL: gasto total US$ {gasto():.2f}", flush=True)
    (SAIDA / f"tabela-{a.conjunto}.md").write_text(tabela(a.conjunto) + "\n\n" + tabela_por_config(a.conjunto) + "\n",
                                                  encoding="utf-8")


if __name__ == "__main__":
    main()
