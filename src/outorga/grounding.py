"""Ancoragem de evidências: o trecho que o LLM citou existe mesmo no documento? Onde?

Cada fato extraído vem com uma citação literal. Aqui ela é localizada no texto original
(comparação aproximada, tolerante a OCR, acentos e quebras de linha). O resultado alimenta:
- o score (citação que não existe = possível alucinação => confiança baixa);
- a interface (destaque do trecho exato na página do documento).
"""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz
from unidecode import unidecode

from .ingest import Documento


@dataclass
class Ancora:
    score: float          # 0-100
    inicio: int | None    # posição no texto original
    fim: int | None
    pagina: int | None
    trecho_original: str | None


def _normalizar_com_mapa(texto: str) -> tuple[str, list[int]]:
    """Normaliza (minúsculas, sem acento, espaços colapsados) guardando o índice original de cada caractere."""
    out, mapa, ultimo_espaco = [], [], False
    for i, ch in enumerate(texto):
        base = unidecode(ch).lower() if ord(ch) > 127 else ch.lower()
        if not base:
            continue
        if base.isspace():
            if ultimo_espaco:
                continue
            base, ultimo_espaco = " ", True
        else:
            ultimo_espaco = False
        for b in base:
            out.append(b)
            mapa.append(i)
    return "".join(out), mapa


class Ancorador:
    def __init__(self, doc: Documento):
        self.doc = doc
        self.texto = doc.texto
        self.norm, self.mapa = _normalizar_com_mapa(self.texto)

    def ancorar(self, citacao: str | None) -> Ancora:
        if not citacao or len(citacao.strip()) < 4:
            return Ancora(0.0, None, None, None, None)
        alvo, _ = _normalizar_com_mapa(citacao.strip().strip('"“”'))
        if not alvo.strip():
            return Ancora(0.0, None, None, None, None)
        pos = self.norm.find(alvo)
        if pos >= 0:
            score, ini, fim = 100.0, pos, pos + len(alvo)
        else:
            al = fuzz.partial_ratio_alignment(alvo, self.norm, score_cutoff=0)
            if al is None:
                return Ancora(0.0, None, None, None, None)
            score, ini, fim = al.score, al.dest_start, al.dest_end
            # citação muito longa parcialmente inventada: penaliza pela fração coberta
            cobertura = (fim - ini) / max(1, len(alvo))
            if cobertura < 0.8:
                score *= cobertura
        o_ini = self.mapa[ini] if ini < len(self.mapa) else None
        o_fim = (self.mapa[fim - 1] + 1) if 0 < fim <= len(self.mapa) else None
        pagina = self.doc.pagina_de(o_ini) if o_ini is not None else None
        trecho = self.texto[o_ini:o_fim] if o_ini is not None and o_fim is not None else None
        return Ancora(round(score, 1), o_ini, o_fim, pagina, trecho)

    def contem_valor(self, valor: str | None) -> bool:
        """O valor (CPF, placa, número) aparece literalmente no documento?"""
        if not valor:
            return False
        alvo, _ = _normalizar_com_mapa(valor)
        return alvo.strip() in self.norm
