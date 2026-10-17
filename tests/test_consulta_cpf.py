"""Chefe (17/10, 11:40): consulta ANTES da ATPV-e — veículo + CPF + vender/comprar. PJ: o CPF tem poder pela empresa?
PF: o CPF é do próprio dono? Se não for, pergunta pela procuração e confere se ela dá poder àquele CPF."""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "corpus"))

from gold import E, P, V, leituras_gold, nome  # noqa: E402
from outorga.engine import Politica  # noqa: E402
from outorga.pipeline import analisar_leituras  # noqa: E402


@pytest.fixture(autouse=True)
def base_veicular(tmp_path, monkeypatch):
    """Base veicular de teste: STRADA da JANGADA (PJ), HILUX do João (PF), CIVIC da Maria (PF)."""
    def item(vid, tipo, nome_, doc):
        v = V[vid]
        return {"placa": v["placa"], "renavam": v["renavam"], "chassi": v["chassi"], "marca_modelo": v["marca_modelo"],
                "proprietario": {"tipo": tipo, "nome": nome_, "documento": doc}}
    base = {"veiculos": [item("STRADA", "PJ", E["JANGADA"]["razao_social"], E["JANGADA"]["cnpj"]),
                         item("HILUX", "PF", nome("JOAO"), P["JOAO"]["cpf"]),
                         item("CIVIC", "PF", nome("MARIA"), P["MARIA"]["cpf"])]}
    arq = tmp_path / "base.json"
    arq.write_text(json.dumps(base, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("OUTORGA_BASE_VEICULAR", str(arq))


def _consulta(vid, quem, papel="vender", **kw):
    return {"veiculo": {"placa": V[vid]["placa"]}, "papel": papel, "cpf": P[quem]["cpf"], "data_venda": "2026-10-16", **kw}


def _poa_joao():  # procuração PARTICULAR (firma reconhecida) de João, em nome próprio, a Kleber: "veículos de propriedade do outorgante"
    return [l for l in leituras_gold("C21") if l.procuracao]


def _quem(res):
    return {frozenset(p["nome"] for p in a["pessoas"]) for a in res["quem_pode"]}


# ------------------------------------------------------------------------------------- pessoa física
def test_pf_o_proprio_dono_assina_sem_documentos():
    res = analisar_leituras([], _consulta("HILUX", "JOAO"), Politica())
    assert res["veredito"] == "PODE" and res["faixa"] == "VERDE" and list(res["lados"]) == ["vendedor"]
    assert "próprio proprietário" in res["resumo"]
    assert res["lados"]["vendedor"]["empresa"]["tipo"] == "PF"


def test_pf_cpf_diferente_sem_procuracao_pergunta_pela_procuracao():
    res = analisar_leituras([], _consulta("HILUX", "KLEBER"), Politica())
    assert res["veredito"] == "INDETERMINADO" and res["faixa"] == "AMARELO"
    assert [p["tipo"] for p in res["pendencias"]] == ["procuracao"]
    assert _quem(res) == {frozenset({"João Batista Andrade"})}


def test_pf_procuracao_do_dono_vale_pelo_codigo_civil_e_o_detran_ce_exige_publica():
    gen = analisar_leituras(_poa_joao(), _consulta("HILUX", "KLEBER"), Politica.por_nome("generica"))
    assert gen["veredito"] == "PODE" and "procurador" in gen["resumo"]
    ce = analisar_leituras(_poa_joao(), _consulta("HILUX", "KLEBER"), Politica())
    assert ce["veredito"] == "NAO_PODE" and ce["faixa"] != "VERDE"


def test_pf_procuracao_de_quem_nao_e_o_dono_nao_serve():
    """O CIVIC é da Maria; a procuração é do João."""
    res = analisar_leituras(_poa_joao(), _consulta("CIVIC", "KLEBER"), Politica.por_nome("generica"))
    assert res["veredito"] == "NAO_PODE"
    codigos = {a["codigo"] for b in res["lados"]["vendedor"]["caminhos_invalidos"] for a in b["achados"]}
    assert "OUTORGANTE_NAO_E_O_TITULAR" in codigos


def test_pf_procuracao_anexada_e_de_outra_pessoa():
    """A procuração anexada é para o Kleber; quem vai assinar é a Maria: pergunta pela procuração DELA (não recusa)."""
    res = analisar_leituras(_poa_joao(), _consulta("HILUX", "MARIA"), Politica.por_nome("generica"))
    assert res["veredito"] == "INDETERMINADO" and res["pendencias"][0]["tipo"] == "procuracao"
    assert "é para Kleber Jorge Matos" in res["resumo"]


# ------------------------------------------------------------------------------------- pessoa jurídica
def test_pj_cpf_do_administrador():
    ls = [l for l in leituras_gold("C04") if not l.crlv]
    res = analisar_leituras(ls, _consulta("STRADA", "FRANCISCO"), Politica())
    assert res["veredito"] == "PODE" and res["faixa"] == "VERDE"
    assert any(a["codigo"] == "TITULARIDADE_BASE" for a in res["achados"])  # dono conferido na base: dispensa o CRLV


def test_pj_cpf_sem_poder_e_sem_procuracao_pergunta_antes_de_recusar():
    ls = [l for l in leituras_gold("C04") if not l.crlv]
    res = analisar_leituras(ls, _consulta("STRADA", "ANABEATRIZ"), Politica())
    assert res["veredito"] == "INDETERMINADO" and res["faixa"] == "AMARELO"
    assert res["pendencias"][0]["tipo"] == "procuracao"


def test_pj_procurador_com_procuracao_da_empresa():
    ls = [l for l in leituras_gold("C16") if not l.crlv]
    res = analisar_leituras(ls, _consulta("STRADA", "PEDRO"), Politica())
    assert res["veredito"] == "PODE"


# ------------------------------------------------------------------------------------- entrada
def test_cpf_invalido_e_veiculo_desconhecido():
    with pytest.raises(ValueError, match="CPF inválido"):
        analisar_leituras([], {"veiculo": {"placa": V["HILUX"]["placa"]}, "papel": "vender", "cpf": "111.111.111-11"})
    with pytest.raises(ValueError, match="proprietário"):
        analisar_leituras([], {"veiculo": {"placa": "ZZZ9Z99"}, "papel": "vender", "cpf": P["JOAO"]["cpf"]})


def test_comprador_pf_por_procurador_sem_procuracao():
    pedido = _consulta("HILUX", "KLEBER", papel="comprar",
                       comprador={"tipo": "PF", "nome": nome("MARIA"), "documento": P["MARIA"]["cpf"]})
    res = analisar_leituras([], pedido, Politica())
    assert list(res["lados"]) == ["comprador"] and res["veredito"] == "INDETERMINADO"
    assert "comprador" in res["pendencias"][0]["mensagem"]


def test_fluxo_da_atpv_e_continua_ignorando_pf_que_assina_por_si():
    """Formato ATPV-e: vendedor PJ verificado; comprador PF sem assinante → não vira um lado."""
    ped = json.loads((RAIZ / "corpus" / "casos" / "C01" / "pedido.json").read_text(encoding="utf-8"))
    res = analisar_leituras(leituras_gold("C01"), ped, Politica())
    assert list(res["lados"]) == ["vendedor"] and res["veredito"] == "PODE"
