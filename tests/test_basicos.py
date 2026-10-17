"""Testes determinísticos (sem LLM): identificadores, léxico jurídico, ancoragem e auditoria."""

from datetime import date

import pytest

from outorga import lexicon as lx
from outorga.ids import (cnpj_valido, cpf_valido, gerar_cpf, gerar_renavam, placas_equivalentes, renavam_valido,
                         similaridade_nomes)


# ------------------------------------------------------------------------------------------ ids
def test_cpf_cnpj():
    assert cpf_valido("529.982.247-25")
    assert not cpf_valido("111.111.111-11")
    assert not cpf_valido("529.982.247-24")
    assert cnpj_valido("33.000.167/0001-01")
    assert not cnpj_valido("33.000.167/0001-02")


def test_geradores_validos():
    import random
    r = random.Random(7)
    assert all(cpf_valido(gerar_cpf(r)) for _ in range(50))
    assert all(renavam_valido(gerar_renavam(r)) for _ in range(50))


def test_placa_mercosul():
    assert placas_equivalentes("ABC-1234", "ABC1C34")
    assert not placas_equivalentes("ABC1234", "ABC1D34")


def test_nomes():
    assert similaridade_nomes("Joao B. Andrade", "JOÃO BATISTA ANDRADE") >= 90
    assert similaridade_nomes("Dra. Paula Regina Saraiva", "PAULA REGINA SARAIVA") == 100
    assert similaridade_nomes("João Batista Andrade", "Maria Clara Fontenele") < 60


# -------------------------------------------------------------------------------------- léxico
@pytest.mark.parametrize("texto, esperado", [
    ("que a exercerão indistintamente", "isolado"),
    ("qualquer deles isoladamente", "isolado"),
    ("em conjunto ou isoladamente", "isolado"),
    ("isolada ou conjuntamente", "isolado"),
    ("exercida conjuntamente pelos sócios", "conjunto"),
    ("sendo vedada a prática isolada de qualquer ato de alienação", "conjunto"),
    ("dependerá da assinatura conjunta de ambos os administradores", "conjunto"),
    ("por 2 (dois) Diretores em conjunto", "conjunto"),
    ("com os poderes e atribuições de administradores", None),
])
def test_modo(texto, esperado):
    assert lx.modo_por_lexico(texto).modo == esperado


def test_imoveis_nao_alcancam_veiculo():
    s = lx.escopo_por_lexico("onerar ou alienar bens imóveis da sociedade, sem autorização dos sócios")
    assert s.so_imoveis and s.alienacao
    s2 = lx.escopo_por_lexico("alienação de bens do ativo não circulante, inclusive veículos automotores")
    assert not s2.so_imoveis and s2.menciona_veiculo and s2.menciona_imobilizado


def test_poderes():
    g = lx.poderes_por_lexico("amplos e gerais poderes para gerir e administrar, representar perante o DETRAN, licenciar veículos")
    assert g.gerais and not g.alienar
    e = lx.poderes_por_lexico("poderes especiais e expressos para vender, ceder e transferir veículos, assinar a ATPV-e")
    assert e.especiais and e.alienar and e.atpv


@pytest.mark.parametrize("texto, esperado", [
    ("sendo expressamente vedado o substabelecimento", "vedado"),
    ("não podendo substabelecer", "vedado"),
    ("podendo substabelecer, no todo ou em parte, com reserva de iguais poderes", "permitido_com_reserva"),
    ("podendo substabelecer", "permitido"),
    ("o mandato vigorará por um ano", None),
])
def test_substabelecimento(texto, esperado):
    assert lx.substabelecimento_por_lexico(texto) == esperado


def test_datas_e_prazos():
    assert lx.parse_data("Fortaleza/CE, 10 de dezembro de 2026.") == date(2026, 12, 10)
    assert lx.parse_data("1º de março de 2025") == date(2025, 3, 1)
    assert lx.parse_data("15/01/2026") == date(2026, 1, 15)
    assert lx.somar_prazo(date(2025, 1, 20), "pelo prazo de 6 (seis) meses") == date(2025, 7, 20)
    assert lx.somar_prazo(date(2021, 2, 10), "pelo prazo de 3 (três) anos, contados do registro") == date(2024, 2, 10)
    assert lx.somar_prazo(date(2026, 7, 1), "90 (noventa) dias") == date(2026, 9, 29)
    assert lx.valor_monetario("superior a R$ 150.000,00 (cento e cinquenta mil reais)") == 150000.0


# ------------------------------------------------------------------------------------ ancoragem
def test_ancoragem():
    from outorga.grounding import Ancorador
    from outorga.ingest import Documento, _calc_offsets

    pags = ["CLÁUSULA SÉTIMA – DA ADMINISTRAÇÃO\nA administração caberá aos sócios, que a\nexercerão indistintamente.",
            "Parágrafo único. É vedado o uso do nome empresarial em avais."]
    d = Documento("X", "x.pdf", "x.pdf", pags, "h", "texto")
    d.offsets = _calc_offsets(pags)
    a = Ancorador(d)
    exato = a.ancorar("que a exercerão indistintamente")
    assert exato.score == 100 and exato.pagina == 1
    ruido = a.ancorar("que a exercerao indistintamente")  # sem acento / OCR
    assert ruido.score >= 95
    assert a.ancorar("vedado o uso do nome empresarial").pagina == 2
    assert a.ancorar("os administradores assinarão sempre em conjunto com o conselho fiscal").score < 75


# ------------------------------------------------------------------------------------ auditoria
def test_cadeia_de_auditoria(tmp_path, monkeypatch):
    from outorga import store

    monkeypatch.setattr(store, "DADOS", tmp_path)
    monkeypatch.setattr(store, "_con", None)
    store.auditar("analise", "A1", {"x": 1})
    store.auditar("revisao_humana", "A1", {"decisao": "aprovar"})
    store.auditar("politica", None, {"limiar": 85})
    assert store.verificar_cadeia() == {**store.verificar_cadeia(), "integra": True, "registros": 3}
    store.con().execute("UPDATE auditoria SET payload_hash = 'adulterado' WHERE seq = 2")
    v = store.verificar_cadeia()
    assert not v["integra"] and v["quebra_em"] == 2
