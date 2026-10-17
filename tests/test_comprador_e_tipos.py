"""Respostas do chefe (17/10): verificar quem assina VENDENDO OU COMPRANDO, todos os tipos de empresa, ATPV-e digital."""

import copy
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "corpus"))

from gold import E, P, V, leituras_gold, nome  # noqa: E402
from outorga import schemas as sc  # noqa: E402
from outorga.consolidate import LeituraDocumento  # noqa: E402
from outorga.engine import Politica  # noqa: E402
from outorga.extract import atpv_por_regex  # noqa: E402
from outorga.ingest import Documento, _calc_offsets  # noqa: E402
from outorga.pipeline import analisar_leituras, pedido_atpv_de_json  # noqa: E402


def _doc(did: str, texto: str) -> Documento:
    d = Documento(did, f"{did}.pdf", f"{did}.pdf", [texto], did.ljust(64, "0"), "texto")
    d.offsets = _calc_offsets(d.paginas)
    return d


def _pedido(veic: str, data: str, vendedor: dict, comprador: dict, valor=None) -> dict:
    v = V[veic]
    return {"veiculo": {"placa": v["placa"], "renavam": v["renavam"], "chassi": v["chassi"], "descricao": v["marca_modelo"]},
            "data_venda": data, "valor": valor if valor is not None else v["valor"], "vendedor": vendedor, "comprador": comprador}


def _pj(emp: str, *assinantes: str) -> dict:
    return {"tipo": "PJ", "nome": E[emp]["razao_social"], "documento": E[emp]["cnpj"],
            "assinantes": [{"nome": P[a]["nome"], "cpf": P[a]["cpf"]} for a in assinantes]}


PF_VENDEDOR = {"tipo": "PF", "nome": "Rita de Cássia Moreira", "documento": "529.982.247-25", "assinantes": []}


def _sem_crlv(leituras):
    return [l for l in leituras if not l.crlv]


def _quem(res) -> set[frozenset[str]]:
    return {frozenset(p["nome"] for p in a["pessoas"]) for a in res["quem_pode"]}


# ------------------------------------------------------------------------------------- comprador PJ
def test_comprador_pj_administrador_assina():
    ped = _pedido("STRADA", "2026-09-10", PF_VENDEDOR, _pj("SERTAO", "JOAO"))
    res = analisar_leituras(_sem_crlv(leituras_gold("C01")), ped, Politica())
    assert res["lado"] == "comprador" and res["veredito"] == "PODE" and res["faixa"] == "VERDE"
    assert "como comprador" in res["resumo"]


def test_comprador_pj_socio_sem_poder():
    ped = _pedido("HB20", "2026-09-04", PF_VENDEDOR, _pj("JANGADA", "ANABEATRIZ"))
    res = analisar_leituras(_sem_crlv(leituras_gold("C04")), ped, Politica())
    assert res["veredito"] == "NAO_PODE" and _quem(res) == {frozenset({"Francisco Wellington Rocha"})}


def test_procuracao_so_de_venda_nao_serve_para_comprar():
    ped = _pedido("KWID", "2026-09-18", PF_VENDEDOR, _pj("JANGADA", "PEDRO"))
    res = analisar_leituras(_sem_crlv(leituras_gold("C16")), ped, Politica())
    assert res["veredito"] == "NAO_PODE"
    codigos = {a["codigo"] for b in res["caminhos_invalidos"] for a in b["achados"]}
    assert "PODERES_SO_DE_VENDA" in codigos


def test_procuracao_com_poder_de_compra():
    leituras = _sem_crlv(leituras_gold("C16"))
    poa = next(l for l in leituras if l.doc.id == "POA_PEDRO")
    poa.procuracao = copy.deepcopy(poa.procuracao)
    poa.procuracao.poderes.evidencia = ("poderes especiais e expressos para comprar e adquirir veículos em nome da outorgante, "
                                        "assinando a ATPV-e na qualidade de adquirente")
    ped = _pedido("KWID", "2026-09-18", PF_VENDEDOR, _pj("JANGADA", "PEDRO"))
    res = analisar_leituras(leituras, ped, Politica())
    assert res["veredito"] == "PODE"


