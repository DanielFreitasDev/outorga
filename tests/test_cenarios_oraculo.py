"""Os 38 cenários jurídicos com leitura perfeita (gabarito): o motor deve acertar todos, nas duas políticas."""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "corpus"))

from gold import SPEC, leituras_gold  # noqa: E402
from outorga.avaliacao import comparar  # noqa: E402
from outorga.engine import Politica  # noqa: E402
from outorga.pipeline import analisar_leituras, pedido_de_json  # noqa: E402

CASOS = [c["id"] for c in SPEC["casos"] if not c.get("ocr")]  # OCR fica no teste lento


@pytest.mark.parametrize("politica", ["ce", "generica"])
@pytest.mark.parametrize("caso", CASOS)
def test_cenario(caso, politica):
    pasta = RAIZ / "corpus" / "casos" / caso
    gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
    pedido = pedido_de_json(json.loads((pasta / "pedido.json").read_text(encoding="utf-8")))
    pol = Politica.por_nome(politica)
    res = analisar_leituras(leituras_gold(caso), pedido, pol)
    cmp = comparar(res, gab, pol)
    assert not cmp["erro_perigoso"], res["resumo"]
    assert cmp["veredito_ok"], f"{res['veredito']}: {res['resumo']}"
    assert cmp["faixa_ok"], f"{res['faixa']} ({res['motivos_faixa']})"
    assert cmp["conjuntos_ok"] is not False, [a["pessoas"] for a in res["quem_pode"]]
    c = res["comprovacao_poderes"]
    assert c["norma"].startswith("Resolução CONTRAN nº 1.027/2026")
    assert c["outorgante"]["cnpj"] and c["outorgado"]


def test_sem_contrato_social_vai_para_revisao():
    """Procuração da empresa sem o contrato social: não dá para conferir quem outorgou → nunca aceite automático."""
    pasta = RAIZ / "corpus" / "casos" / "C16"
    pedido = pedido_de_json(json.loads((pasta / "pedido.json").read_text(encoding="utf-8")))
    leituras = [l for l in leituras_gold("C16") if l.doc.id != "JANGADA_CS"]
    res = analisar_leituras(leituras, pedido, Politica())
    assert res["faixa"] == "AMARELO"
    codigos = {a["codigo"] for a in res["achados"]} | {a["codigo"] for a in (res["caminho_escolhido"] or {}).get("achados", [])}
    assert {"SEM_ATO_CONSTITUTIVO", "PODERES_DO_OUTORGANTE_NAO_VERIFICADOS"} <= codigos


def test_cnpj_do_vendedor_diferente_bloqueia():
    pasta = RAIZ / "corpus" / "casos" / "C01"
    p = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
    p["vendedor"]["cnpj"] = "33.000.167/0001-01"
    res = analisar_leituras(leituras_gold("C01"), pedido_de_json(p), Politica())
    assert res["veredito"] == "NAO_PODE" and res["faixa"] != "VERDE"


# ---------------------------------------------------------------- lote ATPV-e: vendendo ou comprando, todos os tipos de PJ
CASOS_ATPV = [c["id"] for c in SPEC.get("casos_atpv", []) if (RAIZ / "corpus" / "casos" / c["id"] / "gabarito.json").exists()]


@pytest.mark.parametrize("politica", ["ce", "generica"])
@pytest.mark.parametrize("caso", CASOS_ATPV)
def test_cenario_atpv(caso, politica):
    """O pedido traz só quem assina; veículo, partes, valor e data vêm da ATPV-e. Cada lado PJ confere com o gabarito."""
    pasta = RAIZ / "corpus" / "casos" / caso
    gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
    pedido = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
    pol = Politica.por_nome(politica)
    res = analisar_leituras(leituras_gold(caso), pedido, pol)
    cmp = comparar(res, gab, pol)
    assert not cmp["erro_perigoso"], res["resumo"]
    assert cmp["veredito_ok"], f"{res['veredito']} {cmp.get('lados_ok')}: {res['resumo']}"
    assert cmp["faixa_ok"], f"{res['faixa']} ({res['motivos_faixa']})"
    assert cmp["conjuntos_ok"] is not False, {k: [a["pessoas"] for a in r["quem_pode"]] for k, r in res["lados"].items()}
    assert set(res["lados"]) == set(gab["esperado_lados"])
    assert res["pedido_atpv"]["origem"] == "ATPV-e" and res["pedido_atpv"]["veiculo"]["placa"]


@pytest.mark.parametrize("caso", CASOS_ATPV)
def test_leitor_de_atpv_por_regras(caso):
    """A ATPV-e simulada de cada caso é lida por regras (sem IA) exatamente como no gabarito, assinaturas inclusive."""
    from gold import gold_atpv
    from outorga.extract import atpv_por_regex
    from outorga.ingest import carregar
    c = next(c for c in SPEC["casos_atpv"] if c["id"] == caso)
    lido = atpv_por_regex(carregar(RAIZ / "corpus" / "casos" / caso / "docs" / "ATPV-e.pdf", "ATPV-e"))
    assert lido is not None and lido.model_dump() == gold_atpv(c).model_dump()


# ---------------------------------------------------------------- lote consulta por CPF (antes da ATPV-e; pessoa física)
CASOS_PF = [c["id"] for c in SPEC.get("casos_pf", []) if (RAIZ / "corpus" / "casos" / c["id"] / "gabarito.json").exists()]


@pytest.mark.parametrize("politica", ["ce", "generica"])
@pytest.mark.parametrize("caso", CASOS_PF)
def test_cenario_consulta_cpf(caso, politica, monkeypatch):
    """Só veículo + CPF + papel: o dono vem da base veicular simulada (gerada do próprio corpus)."""
    import subprocess
    base = RAIZ / "corpus" / "base_veicular.json"
    if not base.exists():
        subprocess.run([sys.executable, str(RAIZ / "corpus" / "gerar_base_veicular.py")], check=True)
    monkeypatch.setenv("OUTORGA_BASE_VEICULAR", str(base))
    pasta = RAIZ / "corpus" / "casos" / caso
    gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
    pedido = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
    pol = Politica.por_nome(politica)
    res = analisar_leituras(leituras_gold(caso), pedido, pol)
    cmp = comparar(res, gab, pol)
    assert not cmp["erro_perigoso"], res["resumo"]
    assert cmp["veredito_ok"], f"{res['veredito']} {cmp.get('lados_ok')}: {res['resumo']}"
    assert cmp["faixa_ok"], f"{res['faixa']} ({res['motivos_faixa']})"
    assert cmp["conjuntos_ok"] is not False, {k: [a["pessoas"] for a in r["quem_pode"]] for k, r in res["lados"].items()}
