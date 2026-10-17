"""Parte 2 da rodada cega do lote ATPV-e (A08, A09, A13) com o motor EXATAMENTE como estava antes das correções
motivadas pela parte 1: desliga as três funções novas (cláusula geral de administração vale para comprar; cargo nomeado
restringe a regra; Conselho Fiscal não representa). Assim a medição continua cega para essas correções."""
import sys
from pathlib import Path
import outorga.lexicon as lx
lx.clausula_geral_de_administracao = lambda texto: False
lx.cargos_signatarios = lambda texto: []
lx.cargo_sem_representacao = lambda cargo: False
from outorga.avaliacao import RESULTADOS, rodar
from outorga.engine import Politica
from outorga.llm import provedor_padrao
rodar("llm", ["A08", "A09", "A13"], Politica.por_nome("ce"), provedor_padrao(), 1, RESULTADOS / "llm-atpv-parte2", conjunto="atpv")