def test_restricao_de_venda_nao_vale_para_compra():
    """Cariri: 'alienação de veículos acima de R$ 150 mil exige os dois' — não alcança a COMPRA de R$ 215 mil."""
    ped = _pedido("S10", "2026-09-17", PF_VENDEDOR, _pj("CARIRI", "ANTONIO"))
    res = analisar_leituras(_sem_crlv(leituras_gold("C09")), ped, Politica())
    assert res["veredito"] == "PODE"


def test_restricao_de_compra_rotulada_como_alienacao():
    """A IA rotula 'aquisição de veículos acima de R$ 150 mil' como alienação: vale para comprar, não para vender."""
    leituras = leituras_gold("C09")  # CRLV do S10
    cs = next(l for l in leituras if l.doc.id == "CARIRI_CS")
    cs.regras = copy.deepcopy(cs.regras)
    r = cs.regras.regras[1]
    r.evidencia = ("A aquisição de veículos de valor superior a R$ 150.000,00 (cento e cinquenta mil reais) dependerá da "
                   "assinatura conjunta de ambos os administradores")
    compra = analisar_leituras(_sem_crlv(leituras), _pedido("S10", "2026-09-17", PF_VENDEDOR, _pj("CARIRI", "ANTONIO")), Politica())
    assert compra["veredito"] == "NAO_PODE"
    venda = analisar_leituras(leituras, _pedido("S10", "2026-09-17", _pj("CARIRI", "ANTONIO"),
                                                {"tipo": "PF", "nome": "Comprador PF"}), Politica())
    assert venda["veredito"] == "PODE"


def test_dois_lados_pj_faixa_pelo_elo_mais_fraco():
    vendedor = analisar_leituras(leituras_gold("C03") + _sem_crlv(leituras_gold("C01")),
                                 _pedido("SAVEIRO_M", "2026-09-15", _pj("MANDACARU", "CARLOS", "LUCIANA"), _pj("SERTAO", "JOAO")),
                                 Politica())
    assert set(vendedor["lados"]) == {"vendedor", "comprador"}
    assert vendedor["geral"]["veredito"] == "PODE" and vendedor["faixa"] == "VERDE"
    ruim = analisar_leituras(leituras_gold("C03") + _sem_crlv(leituras_gold("C01")),
                             _pedido("SAVEIRO_M", "2026-09-15", _pj("MANDACARU", "CARLOS", "LUCIANA"), _pj("SERTAO", "KLEBER")),
                             Politica())
    assert ruim["lados"]["vendedor"]["faixa"] == "VERDE"
    assert ruim["lados"]["comprador"]["veredito"] == "NAO_PODE"
    assert ruim["veredito"] == "NAO_PODE" and ruim["faixa"] != "VERDE"


