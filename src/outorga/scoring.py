"""Índice de aceitação (0–100) e a "faixa intermediária" que o chefe pediu.

    índice = 50 + 50 × direção × confiança
        direção   = +1 (pode assinar), −1 (não pode), 0 (indeterminado)
        confiança = leitura (ancoragem × conferência léxica × OCR × consistência) × robustez jurídica

    VERDE    índice ≥ limiar_aceite   e nenhum alerta     → aceito automaticamente
    VERMELHO índice ≤ limiar_recusa   e nenhum alerta     → recusado automaticamente
    AMARELO  o resto                                       → revisão humana (com a lista do que conferir)

Os limiares são calibrados com casos rotulados (gabarito + revisões humanas acumuladas): para um risco
máximo α na faixa automática, escolhemos o limiar que maximiza a cobertura com o limite superior de
Clopper-Pearson (95%) do erro abaixo de α. Com poucos casos o limite é largo — e é isso que deve ser:
o sistema só fica mais automático à medida que prova que acerta.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .domain import Faixa, Severidade, Veredito, fator_ancoragem  # noqa: F401
from .engine import Politica, Resultado, faixa_por_indice

ALERTAS_DE_LEITURA = 80.0  # fato decisivo com ancoragem abaixo disto => revisão


@dataclass
class Avaliacao:
    indice: float
    confianca: float
    faixa: Faixa
    componentes: dict = field(default_factory=dict)
    motivos: list[str] = field(default_factory=list)


def avaliar(res: Resultado, pol: Politica) -> Avaliacao:
    motivos = []
    confs = [f["confianca"] for f in res.fatos_decisivos if f.get("confianca") is not None]
    if not confs:
        confs = [0.8]
    c_leitura = 0.5 * min(confs) + 0.5 * (sum(confs) / len(confs))
    fracas = [f for f in res.fatos_decisivos if f.get("fonte") is not None and (f["fonte"].ancoragem or 0) < ALERTAS_DE_LEITURA]
    alertas = [a for a in res.achados if a.severidade == Severidade.ALERTA]
    if res.escolhida:
        alertas += [a for a in res.escolhida.achados if a.severidade == Severidade.ALERTA]
    atencoes = [a for a in res.achados if a.severidade == Severidade.ATENCAO]
    if res.escolhida:
        atencoes += [a for a in res.escolhida.achados if a.severidade == Severidade.ATENCAO]
    c_juridica = max(0.6, 1.0 - 0.06 * len(atencoes))
    confianca = round(c_leitura * c_juridica, 3)
    direcao = {Veredito.PODE: 1, Veredito.NAO_PODE: -1, Veredito.INDETERMINADO: 0}[res.veredito]
    indice = round(50 + 50 * direcao * confianca, 1)
    forcar = False
    if res.veredito == Veredito.INDETERMINADO:
        forcar = True
        motivos.append("indeterminado: " + "; ".join(res.indeterminacoes or ["pendência"]))
    if alertas:
        forcar = True
        motivos += [f"alerta: {t}" for t in dict.fromkeys(a.titulo for a in alertas)]
    if fracas:
        forcar = True
        motivos.append(f"{len(fracas)} fato(s) decisivo(s) com citação pouco ancorada no texto")
    faixa = faixa_por_indice(indice, pol, forcar)
    if not forcar:
        if faixa == Faixa.AMARELO:
            motivos.append(f"índice {indice:g} entre os limiares ({pol.limiar_recusa:g}–{pol.limiar_aceite:g})")
        else:
            motivos.append(f"índice {indice:g} {'≥' if faixa == Faixa.VERDE else '≤'} limiar "
                           f"{pol.limiar_aceite if faixa == Faixa.VERDE else pol.limiar_recusa:g}")
    return Avaliacao(indice, confianca, faixa, {
        "leitura": round(c_leitura, 3), "juridica": round(c_juridica, 3), "fatos_decisivos": len(res.fatos_decisivos),
        "menor_confianca_fato": round(min(confs), 3), "alertas": len(set(map(id, alertas))), "atencoes": len(atencoes),
        "fatos_pouco_ancorados": len(fracas)}, motivos)


# ------------------------------------------------------------------------------- calibração
def clopper_pearson_sup(erros: int, n: int, conf: float = 0.95) -> float:
    """Limite superior unilateral do erro (Clopper-Pearson) por bisseção na binomial."""
    if n == 0:
        return 1.0
    if erros >= n:
        return 1.0
    alvo = 1 - conf

    def cdf(p: float) -> float:
        return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(erros + 1))

    lo, hi = erros / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cdf(mid) > alvo:
            lo = mid
        else:
            hi = mid
    return hi


@dataclass
class Ponto:
    limiar: float
    cobertura: float
    decididos: int
    erros: int
    risco: float
    risco_sup: float


def curva_risco_cobertura(itens: list[dict], lado: str) -> list[Ponto]:
    """itens: {'indice', 'previsto', 'esperado'}. lado='aceite' (PODE) ou 'recusa' (NAO_PODE)."""
    n = len(itens)
    pts = []
    limiares = [x / 2 for x in range(100, 201)] if lado == "aceite" else [x / 2 for x in range(100, -1, -1)]
    for t in limiares:
        if lado == "aceite":
            dec = [i for i in itens if i["previsto"] == "PODE" and i["indice"] >= t]
            err = [i for i in dec if i["esperado"] != "PODE"]
        else:
            dec = [i for i in itens if i["previsto"] == "NAO_PODE" and i["indice"] <= t]
            err = [i for i in dec if i["esperado"] != "NAO_PODE"]
        risco = len(err) / len(dec) if dec else 0.0
        pts.append(Ponto(t, len(dec) / n if n else 0, len(dec), len(err), risco, clopper_pearson_sup(len(err), len(dec))))
    return pts


def sugerir_limiares(itens: list[dict], alfa: float = 0.05, usar_limite_superior: bool = False) -> dict:
    """Menor limiar de aceite (maior de recusa) cujo risco (ou limite superior) fica ≤ α."""
    out = {}
    for lado in ("aceite", "recusa"):
        pts = curva_risco_cobertura(itens, lado)
        ok = [p for p in pts if p.decididos > 0 and (p.risco_sup if usar_limite_superior else p.risco) <= alfa]
        if lado == "aceite":
            melhor = min(ok, key=lambda p: p.limiar) if ok else None
        else:
            melhor = max(ok, key=lambda p: p.limiar) if ok else None
        out[lado] = melhor.__dict__ if melhor else None
        out[f"curva_{lado}"] = [p.__dict__ for p in pts]
    return out
