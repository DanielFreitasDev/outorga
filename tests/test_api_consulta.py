"""API: consulta por CPF antes da ATPV-e (documentos opcionais) e consulta do dono pela placa."""

import json
import sys
import time
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "corpus"))

from gold import P, V, nome  # noqa: E402


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from outorga import store
    import outorga.api as api

    monkeypatch.setattr(store, "DADOS", tmp_path / "dados")
    monkeypatch.setattr(store, "_con", None)
    v = V["HILUX"]
    base = tmp_path / "base.json"
    base.write_text(json.dumps({"veiculos": [{"placa": v["placa"], "renavam": v["renavam"], "marca_modelo": v["marca_modelo"],
                                              "proprietario": {"tipo": "PF", "nome": nome("JOAO"), "documento": P["JOAO"]["cpf"]}}]}),
                    encoding="utf-8")
    monkeypatch.setenv("OUTORGA_BASE_VEICULAR", str(base))
    return TestClient(api.app)


def _esperar(c, aid):
    for _ in range(100):
        a = c.get(f"/api/analises/{aid}").json()
        if a["status"] != "processando":
            return a
        time.sleep(0.05)
    raise AssertionError("análise não terminou")


def test_dono_pela_placa(cliente):
    r = cliente.get("/api/veiculo", params={"placa": V["HILUX"]["placa"]})
    assert r.status_code == 200 and r.json()["proprietario"]["tipo"] == "PF"
    assert cliente.get("/api/veiculo", params={"placa": "ZZZ9Z99"}).status_code == 404


def test_consulta_sem_documentos(cliente):
    pedido = {"veiculo": {"placa": V["HILUX"]["placa"]}, "papel": "vender", "cpf": P["JOAO"]["cpf"], "data_venda": "2026-10-16"}
    r = cliente.post("/api/analises", data={"pedido": json.dumps(pedido)})
    assert r.status_code == 200
    a = _esperar(cliente, r.json()["id"])
    assert a["status"] == "concluida" and a["resultado"]["faixa"] == "VERDE"
    outro = {**pedido, "cpf": P["KLEBER"]["cpf"]}
    a = _esperar(cliente, cliente.post("/api/analises", data={"pedido": json.dumps(outro)}).json()["id"])
    assert a["resultado"]["veredito"] == "INDETERMINADO" and a["resultado"]["pendencias"][0]["tipo"] == "procuracao"


def test_consulta_com_cpf_invalido_e_recusada_na_entrada(cliente):
    pedido = {"veiculo": {"placa": V["HILUX"]["placa"]}, "papel": "vender", "cpf": "123.456.789-00"}
    assert cliente.post("/api/analises", data={"pedido": json.dumps(pedido)}).status_code == 422


def test_simulacao_sobre_consulta_por_cpf(cliente):
    """'E se…?' numa consulta por CPF: troca quem assina sem perder o dono da base veicular."""
    pedido = {"veiculo": {"placa": V["HILUX"]["placa"]}, "papel": "vender", "cpf": P["KLEBER"]["cpf"], "data_venda": "2026-10-16"}
    a = _esperar(cliente, cliente.post("/api/analises", data={"pedido": json.dumps(pedido)}).json()["id"])
    assert a["resultado"]["veredito"] == "INDETERMINADO"
    r = cliente.post(f"/api/analises/{a['id']}/simular", json={"assinantes": [{"nome": nome("JOAO"), "cpf": P["JOAO"]["cpf"]}]})
    assert r.status_code == 200, r.text
    sim = r.json()
    assert sim["veredito"] == "PODE" and list(sim["lados"]) == ["vendedor"]


def test_modo_demonstracao_protege_a_instalacao_publica(cliente, monkeypatch):
    """Demonstração pública: sem envio de documentos, sem mudar política/revisão, histórico sem consultas de visitantes."""
    import outorga.api as api
    monkeypatch.setattr(api, "MODO_DEMO", True)
    pedido = {"veiculo": {"placa": V["HILUX"]["placa"]}, "papel": "vender", "cpf": P["JOAO"]["cpf"], "data_venda": "2026-10-16"}
    a = _esperar(cliente, cliente.post("/api/analises", data={"pedido": json.dumps(pedido)}).json()["id"])  # consulta sem documento: pode
    assert a["status"] == "concluida"
    assert cliente.get("/api/analises").json() == []  # a consulta do visitante não aparece no histórico público
    com_arquivo = cliente.post("/api/analises", data={"pedido": json.dumps(pedido)}, files={"arquivos": ("x.pdf", b"%PDF-1.4", "application/pdf")})
    assert com_arquivo.status_code == 403
    assert cliente.put("/api/politica", json={"perfil": "generica"}).status_code == 403
    assert cliente.post(f"/api/analises/{a['id']}/revisao", json={"decisao": "aprovar"}).status_code == 403
    assert cliente.get("/api/saude").json()["demonstracao"] is True


def test_exemplos_de_consulta(cliente):
    ex = cliente.get("/api/consulta/exemplos").json()
    assert len(ex) == 15 and {e["papel"] for e in ex} == {"vender", "comprar"} and any(not e["documentos"] for e in ex)