# ------------------------------------------------------------------------------------- tipos de empresa
def _cooperativa(rotulo_regra: list[str], modo: str) -> list[LeituraDocumento]:
    cnpj = "33.000.167/0001-01"
    texto_est = ("ESTATUTO SOCIAL DA COOPERATIVA AGROPECUÁRIA DO VALE LTDA. CNPJ 33.000.167/0001-01. Art. 30. A Cooperativa será "
                 "representada pelo Presidente em conjunto com o Tesoureiro. Fortaleza, 10 de março de 2024.")
    est = sc.ExtracaoPartes(
        documento=sc.DadosDocumento(tipo_detalhado="estatuto", data_assinatura="2024-03-10", data_registro="2024-03-20"),
        empresa=sc.DadosEmpresa(razao_social="COOPERATIVA AGROPECUÁRIA DO VALE LTDA.", cnpj=cnpj, tipo_societario="COOPERATIVA",
                                objeto_social="cooperativa agropecuária", comercializa_veiculos=False),
        socios=[], administradores=[], bens_integralizados=[], alteracao=sc.AlteracaoAdministracao(altera_administracao=True))
    regras = sc.ExtracaoRegras(regras=[sc.Regra(
        evidencia="A Cooperativa será representada pelo Presidente em conjunto com o Tesoureiro", clausula="Art. 30",
        expressao_modo="em conjunto", escopo="geral", efeito="autoriza", modo=modo, pessoas=rotulo_regra, cargo=None,
        quantidade_minima=None, combinacoes=[], valor_acima_de=None, valor_ate=None, exige_aprovacao_socios=False,
        quorum_percentual=None, exige_anuencia_de=[])],
        regras_procuracao=sc.RegrasProcuracao(exige_poderes_especificados=False, vedada_para_alienacao=False))
    eleitos = [sc.Eleito(nome=nome(p), cpf=P[p]["cpf"], cargo=c, mandato_descricao="4 anos", mandato_termino="2029-04-30")
               for p, c in (("ROBERTO", "Presidente"), ("SANDRA", "Vice-Presidente"), ("GUSTAVO", "Tesoureiro"))]
    ata = sc.ExtracaoAta(data="2025-04-30", orgao="assembleia_socios", presentes=[], deliberacoes=[sc.Deliberacao(
        evidencia="elegeu o Conselho de Administração", assunto="eleição", tipo="eleicao_administradores", aprovada=True,
        veiculos=[], eleitos=eleitos)])
    return [LeituraDocumento(_doc("ESTATUTO_COOP", texto_est), sc.Classificacao(tipo="estatuto_social", titulo="Estatuto (2024)",
                                                                              data_documento="2024-03-10", confianca=1),
                             partes=est, regras=regras),
            LeituraDocumento(_doc("ATA_AGO", "ATA DA ASSEMBLEIA GERAL ORDINÁRIA. COOPERATIVA AGROPECUÁRIA DO VALE LTDA. "
                                             "CNPJ 33.000.167/0001-01. Fortaleza, 30 de abril de 2025."),
                             sc.Classificacao(tipo="ata_assembleia", titulo="Ata da AGO (2025)", data_documento="2025-04-30",
                                              confianca=1), ata=ata)]


def test_cooperativa_presidente_sozinho_nao_basta():
    coop = {"tipo": "PJ", "nome": "COOPERATIVA AGROPECUÁRIA DO VALE LTDA.", "documento": "33.000.167/0001-01",
            "assinantes": [{"nome": P["ROBERTO"]["nome"], "cpf": P["ROBERTO"]["cpf"]}]}
    res = analisar_leituras(_cooperativa(["Presidente", "Tesoureiro"], "conjunto"),
                            _pedido("HILUX", "2026-09-15", coop, {"tipo": "PF", "nome": "Comprador"}), Politica())
    assert res["veredito"] == "NAO_PODE"
    assert _quem(res) == {frozenset({"Roberto Diniz Câmara", "Gustavo Henrique Teles"})}  # Vice-Presidente não entra


def test_eireli_e_mei_e_sa_omissa():
    leituras = leituras_gold("C31")
    cs = next(l for l in leituras if l.doc.id == "TECH_CS")
    cs.doc = _doc("TECH_CS", "ATO CONSTITUTIVO DE EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA – EIRELI. " + cs.doc.texto)
    res = analisar_leituras(leituras, pedido_atpv_de_json(
        _pedido("CIVIC", "2026-09-12", _pj("TECH", "RAFAEL"), {"tipo": "PF", "nome": "Comprador"})), Politica())
    assert res["veredito"] == "PODE" and any(a["codigo"] == "EIRELI_SLU" for a in res["achados"])
    leituras = leituras_gold("C34")
    req = next(l for l in leituras if l.doc.id == "JPSILVA_REQ")
    req.doc = _doc("JPSILVA_REQ", "CERTIFICADO DA CONDIÇÃO DE MICROEMPREENDEDOR INDIVIDUAL (CCMEI). " + req.doc.texto)
    res = analisar_leituras(leituras, _pedido("CARGO", "2026-09-19", _pj("JPSILVA", "JOSUE"), {"tipo": "PF", "nome": "X"}), Politica())
    assert res["veredito"] == "PODE" and any(a["codigo"] == "MEI_EI" for a in res["achados"])


