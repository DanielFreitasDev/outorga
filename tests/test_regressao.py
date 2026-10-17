"""Regressões de lacunas encontradas em revisão de código (antes do lote de validação independente)."""

import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "corpus"))

from gold import P, leituras_gold, nome  # noqa: E402
from outorga import lexicon as lx  # noqa: E402
from outorga import schemas as sc  # noqa: E402
from outorga.consolidate import LeituraDocumento  # noqa: E402
from outorga.engine import Politica  # noqa: E402
from outorga.ingest import Documento, _calc_offsets  # noqa: E402
from outorga.pipeline import analisar_leituras, pedido_de_json  # noqa: E402


def _pedido(caso: str, assinantes: list[str] | None = None):
    p = json.loads((RAIZ / "corpus" / "casos" / caso / "pedido.json").read_text(encoding="utf-8"))
    if assinantes:
        p["assinantes"] = [{"nome": P[a]["nome"], "cpf": P[a]["cpf"]} for a in assinantes]
    return pedido_de_json(p)


def _doc(did: str, texto: str) -> Documento:
    d = Documento(did, f"{did}.pdf", f"{did}.pdf", [texto], "x" * 64, "texto")
    d.offsets = _calc_offsets(d.paginas)
    return d


def _quem(res) -> set[frozenset[str]]:
    return {frozenset(p["nome"] for p in a["pessoas"]) for a in res["quem_pode"]}


def test_anuencia_em_regra_so_de_condicao():
    """'Venda de veículos depende da anuência da sócia X' (sem dizer quem assina) também restringe."""
    leituras = leituras_gold("C01")
    l = next(x for x in leituras if x.doc.id == "SERTAO_CS")
    l.regras = copy.deepcopy(l.regras)
    l.regras.regras.append(sc.Regra(
        evidencia="A venda de veículos dependerá da anuência da sócia MARIA CLARA FONTENELE.", clausula=None,
        expressao_modo=None, escopo="alienacao_veiculos", veiculo=None, efeito="restringe", modo="nao_especificado",
        pessoas=[], cargo=None, quantidade_minima=None, combinacoes=[], valor_acima_de=None, valor_ate=None,
        exige_aprovacao_socios=False, quorum_percentual=None, exige_anuencia_de=[nome("MARIA")]))
    res = analisar_leituras(leituras, _pedido("C01"), Politica())
    assert res["veredito"] == "NAO_PODE" and res["faixa"] != "VERDE"
    assert _quem(res) == {frozenset({"Maria Clara Fontenele"})}


def test_revogacao_generica_por_outorgado():
    leituras = leituras_gold("C16")
    texto = ("ESCRITURA PÚBLICA DE REVOGAÇÃO. A outorgante revoga todas as procurações anteriormente outorgadas a "
             "PEDRO HENRIQUE LIMA. Caucaia, 1º de maio de 2026.")
    rev = sc.ExtracaoRevogacao(
        evidencia="revoga todas as procurações anteriormente outorgadas a PEDRO HENRIQUE LIMA", forma="publica",
        data="2026-05-01", revogante=sc.Outorgante(evidencia="A outorgante", tipo="PJ", nome="LOCADORA JANGADA LTDA.",
                                                    documento=None, representantes=[], age_em_nome_da_empresa=False),
        procuracao_revogada=sc.RefProcuracao(data=None, cartorio=None, livro=None, folhas=None, outorgante_nome=None,
                                             outorgado_nome=nome("PEDRO")))
    cl = sc.Classificacao(tipo="revogacao_procuracao", titulo="Revogação genérica", data_documento="2026-05-01", confianca=1)
    leituras.append(LeituraDocumento(_doc("REV_GEN", texto), cl, revogacao=rev))
    res = analisar_leituras(leituras, _pedido("C16"), Politica())
    assert res["veredito"] == "NAO_PODE"
    assert frozenset({"Pedro Henrique Lima"}) not in _quem(res)


def test_revogacao_embutida_em_outro_documento():
    leituras = leituras_gold("C16")
    texto = "ATA DE REUNIÃO DE SÓCIOS. Ficam revogadas todas as procurações outorgadas pela sociedade. Caucaia, 1º de junho de 2026."
    cl = sc.Classificacao(tipo="outro", titulo="Ata (2026)", data_documento="2026-06-01", confianca=1)
    leituras.append(LeituraDocumento(_doc("ATA_REV", texto), cl))
    res = analisar_leituras(leituras, _pedido("C16"), Politica())
    assert res["veredito"] == "NAO_PODE"


def test_substabelecimento_em_cadeia_vai_para_revisao():
    leituras = leituras_gold("C23")
    texto = ("SUBSTABELECIMENTO. ANA PAULA BASTOS substabelece, com reserva, a KLEBER JORGE MATOS os poderes que recebeu. "
             "Caucaia, 20 de agosto de 2026.")
    sub2 = sc.ExtracaoSubstabelecimento(
        evidencia="substabelece, com reserva, a KLEBER JORGE MATOS", forma="publica", data="2026-08-20",
        firma_reconhecida=None, procuracao_origem=sc.RefProcuracao(data="2026-08-03", cartorio=None, livro=None, folhas=None,
                                                                    outorgante_nome=None, outorgado_nome=nome("ANAPAULA")),
        substabelecente=sc.PessoaRef(nome=nome("ANAPAULA"), cpf=P["ANAPAULA"]["cpf"]),
        substabelecidos=[sc.PessoaRef(nome=nome("KLEBER"), cpf=P["KLEBER"]["cpf"])], reserva="com_reserva",
        todos_os_poderes=True, alienar_veiculos=True)
    cl = sc.Classificacao(tipo="substabelecimento", titulo="Substabelecimento (2º nível)", data_documento="2026-08-20", confianca=1)
    leituras.append(LeituraDocumento(_doc("SUB2", texto), cl, substabelecimento=sub2))
    res = analisar_leituras(leituras, _pedido("C23", ["KLEBER"]), Politica())
    assert res["veredito"] == "PODE" and res["faixa"] == "AMARELO"
    codigos = {a["codigo"] for a in res["caminho_escolhido"]["achados"]}
    assert "SUBSTABELECIMENTO_EM_CADEIA" in codigos


