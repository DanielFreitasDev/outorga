"""Consulta de quem é o proprietário de um veículo (placa/RENAVAM).

No DETRAN, essa informação vem da própria base veicular (RENAVAM). O protótipo usa uma base SIMULADA em JSON
(`corpus/base_veicular.json`, gerada a partir do corpus fictício por `corpus/gerar_base_veicular.py`) e, na falta dela,
o CRLV anexado. Para integrar com a base real, basta trocar `consultar()` por uma chamada ao serviço do órgão
(variável `OUTORGA_BASE_VEICULAR` aponta para o arquivo ou, no futuro, para a URL do serviço).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from .ids import placas_equivalentes, so_digitos

RAIZ = Path(__file__).resolve().parents[2]
PADRAO = RAIZ / "corpus" / "base_veicular.json"


def _arquivo() -> Path:
    return Path(os.environ.get("OUTORGA_BASE_VEICULAR") or PADRAO)


@lru_cache(maxsize=4)
def _carregar(caminho: str, mtime: float) -> list[dict]:
    return json.loads(Path(caminho).read_text(encoding="utf-8")).get("veiculos", [])


def disponivel() -> bool:
    return _arquivo().exists()


def consultar(placa: str | None = None, renavam: str | None = None) -> dict | None:
    """Devolve {placa, renavam, chassi, marca_modelo, proprietario: {tipo, nome, documento}, fonte} ou None."""
    arq = _arquivo()
    if not arq.exists() or not (placa or renavam):
        return None
    ren = so_digitos(renavam)
    for v in _carregar(str(arq), arq.stat().st_mtime):
        if (ren and so_digitos(v.get("renavam")) == ren) or (placa and v.get("placa") and placas_equivalentes(placa, v["placa"])):
            return {**v, "fonte": "base veicular simulada (protótipo)"}
    return None