# ------------------------------------------------------------------------------------- ATPV-e como entrada
ATPV_TXT = """AUTORIZAÇÃO PARA TRANSFERÊNCIA DE PROPRIEDADE DO VEÍCULO — DIGITAL (ATPV-e)
Número da ATPV-e: 2026000123456
Placa: {placa}
RENAVAM: {renavam}
Chassi: {chassi}
Marca / Modelo: {modelo}
Valor declarado da venda: R$ 98.500,00
Data da venda: 10/09/2026
VENDEDOR (ANTIGO PROPRIETÁRIO)
Nome / Razão social: TRANSPORTES SERTÃO VERDE LTDA.
CPF / CNPJ: {cnpj}
COMPRADOR (NOVO PROPRIETÁRIO)
Nome / Razão social: Rita de Cássia Moreira
CPF / CNPJ: 529.982.247-25
ASSINATURAS ELETRÔNICAS: pendentes
"""


def test_atpv_e_preenche_o_pedido():
    v = V["STRADA"]
    doc = _doc("ATPV_E", ATPV_TXT.format(placa=v["placa"], renavam=v["renavam"], chassi=v["chassi"], modelo=v["marca_modelo"],
                                         cnpj=E["SERTAO"]["cnpj"]))
    a = atpv_por_regex(doc)
    assert a and a.vendedor.tipo == "PJ" and a.comprador.tipo == "PF" and a.valor == 98500.0 and a.data == "2026-09-10"
    leituras = leituras_gold("C01") + [LeituraDocumento(doc, sc.Classificacao(tipo="atpv", titulo="ATPV-e", data_documento=None,
                                                                             confianca=1), atpv=a)]
    pedido = {"veiculo": {}, "data_venda": None, "valor": None,
              "vendedor": {"assinantes": [{"nome": P["JOAO"]["nome"], "cpf": P["JOAO"]["cpf"]}]}, "comprador": {}}
    res = analisar_leituras(leituras, pedido, Politica())
    assert res["veredito"] == "PODE" and res["pedido_atpv"]["origem"] == "ATPV-e"
    assert res["pedido_atpv"]["comprador"]["tipo"] == "PF"


def test_clausula_geral_rotulada_como_alienacao_vale_para_comprar():
    """Rodada cega do lote ATPV-e (A01): a IA rotulou 'A administração da sociedade caberá aos sócios ..., que a exercerão
    isoladamente ..., inclusive a venda de bens' como alienacao_bens. A cláusula é a regra geral: vale para comprar."""
    leituras = _sem_crlv(leituras_gold("C01"))
    cs = next(l for l in leituras if l.regras)
    geral = cs.regras.regras[0]
    geral.escopo = "alienacao_bens"
    geral.evidencia = (geral.evidencia + ", com representação ativa e passiva da sociedade, em juízo ou fora dele, "
                       "inclusive a venda de bens da sociedade")
    cs.doc = _doc(cs.doc.id, cs.doc.texto + " " + geral.evidencia)
    res = analisar_leituras(leituras, _pedido("STRADA", "2026-09-10", PF_VENDEDOR, _pj("SERTAO", "JOAO")), Politica())
    assert res["lado"] == "comprador" and res["veredito"] == "PODE" and res["faixa"] == "VERDE", res["motivos_faixa"]