@pytest.mark.parametrize("texto, n", [
    ("Ficam revogadas todas as procurações outorgadas pela sociedade.", 1),
    ("revogando expressamente a procuração lavrada no livro 312", 1),
    ("As procurações poderão ser revogadas a qualquer tempo.", 0),
    ("válida por prazo indeterminado, até revogação expressa", 0),
    ("O presente mandato é irrevogável.", 0),
])
def test_deteccao_de_revogacao_no_texto(texto, n):
    assert len(lx.revogacoes_no_texto(texto)) == n


def test_consulta_sem_assinantes():
    p = json.loads((RAIZ / "corpus" / "casos" / "C16" / "pedido.json").read_text(encoding="utf-8"))
    p["assinantes"] = []
    res = analisar_leituras(leituras_gold("C16"), pedido_de_json(p), Politica())
    assert res["veredito"] == "INDETERMINADO" and res["faixa"] == "AMARELO"
    assert res["resumo"].startswith("Consulta") and len(res["quem_pode"]) == 2


# ---------------------------------------------------------------- lições da validação independente (I02, I05, I06, I07)
def test_ata_unanimidade_dos_presentes_nao_e_cem_por_cento():
    """I06: 'aprovada por unanimidade dos presentes' com presentes abaixo do quórum = não pode (fato negativo)."""
    leituras = leituras_gold("C12")
    ata = next(x for x in leituras if x.doc.id == "CAMOCIM_ATA")
    ata.ata = copy.deepcopy(ata.ata)
    ata.ata.presentes = ata.ata.presentes[:1]                    # só VALDIR (40%) presente
    ata.ata.deliberacoes[0].percentual_favoravel = 100.0          # leitura ingênua: "unanimidade"
    res = analisar_leituras(leituras, _pedido("C12"), Politica())
    assert res["veredito"] == "NAO_PODE" and res["faixa"] != "VERDE"
    assert res["quem_pode"] == []


def test_classes_de_administradores_vao_para_revisao():
    """I02: 'um Administrador A e um Administrador B' sem combinação explícita por grupos nunca é aceite automático."""
    leituras = leituras_gold("C03")
    l = next(x for x in leituras if x.doc.id == "MANDACARU_CS")
    l.regras = copy.deepcopy(l.regras)
    for r in l.regras.regras:
        r.evidencia = "somente obrigarão a sociedade se praticados em conjunto por um Administrador A e um Administrador B"
    res = analisar_leituras(leituras, _pedido("C03"), Politica())
    assert res["faixa"] == "AMARELO"


def test_regra_antiga_de_quem_saiu_nao_vence_a_nova():
    """I05: contrato antigo (veículos → Joaquim) x alteração (bens móveis → Lúcia): vale a administração nova."""
    leituras = leituras_gold("C28")
    cs = next(x for x in leituras if x.doc.id == "CHAPADA_CS")
    alt = next(x for x in leituras if x.doc.id == "CHAPADA_ALT1")
    cs.regras = copy.deepcopy(cs.regras)
    alt.regras = copy.deepcopy(alt.regras)
    cs.regras.regras[0].escopo = "alienacao_veiculos"
    alt.regras.regras[0].escopo = "alienacao_bens_moveis"
    res = analisar_leituras(leituras, _pedido("C28", ["LUCIA"]), Politica())
    assert res["veredito"] == "PODE"
    assert frozenset({"Lúcia Helena Brito"}) in _quem(res)


def test_lacuna_de_alteracoes_torna_outorga_incerta():
    """I07: quem outorgou não aparece como administrador nos atos apresentados, mas faltam alterações intermediárias."""
    leituras = leituras_gold("C16")
    poa = next(x for x in leituras if x.doc.id == "POA_PEDRO")
    poa.procuracao = copy.deepcopy(poa.procuracao)
    poa.procuracao.outorgante.representantes = [sc.PessoaRef(nome=nome("RAIMUNDO"), cpf=P["RAIMUNDO"]["cpf"])]
    cs = next(x for x in leituras if x.doc.id == "JANGADA_CS")
    consolidacao = copy.deepcopy(cs)
    consolidacao.partes = copy.deepcopy(cs.partes)
    consolidacao.partes.documento.tipo_detalhado = "alteracao_e_consolidacao"
    consolidacao.partes.documento.numero_alteracao = 5
    consolidacao.partes.documento.data_assinatura = "2026-05-02"
    consolidacao.partes.documento.data_registro = "2026-05-15"
    consolidacao.doc = _doc("QUINTA_ALT", "QUINTA ALTERAÇÃO E CONSOLIDAÇÃO. " + cs.doc.texto)
    consolidacao.classificacao = sc.Classificacao(tipo="contrato_consolidado", titulo="Quinta Alteração (2026)",
                                                  data_documento="2026-05-02", confianca=1)
    leituras.append(consolidacao)
    res = analisar_leituras(leituras, _pedido("C16"), Politica())
    assert res["veredito"] == "INDETERMINADO" and res["faixa"] == "AMARELO"


def test_classes_lexico():
    assert lx.menciona_classes("em conjunto por um Administrador A e um Administrador B")
    assert not lx.menciona_classes("ao administrador a quem compete representar a sociedade")
    assert lx.alteracoes_citadas("nos termos da Terceira Alteração Contratual") == {3}
