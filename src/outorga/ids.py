"""Identificadores brasileiros (CPF, CNPJ, RENAVAM, placa, chassi) e normalização de nomes.

Tudo aqui é determinístico e sem dependência de LLM: é a base para casar pessoas e veículos
entre documentos diferentes (contrato social, procuração, CRLV, pedido de venda).
"""

from __future__ import annotations

import random
import re

from rapidfuzz import fuzz
from unidecode import unidecode


def so_digitos(s: str | None) -> str:
    return re.sub(r"\D", "", s or "")


# ----------------------------------------------------------------------------------------- CPF
def _cpf_dv(base: str) -> str:
    for n in (9, 10):
        soma = sum(int(d) * (n + 1 - i) for i, d in enumerate(base[:n]))
        dv = (soma * 10) % 11
        base = base[:n] + str(0 if dv == 10 else dv)
    return base[9:11]


def cpf_valido(cpf: str | None) -> bool:
    d = so_digitos(cpf)
    if len(d) != 11 or d == d[0] * 11:
        return False
    return _cpf_dv(d[:9] + "00") == d[9:]


def cpf_formatado(cpf: str) -> str:
    d = so_digitos(cpf)
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}" if len(d) == 11 else cpf


def gerar_cpf(rng: random.Random) -> str:
    while True:
        base = "".join(str(rng.randint(0, 9)) for _ in range(9))
        if base != base[0] * 9:
            return cpf_formatado(base + _cpf_dv(base + "00"))


# ---------------------------------------------------------------------------------------- CNPJ
_PESOS_CNPJ_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_PESOS_CNPJ_2 = [6] + _PESOS_CNPJ_1


def _cnpj_dv(base12: str) -> str:
    def dv(nums: str, pesos: list[int]) -> str:
        r = sum(int(n) * p for n, p in zip(nums, pesos)) % 11
        return "0" if r < 2 else str(11 - r)

    d1 = dv(base12, _PESOS_CNPJ_1)
    return d1 + dv(base12 + d1, _PESOS_CNPJ_2)


def cnpj_valido(cnpj: str | None) -> bool:
    d = so_digitos(cnpj)
    if len(d) != 14 or d == d[0] * 14:
        return False
    return _cnpj_dv(d[:12]) == d[12:]


def cnpj_formatado(cnpj: str) -> str:
    d = so_digitos(cnpj)
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 else cnpj


def gerar_cnpj(rng: random.Random) -> str:
    base = "".join(str(rng.randint(0, 9)) for _ in range(8)) + "0001"
    return cnpj_formatado(base + _cnpj_dv(base))


# ------------------------------------------------------------------------------------- RENAVAM
def _renavam_dv(base10: str) -> str:
    pesos = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(d) * p for d, p in zip(base10, pesos))
    dv = (soma * 10) % 11
    return "0" if dv == 10 else str(dv)


def renavam_valido(renavam: str | None) -> bool:
    d = so_digitos(renavam).zfill(11)
    return len(d) == 11 and _renavam_dv(d[:10]) == d[10]


def gerar_renavam(rng: random.Random) -> str:
    base = "0" + "".join(str(rng.randint(0, 9)) for _ in range(9))
    return base + _renavam_dv(base)


# --------------------------------------------------------------------------------- placa/chassi
_RE_PLACA = re.compile(r"^[A-Z]{3}\d[A-Z0-9]\d{2}$")
_MERCOSUL = "ABCDEFGHIJ"


def normalizar_placa(placa: str | None) -> str:
    return re.sub(r"[^A-Z0-9]", "", unidecode(placa or "").upper())


def placa_valida(placa: str | None) -> bool:
    return bool(_RE_PLACA.match(normalizar_placa(placa)))


def placas_equivalentes(a: str | None, b: str | None) -> bool:
    """Compara placas aceitando a conversão antiga→Mercosul (ABC1234 ≡ ABC1C34)."""
    pa, pb = normalizar_placa(a), normalizar_placa(b)
    if not pa or not pb:
        return False
    if pa == pb:
        return True

    def mercosul(p: str) -> str:
        if len(p) == 7 and p[4].isdigit():
            return p[:4] + _MERCOSUL[int(p[4])] + p[5:]
        return p

    return mercosul(pa) == mercosul(pb)


def gerar_placa(rng: random.Random) -> str:
    letras = "ABCDEFGHJKLMNPRSTUVWXYZ"
    return (
        "".join(rng.choice(letras) for _ in range(3))
        + str(rng.randint(0, 9))
        + rng.choice(letras)
        + f"{rng.randint(0, 99):02d}"
    )


def normalizar_chassi(chassi: str | None) -> str:
    return re.sub(r"[^A-Z0-9]", "", unidecode(chassi or "").upper())


def gerar_chassi(rng: random.Random, wmi: str = "9BD") -> str:
    validos = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    return wmi + "".join(rng.choice(validos) for _ in range(14))


# ------------------------------------------------------------------------------------- nomes
_PARTICULAS = {"DA", "DE", "DO", "DAS", "DOS", "E", "D"}


def normalizar_nome(nome: str | None) -> str:
    s = unidecode(nome or "").upper()
    s = re.sub(r"\b(DR|DRA|SR|SRA)\.?\s+", " ", s)
    s = re.sub(r"[^A-Z ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _tokens(nome: str) -> list[str]:
    return [t for t in normalizar_nome(nome).split() if t not in _PARTICULAS]


def similaridade_nomes(a: str | None, b: str | None) -> float:
    """0–100. Tolera acentos, caixa, partículas (da/de/dos) e abreviações ("João B. Andrade")."""
    ta, tb = _tokens(a or ""), _tokens(b or "")
    if not ta or not tb:
        return 0.0
    base = fuzz.token_sort_ratio(" ".join(ta), " ".join(tb))
    # abreviação: cada token da forma curta casa com um token da forma longa (inicial ou inteiro)
    curto, longo = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if curto[0] == longo[0] and curto[-1] == longo[-1]:
        restantes = list(longo[1:-1])
        ok = True
        for t in curto[1:-1]:
            achou = next((r for r in restantes if r == t or (len(t) == 1 and r.startswith(t))), None)
            if achou is None:
                ok = False
                break
            restantes.remove(achou)
        if ok:
            base = max(base, 93.0 if len(curto) < len(longo) or any(len(t) == 1 for t in curto) else 100.0)
    return float(base)


def mesmo_individuo(nome_a: str | None, cpf_a: str | None, nome_b: str | None, cpf_b: str | None) -> tuple[bool, str]:
    """Decide se dois registros são a mesma pessoa. Retorna (bool, criterio)."""
    da, db = so_digitos(cpf_a), so_digitos(cpf_b)
    if len(da) == 11 and len(db) == 11:
        return (da == db, "cpf")
    s = similaridade_nomes(nome_a, nome_b)
    return (s >= 92, f"nome:{s:.0f}")


def formatar_documento(doc: str | None) -> str | None:
    """CPF/CNPJ só com dígitos → com pontuação (o resto volta como veio)."""
    d = so_digitos(doc)
    if len(d) == 11:
        return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    if len(d) == 14:
        return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
    return doc