def _associacao(cargo_lido: str | None, pessoas_lidas: list[str]) -> list[LeituraDocumento]:
    """Estatuto que nomeia o cargo ('Compete ao Presidente representar...') + ata que elege a diretoria E o Conselho Fiscal."""
    cnpj = "92.004.472/0001-30"
    texto = ("ESTATUTO SOCIAL DA ASSOCIAÇÃO COMUNITÁRIA DE TESTE. CNPJ 92.004.472/0001-30. Art. 20. Compete ao Presidente "
             "representar a Associação ativa e passivamente, judicial e extrajudicialmente, sozinho. Quixeramobim, 5 de agosto de 2017.")
    est = sc.ExtracaoPartes(
        documento=sc.DadosDocumento(tipo_detalhado="estatuto", data_assinatura="2017-08-05", data_registro="2017-08-21"),
        empresa=sc.DadosEmpresa(razao_social="ASSOCIAÇÃO COMUNITÁRIA DE TESTE", cnpj=cnpj, tipo_societario="OUTRO",
                                objeto_social="assistência social sem fins lucrativos", comercializa_veiculos=False),
        socios=[], administradores=[], bens_integralizados=[], alteracao=sc.AlteracaoAdministracao(altera_administracao=True))
    regras = sc.ExtracaoRegras(regras=[sc.Regra(
        evidencia="Compete ao Presidente representar a Associação ativa e passivamente, judicial e extrajudicialmente, sozinho",
        clausula="Art. 20", expressao_modo="sozinho", escopo="geral", efeito="autoriza", modo="isolado", pessoas=pessoas_lidas,
        cargo=cargo_lido, quantidade_minima=None, combinacoes=[], valor_acima_de=None, valor_ate=None,
        exige_aprovacao_socios=False, quorum_percentual=None, exige_anuencia_de=[])],
        regras_procuracao=sc.RegrasProcuracao(exige_poderes_especificados=False, vedada_para_alienacao=False))
    eleitos = [sc.Eleito(nome=nome(p), cpf=P[p]["cpf"], cargo=c, mandato_descricao="3 anos", mandato_termino="2027-02-16")
               for p, c in (("ROBERTO", "Presidente"), ("SANDRA", "Vice-Presidente"), ("GUSTAVO", "Conselho Fiscal"))]
    ata = sc.ExtracaoAta(data="2024-02-17", orgao="assembleia_socios", presentes=[], deliberacoes=[sc.Deliberacao(
        evidencia="elegeu a Diretoria e o Conselho Fiscal", assunto="eleição", tipo="eleicao_administradores", aprovada=True,
        veiculos=[], eleitos=eleitos)])
    return [LeituraDocumento(_doc("ESTATUTO_ASSOC", texto), sc.Classificacao(tipo="estatuto_social", titulo="Estatuto (2017)",
                                                                           data_documento="2017-08-05", confianca=1),
                             partes=est, regras=regras),
            LeituraDocumento(_doc("ATA_ELEICAO", "ATA DA ASSEMBLEIA GERAL DE ELEIÇÃO. ASSOCIAÇÃO COMUNITÁRIA DE TESTE. "
                                                 "CNPJ 92.004.472/0001-30. A Assembleia elegeu a Diretoria e o Conselho Fiscal. "
                                                 "Quixeramobim, 17 de fevereiro de 2024."),
                             sc.Classificacao(tipo="ata_assembleia", titulo="Ata de eleição (2024)", data_documento="2024-02-17",
                                              confianca=1), ata=ata)]


def test_cargo_nomeado_restringe_regra_lida_como_administradores():
    """Rodada cega (A10): a IA leu 'Compete ao Presidente representar...' como cargo 'administradores' e o Conselho Fiscal
    eleito na ata virou administrador — qualquer um dos 7 assinaria. Só o Presidente pode; Vice e conselheiro fiscal, não."""
    for quem in ("SANDRA", "GUSTAVO"):
        assoc = {"tipo": "PJ", "nome": "ASSOCIAÇÃO COMUNITÁRIA DE TESTE", "documento": "92.004.472/0001-30",
                 "assinantes": [{"nome": P[quem]["nome"], "cpf": P[quem]["cpf"]}]}
        res = analisar_leituras(_associacao("administradores", []),
                                _pedido("HB20", "2026-10-09", PF_VENDEDOR, assoc), Politica())
        assert res["veredito"] == "NAO_PODE" and res["faixa"] != "VERDE", quem
        assert _quem(res) == {frozenset({"Roberto Diniz Câmara"})}


