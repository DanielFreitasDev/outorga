"""Gera a base veicular SIMULADA (corpus/base_veicular.json): quem é o proprietário de cada veículo do corpus.

No DETRAN essa consulta é feita na base RENAVAM; aqui ela é simulada com os dados fictícios de `cenarios.json`
(proprietário = o do CRLV de cada caso).

    uv run python corpus/gerar_base_veicular.py
"""

from __future__ import annotations

import json
from pathlib import Path

AQUI = Path(__file__).parent
SPEC = json.loads((AQUI / "cenarios.json").read_text(encoding="utf-8"))
DESTINO = AQUI / "base_veicular.json"


def main() -> None:
    veiculos = {}
    casos = SPEC["casos"] + SPEC.get("casos_holdout", []) + SPEC.get("casos_atpv", []) + SPEC.get("casos_pf", [])
    for c in casos:
        v = SPEC["veiculos"][c["veiculo"]]
        dono = c["crlv_proprietario"]
        if dono["tipo"] == "PJ":
            e = SPEC["empresas"][dono["empresa"]]
            pr = {"tipo": "PJ", "nome": e["razao_social"], "documento": e["cnpj"]}
        else:
            p = SPEC["pessoas"][dono["pessoa"]]
            pr = {"tipo": "PF", "nome": p["nome"].upper(), "documento": p["cpf"]}
        veiculos[v["placa"]] = {"placa": v["placa"], "renavam": v["renavam"], "chassi": v["chassi"],
                                "marca_modelo": v["marca_modelo"], "ano_modelo": v["ano_modelo"], "proprietario": pr}
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(json.dumps({"aviso": "BASE SIMULADA — dados fictícios do corpus de avaliação",
                                   "veiculos": list(veiculos.values())}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(veiculos)} veículos em {DESTINO}")


if __name__ == "__main__":
    main()
