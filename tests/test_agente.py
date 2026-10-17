"""Modo agente: pasta vigiada → parecer, resumo, auditoria e arquivamento (sem IA: a leitura vem do gabarito)."""

import json
import shutil
import sys
import zipfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "corpus"))

from gold import leituras_gold  # noqa: E402
from outorga import agente, store  # noqa: E402


class ProvedorFalso:
    nome, modelo = "falso", "gabarito"

    def disponivel(self) -> bool:
        return True


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DADOS", tmp_path / "dados")
    monkeypatch.setattr(store, "_con", None)
    monkeypatch.setattr(agente, "provedor_padrao", lambda: ProvedorFalso())
    lidos = {}

    def ler(arquivos, prov, amostras, progresso):  # devolve o gabarito do caso cujos PDFs estão na pasta
        caso = next(c for c in ("C01", "C02") if (RAIZ / "corpus" / "casos" / c / "docs" / arquivos[0].name).exists())
        lidos["caso"] = caso
        return leituras_gold(caso)

    monkeypatch.setattr(agente, "ler_arquivos", ler)
    entrada, saida = tmp_path / "entrada", tmp_path / "saida"
    return agente.Agente(entrada, saida, intervalo=0, estabilidade=0), entrada, saida


def _montar(pasta: Path, caso: str, pronto: bool = True) -> None:
    pasta.mkdir(parents=True)
    for f in (RAIZ / "corpus" / "casos" / caso / "docs").iterdir():
        shutil.copy(f, pasta / f.name)
    shutil.copy(RAIZ / "corpus" / "casos" / caso / "pedido.json", pasta / "pedido.json")
    if pronto:
        (pasta / agente.MARCADOR).touch()


def test_agente_processa_pedido_e_arquiva(ambiente):
    ag, entrada, saida = ambiente
    _montar(entrada / "pedido-001", "C01")
    assert ag.rodar(uma_vez=True) == 0
    out = saida / "pedido-001"
    res = json.loads((out / "resultado.json").read_text(encoding="utf-8"))
    assert res["faixa"] == "VERDE" and res["veredito"] == "PODE" and res["auditoria"]["hash"]
    assert (out / "parecer.pdf").read_bytes()[:4] == b"%PDF"
    resumo = (out / "resumo.txt").read_text(encoding="utf-8")
    assert "ACEITO" in resumo and "Quem pode assinar" in resumo
    assert (entrada / "processados" / "pedido-001" / "pedido.json").exists() and not (entrada / "pedido-001").exists()
    assert store.obter_analise(res["id"])["origem"] == "agente"
    assert store.verificar_cadeia()["integra"]
    status = json.loads((saida / "agente_status.json").read_text(encoding="utf-8"))
    assert status["processados"] == 1 and status["erros"] == 0


def test_agente_recusa_e_pasta_sem_documentos_vai_para_erro(ambiente):
    ag, entrada, saida = ambiente
    _montar(entrada / "recusa", "C02")
    (entrada / "vazia").mkdir()
    (entrada / "vazia" / "pedido.json").write_text("{}", encoding="utf-8")
    (entrada / "vazia" / agente.MARCADOR).touch()
    ag.rodar(uma_vez=True)
    assert json.loads((saida / "recusa" / "resultado.json").read_text(encoding="utf-8"))["faixa"] == "VERMELHO"
    erro = (entrada / "com_erro" / "vazia" / "erro.txt").read_text(encoding="utf-8")
    assert "nenhum documento" in erro


def test_agente_espera_a_copia_terminar(ambiente):
    ag, entrada, saida = ambiente
    ag.estabilidade = 3600
    _montar(entrada / "copiando", "C01", pronto=False)
    assert ag.pendentes() == []          # 1ª varredura: registra o estado
    assert ag.pendentes() == []          # ainda dentro da janela de estabilidade
    (entrada / "copiando" / agente.MARCADOR).touch()
    assert [p.name for p in ag.pendentes()] == ["copiando"]


def test_agente_aceita_zip(ambiente, tmp_path):
    ag, entrada, saida = ambiente
    origem = tmp_path / "origem"
    _montar(origem, "C01", pronto=False)
    entrada.mkdir(exist_ok=True)
    with zipfile.ZipFile(entrada / "lote-7.zip", "w") as z:
        for f in origem.iterdir():
            z.write(f, f.name)
    ag.rodar(uma_vez=True)
    assert (saida / "lote-7" / "parecer.pdf").exists()
    assert not (entrada / "lote-7.zip").exists()


def test_agente_aguarda_quando_a_ia_esta_fora(ambiente, monkeypatch):
    ag, entrada, saida = ambiente

    class Fora(ProvedorFalso):
        def disponivel(self) -> bool:
            return False

    monkeypatch.setattr(agente, "provedor_padrao", lambda: Fora())
    _montar(entrada / "pedido-002", "C01")
    assert ag.rodar(uma_vez=True) == 2
    assert (entrada / "pedido-002").exists()  # continua na fila


def test_agente_consulta_por_cpf_sem_documentos(ambiente, monkeypatch, tmp_path):
    """pedido.json no formato da consulta por CPF: o próprio dono pessoa física assinando não precisa de documento."""
    import json as _json
    from gold import P, V, nome
    ag, entrada, saida = ambiente
    base = tmp_path / "base.json"
    v = V["HILUX"]
    base.write_text(_json.dumps({"veiculos": [{"placa": v["placa"], "renavam": v["renavam"], "marca_modelo": v["marca_modelo"],
                                               "proprietario": {"tipo": "PF", "nome": nome("JOAO"), "documento": P["JOAO"]["cpf"]}}]}),
                    encoding="utf-8")
    monkeypatch.setenv("OUTORGA_BASE_VEICULAR", str(base))
    pasta = entrada / "consulta-joao"
    pasta.mkdir(parents=True)
    (pasta / "pedido.json").write_text(_json.dumps({"veiculo": {"placa": v["placa"]}, "papel": "vender",
                                                    "cpf": P["JOAO"]["cpf"], "data_venda": "2026-10-16"}), encoding="utf-8")
    (pasta / agente.MARCADOR).touch()
    ag.rodar(uma_vez=True)
    res = _json.loads((saida / "consulta-joao" / "resultado.json").read_text(encoding="utf-8"))
    assert res["faixa"] == "VERDE" and "próprio proprietário" in res["resumo"]