def test_conselho_fiscal_nao_representa_nem_com_regra_generica_sem_cargo_no_texto():
    leituras = _associacao("administradores", [])
    leituras[0].regras.regras[0].evidencia = "A Associação será administrada pela Diretoria eleita, que a representará"
    leituras[0].doc = _doc("ESTATUTO_ASSOC", leituras[0].doc.texto + " " + leituras[0].regras.regras[0].evidencia)
    res = analisar_leituras(leituras, _pedido("HB20", "2026-10-09", PF_VENDEDOR, {
        "tipo": "PJ", "nome": "ASSOCIAÇÃO COMUNITÁRIA DE TESTE", "documento": "92.004.472/0001-30",
        "assinantes": [{"nome": P["GUSTAVO"]["nome"], "cpf": P["GUSTAVO"]["cpf"]}]}), Politica())
    assert res["veredito"] == "NAO_PODE"
    assert all("Gustavo Henrique Teles" not in a for a in _quem(res))


def test_cargo_nomeado_nao_afrouxa_assinatura_conjunta():
    """'representada pelo Diretor-Presidente em conjunto com outro Diretor' lido como 2 diretores: a restrição por cargo
    não pode reduzir a regra ao Diretor-Presidente sozinho."""
    leituras = _associacao("diretores", [])
    r = leituras[0].regras.regras[0]
    r.evidencia = "A Associação será representada pelo Presidente em conjunto com outro membro da Diretoria"
    leituras[0].doc = _doc("ESTATUTO_ASSOC", leituras[0].doc.texto + " " + r.evidencia)
    r.modo, r.quantidade_minima, r.expressao_modo = "quantidade_minima", 2, "em conjunto"
    res = analisar_leituras(leituras, _pedido("HB20", "2026-10-09", PF_VENDEDOR, {
        "tipo": "PJ", "nome": "ASSOCIAÇÃO COMUNITÁRIA DE TESTE", "documento": "92.004.472/0001-30",
        "assinantes": [{"nome": P["ROBERTO"]["nome"], "cpf": P["ROBERTO"]["cpf"]}]}), Politica())
    assert res["veredito"] != "PODE" and res["faixa"] != "VERDE"


def test_substituto_na_ausencia_do_titular_vai_para_revisao():
    """'Compete ao Presidente representar...; nas suas ausências e impedimentos, será substituído pelo Vice-Presidente',
    lido como 'Presidente ou Vice-Presidente, isoladamente'. A ausência não é verificável: Vice assinando → revisão humana;
    Presidente assinando → aceite."""
    def rodar(quem):
        leituras = _associacao(None, ["Presidente", "Vice-Presidente"])
        ev = ("Compete ao Presidente representar a Associação ativa e passivamente; nas suas ausências e impedimentos, "
              "será substituído pelo Vice-Presidente")
        leituras[0].regras.regras[0].evidencia = ev
        leituras[0].doc = _doc("ESTATUTO_ASSOC", leituras[0].doc.texto + " " + ev)
        return analisar_leituras(leituras, _pedido("HB20", "2026-10-09", PF_VENDEDOR, {
            "tipo": "PJ", "nome": "ASSOCIAÇÃO COMUNITÁRIA DE TESTE", "documento": "92.004.472/0001-30",
            "assinantes": [{"nome": P[quem]["nome"], "cpf": P[quem]["cpf"]}]}), Politica())
    vice = rodar("SANDRA")
    assert vice["faixa"] == "AMARELO" and any(a["codigo"] == "REPRESENTACAO_POR_SUBSTITUTO" for a in vice["achados"])
    pres = rodar("ROBERTO")
    assert pres["veredito"] == "PODE" and pres["faixa"] == "VERDE", pres["motivos_faixa"]
