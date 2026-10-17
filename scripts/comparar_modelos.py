"""Compara um modelo de IA local na mesma avaliação dos outros (docs/MODELOS.md).

Sobe um llama-server só para o teste (porta 8092, tudo na GPU), roda a avaliação com um cache de leituras próprio do
modelo, mede tempo, tokens, temperatura e memória da GPU e desliga o servidor no fim. A trava térmica do Outorga
(OUTORGA_TEMP_MAX/OUTORGA_TEMP_RETOMAR) pausa entre chamadas quando a GPU esquenta.

    uv run python scripts/comparar_modelos.py --id gemma-x --gguf /caminho/modelo.gguf --conjunto todos
    uv run python scripts/comparar_modelos.py --id gemma-x --gguf ... --casos I01 I02 A01   # só alguns casos
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LLAMA = Path(os.environ.get("LLAMA_SERVER", Path.home() / "local-ai/src/llama.cpp/build/bin/llama-server"))
PORTA = 8092


def gpu() -> tuple[int, int, int] | None:
    try:
        s = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used,utilization.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
        t, m, u = (int(x) for x in s.strip().split(", "))
        return t, m, u
    except Exception:  # noqa: BLE001
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="nome curto do modelo (vira o nome no cache e nos resultados)")
    ap.add_argument("--gguf", required=True)
    ap.add_argument("--ctx", type=int, default=12288)
    ap.add_argument("--conjunto", default="todos")
    ap.add_argument("--casos", nargs="*")
    ap.add_argument("--extra", default="", help="argumentos extras do llama-server (ex.: '--n-cpu-moe 24')")
    ap.add_argument("--apagar", action="store_true", help="apaga o GGUF no fim (só arquivos dentro de models/bench)")
    a = ap.parse_args()

    saida = RAIZ / "avaliacoes" / "modelos" / a.id
    saida.mkdir(parents=True, exist_ok=True)
    os.environ.update({"OUTORGA_LLM": "llamacpp", "OUTORGA_LLM_URL": f"http://127.0.0.1:{PORTA}/v1",
                       "OUTORGA_LLM_MODELO": a.id, "OUTORGA_CACHE": str(saida / "cache"),
                       "OUTORGA_TEMP_MAX": os.environ.get("OUTORGA_TEMP_MAX", "70"),
                       "OUTORGA_TEMP_RETOMAR": os.environ.get("OUTORGA_TEMP_RETOMAR", "62")})
    base_gpu = gpu()
    cmd = [str(LLAMA), "-m", a.gguf, "--host", "127.0.0.1", "--port", str(PORTA), "-c", str(a.ctx), "-ngl", "99",
           "-fa", "on", "-np", "1", "--jinja", "--no-mmproj", *a.extra.split()]
    log = open(saida / "servidor.log", "w")
    srv = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
    amostras: list[tuple[int, int, int]] = []
    parar = threading.Event()

    cpu: list[int] = []

    def medir() -> None:
        from outorga.llm import temperatura_cpu

        while not parar.is_set():
            g = gpu()
            if g:
                amostras.append(g)
            if (c := temperatura_cpu()) is not None:
                cpu.append(c)
            parar.wait(5)

    try:
        import httpx

        for _ in range(240):
            try:
                if httpx.get(f"http://127.0.0.1:{PORTA}/health", timeout=2).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            if srv.poll() is not None:
                raise SystemExit(f"o servidor não subiu: veja {saida / 'servidor.log'}")
            time.sleep(1)
        sys.path.insert(0, str(RAIZ / "src"))
        threading.Thread(target=medir, daemon=True).start()
        from outorga.avaliacao import rodar
        from outorga.engine import Politica
        from outorga.llm import LlamaCpp

        inicio = datetime.now()
        r = rodar("llm", a.casos, Politica.por_nome("ce"), LlamaCpp(), 1, saida / a.conjunto, conjunto=a.conjunto)
        fim = datetime.now()
    finally:
        parar.set()
        srv.terminate()
        try:
            srv.wait(30)
        except subprocess.TimeoutExpired:
            srv.kill()
        log.close()

    chamadas = list((saida / "cache").rglob("*.json"))
    segs = tin = tout = 0.0
    for c in chamadas:
        m = json.loads(c.read_text(encoding="utf-8")).get("meta", {})
        segs += m.get("segundos") or 0
        tin += m.get("tokens_entrada") or 0
        tout += m.get("tokens_saida") or 0
    resumo = {
        "modelo": a.id, "gguf": Path(a.gguf).name, "tamanho_gb": round(Path(a.gguf).stat().st_size / 1e9, 2), "ctx": a.ctx,
        "conjunto": a.conjunto, "inicio": inicio.isoformat(timespec="seconds"), "fim": fim.isoformat(timespec="seconds"),
        "duracao_min": round((fim - inicio).total_seconds() / 60, 1), "chamadas": len(chamadas),
        "inferencia_min": round(segs / 60, 1), "tokens_entrada": int(tin), "tokens_saida": int(tout),
        "tok_s_geracao_aprox": round(tout / segs, 1) if segs else None,
        "gpu_temp_max": max((x[0] for x in amostras), default=None),
        "gpu_mem_max_mb": max((x[1] for x in amostras), default=None),
        "gpu_mem_base_mb": base_gpu[1] if base_gpu else None,
        "cpu_temp_max": max(cpu, default=None),
        "resultado": r["resumo"],
        "erros_de_leitura": sum(1 for l in r["linhas"] if l["previsto"] == "ERRO"),
    }
    resumo["llama_server"] = " ".join(cmd[1:])
    (saida / f"resumo-{a.conjunto}.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    gguf = Path(a.gguf).resolve()
    if a.apagar and gguf.parent.name == "bench" and gguf.parent.parent.name == "models":
        gguf.unlink()
        print(f"apagado: {gguf}")
    print(json.dumps({k: resumo[k] for k in ("modelo", "duracao_min", "tok_s_geracao_aprox", "gpu_temp_max", "gpu_mem_max_mb",
                                             "cpu_temp_max", "erros_de_leitura")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
