"""Confere se os documentos redigidos respeitam a especificação (`cenarios.json`).

    uv run python corpus/verificar_docs.py            # todos
    uv run python corpus/verificar_docs.py SERTAO_CS POA_PEDRO
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).parent
SPEC = json.loads((AQUI / "cenarios.json").read_text(encoding="utf-8"))
DOCS_DIR = AQUI / "docs"

PROIBIDAS_IRACEMA = ["isoladamente", "indistintamente", "em conjunto", "conjuntamente", "individualmente",
                     "separadamente", "de per si", "qualquer um", "qualquer deles", "ambos assinar",
                     "assinatura de ambos", "isolada", "conjunta"]


def _norm(s: str) -> str:
    s = s.replace(" ", " ").replace("**", "")
    return re.sub(r"\s+", " ", s).strip()


def verificar(did: str) -> list[str]:
    d = SPEC["documentos"][did]
    arq = DOCS_DIR / f"{did}.md"
    if not arq.exists():
        return [f"arquivo ausente: {arq}"]
    texto = arq.read_text(encoding="utf-8")
    t = _norm(texto)
    erros = []
    for frase in d["frases_obrigatorias"]:
        if _norm(frase) not in t:
            erros.append(f"frase obrigatória ausente: «{frase}»")
    n = len(re.findall(r"\w+", texto))
    lo, hi = d["palavras"]
    if n < lo * 0.8 or n > hi * 1.25:
        erros.append(f"tamanho {n} palavras fora de {lo}-{hi}")
    emp = SPEC["empresas"].get(d["empresa"]) if d.get("empresa") else None  # None: pessoa física em nome próprio
    if emp is None:
        pass
    elif d["tipo"] != "procuracao" or "em NOME PRÓPRIO" not in " ".join(d["instrucoes"]):
        if emp["cnpj"] not in t and d["tipo"] != "ata_reuniao_socios":
            erros.append(f"CNPJ da empresa ausente ({emp['cnpj']})")
    else:
        if emp["razao_social"].split()[0] in t.upper() and emp["cnpj"] in t:
            erros.append("procuração em nome próprio não deveria citar a empresa")
    # CPFs de todas as pessoas citadas nas instruções devem aparecer
    instr = " ".join(d["instrucoes"])
    for p in SPEC["pessoas"].values():
        if p["nome"] in instr and p["cpf"] not in t:
            erros.append(f"CPF de {p['nome']} ausente ({p['cpf']})")
    if d.get("registro") and d["registro"]["numero"] not in t:
        erros.append(f"número de registro JUCEC ausente ({d['registro']['numero']})")
    if did == "IRACEMA_CS":
        adm = re.search(r"(?is)administra[çc][ãa]o.{0,1500}", texto)
        trecho = (adm.group(0) if adm else texto).lower()
        for w in PROIBIDAS_IRACEMA:
            if w in trecho:
                erros.append(f"IRACEMA_CS não pode conter «{w}» perto da cláusula de administração")
    for v in SPEC["veiculos"].values():
        if v["marca_modelo"] in instr and v["placa"] not in t:
            erros.append(f"placa do veículo {v['marca_modelo']} ausente ({v['placa']})")
    return erros


def main() -> int:
    ids = sys.argv[1:] or list(SPEC["documentos"])
    falhas = 0
    for did in ids:
        erros = verificar(did)
        if erros:
            falhas += 1
            print(f"✗ {did}")
            for e in erros:
                print(f"    - {e}")
        else:
            print(f"✓ {did}")
    print(f"\n{len(ids) - falhas}/{len(ids)} ok")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
