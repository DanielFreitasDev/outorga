"""Especificação do corpus sintético de avaliação (fatos + gabarito).

Gera `cenarios.json` (lido pelo avaliador e pelos redatores dos documentos) e `CENARIOS.md`.
Todos os nomes, empresas, cartórios e números são FICTÍCIOS (CPFs/CNPJs/RENAVAMs têm dígitos
verificadores válidos apenas para exercitar os validadores).

    uv run python corpus/spec.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from outorga.ids import gerar_chassi, gerar_cnpj, gerar_cpf, gerar_placa, gerar_renavam

AQUI = Path(__file__).parent
rng = random.Random(2026)

# ------------------------------------------------------------------------------------- pessoas
_P = [
    # id, nome, nacionalidade/gênero (m/f), estado civil, profissão, cidade
    ("JOAO", "João Batista Andrade", "m", "casado", "empresário", "Fortaleza/CE"),
    ("MARIA", "Maria Clara Fontenele", "f", "divorciada", "administradora de empresas", "Fortaleza/CE"),
    ("CARLOS", "Carlos Eduardo Bezerra", "m", "casado", "engenheiro civil", "Fortaleza/CE"),
    ("LUCIANA", "Luciana Moura Sampaio", "f", "solteira", "arquiteta", "Fortaleza/CE"),
    ("FRANCISCO", "Francisco Wellington Rocha", "m", "casado", "empresário", "Caucaia/CE"),
    ("ANABEATRIZ", "Ana Beatriz Holanda", "f", "casada", "contadora", "Fortaleza/CE"),
    ("RAIMUNDO", "Raimundo Nonato Pires", "m", "viúvo", "comerciante", "Maranguape/CE"),
    ("ROBERTO", "Roberto Diniz Câmara", "m", "casado", "empresário", "Fortaleza/CE"),
    ("SANDRA", "Sandra Helena Pontes", "f", "casada", "empresária", "Fortaleza/CE"),
    ("GUSTAVO", "Gustavo Henrique Teles", "m", "solteiro", "administrador de empresas", "Maracanaú/CE"),
    ("PAULA", "Paula Regina Saraiva", "f", "casada", "cirurgiã-dentista", "Fortaleza/CE"),
    ("ITALO", "Ítalo Menezes Cavalcante", "m", "solteiro", "cirurgião-dentista", "Fortaleza/CE"),
    ("ANTONIO", "Antônio Cícero Lobo", "m", "casado", "agropecuarista", "Juazeiro do Norte/CE"),
    ("JOSEFA", "Josefa Alencar Lobo", "f", "casada", "agropecuarista", "Juazeiro do Norte/CE"),
    ("VALDIR", "Valdir Cunha Teixeira", "m", "casado", "empresário", "Camocim/CE"),
    ("MARCIA", "Márcia Regina Sá", "f", "solteira", "empresária", "Camocim/CE"),
    ("OSVALDO", "Osvaldo Lima Prado", "m", "casado", "empresário", "Camocim/CE"),
    ("MARCOS", "Marcos Antônio Girão", "m", "casado", "empresário", "Fortaleza/CE"),
    ("LEONARDO", "Leonardo Sales Pinheiro", "m", "solteiro", "empresário", "Eusébio/CE"),
    ("RAFAEL", "Rafael Nogueira Brito", "m", "solteiro", "analista de sistemas", "Fortaleza/CE"),
    ("JOAQUIM", "Joaquim Moreira Brito", "m", "casado", "panificador", "Crato/CE"),
    ("LUCIA", "Lúcia Helena Brito", "f", "casada", "empresária", "Crato/CE"),
    ("DAVI", "Davi Brito Alencar", "m", "solteiro", "gerente comercial", "Crato/CE"),
    ("HELIO", "Hélio Bandeira Forte", "m", "casado", "empresário", "Russas/CE"),
    ("REGINA", "Regina Célia Forte", "f", "casada", "empresária", "Russas/CE"),
    ("WAGNER", "Wagner Pontes Aguiar", "m", "casado", "empresário", "Sobral/CE"),
    ("TEREZA", "Tereza Cristina Aguiar", "f", "casada", "empresária", "Sobral/CE"),
    ("MARCELO", "Marcelo Augusto Feitosa", "m", "casado", "administrador de empresas", "Aracati/CE"),
    ("HELENA", "Helena Castro Lins", "f", "casada", "economista", "Fortaleza/CE"),
    ("TIAGO", "Tiago Rolim Vasconcelos", "m", "solteiro", "administrador de empresas", "Aracati/CE"),
    ("JOSUE", "Josué Pereira da Silva", "m", "casado", "comerciante", "Iguatu/CE"),
    ("EDUARDO", "Eduardo Martins Leal", "m", "casado", "empresário", "Fortaleza/CE"),
    ("FERNANDA", "Fernanda Queiroz Leal", "f", "casada", "empresária", "Fortaleza/CE"),
    ("PEDRO", "Pedro Henrique Lima", "m", "casado", "gerente operacional", "Caucaia/CE"),
    ("RODRIGO", "Rodrigo Sales Furtado", "m", "solteiro", "supervisor administrativo", "Caucaia/CE"),
    ("KLEBER", "Kleber Jorge Matos", "m", "casado", "despachante documentalista", "Fortaleza/CE"),
    ("FABIO", "Fábio Júnior Arrais", "m", "casado", "gerente agrícola", "Juazeiro do Norte/CE"),
    ("ANAPAULA", "Ana Paula Bastos", "f", "solteira", "despachante documentalista", "Fortaleza/CE"),
    ("IGOR", "Igor Lacerda Bastos", "m", "solteiro", "gerente administrativo", "Fortaleza/CE"),
    ("CAMILA", "Camila Freire Rocha", "f", "solteira", "secretária executiva", "Fortaleza/CE"),
    ("SERGIO", "Sérgio Paiva Gomes", "m", "casado", "gerente de frota", "Fortaleza/CE"),
    ("BRUNA", "Bruna Teixeira Melo", "f", "solteira", "coordenadora de logística", "Maracanaú/CE"),
]
PESSOAS = {
    pid: {
        "id": pid,
        "nome": nome,
        "genero": g,
        "nacionalidade": "brasileiro" if g == "m" else "brasileira",
        "estado_civil": ec,
        "profissao": prof,
        "cidade": cid,
        "cpf": gerar_cpf(rng),
        "rg": f"{rng.randint(1000000, 99999999)} SSP/CE",
    }
    for pid, nome, g, ec, prof, cid in _P
}


def N(pid: str) -> str:
    return PESSOAS[pid]["nome"]


# ------------------------------------------------------------------------------------ veículos
_V = [
    # id, marca/modelo, fab, mod, cor, combustível, espécie/tipo, valor (None = não informado)
    ("STRADA", "FIAT/STRADA FREEDOM 1.3 CS", 2023, 2024, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 98500),
    ("HILUX", "TOYOTA/HILUX CD SRX 4X4 2.8", 2024, 2024, "PRATA", "DIESEL", "CARGA/CAMINHONETE", 289900),
    ("SAVEIRO_M", "VW/SAVEIRO ROBUST CD 1.6", 2021, 2022, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 79000),
    ("HB20", "HYUNDAI/HB20 1.0M SENSE", 2022, 2022, "CINZA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 72000),
    ("ACCELO", "M.BENZ/ACCELO 1016", 2020, 2021, "BRANCA", "DIESEL", "CARGA/CAMINHÃO", 265000),
    ("FIORINO_M", "FIAT/FIORINO ENDURANCE 1.4", 2023, 2023, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/FURGÃO", 94000),
    ("COMPASS", "JEEP/COMPASS LONGITUDE T270", 2023, 2023, "PRETA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 165000),
    ("MONTANA", "GM/MONTANA PREMIER 1.2 TURBO", 2024, 2024, "VERMELHA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 112000),
    ("S10", "GM/S10 CD LTZ 2.8 4X4", 2023, 2023, "PRATA", "DIESEL", "CARGA/CAMINHONETE", 215000),
    ("SW4", "TOYOTA/SW4 SRX 4X4 2.8", 2022, 2023, "BRANCA", "DIESEL", "PASSAGEIRO/AUTOMÓVEL", None),
    ("MASTER_C", "RENAULT/MASTER FURGÃO L3H2", 2022, 2022, "BRANCA", "DIESEL", "CARGA/FURGÃO", 210000),
    ("DELIVERY", "VW/DELIVERY 9.170", 2021, 2021, "BRANCA", "DIESEL", "CARGA/CAMINHÃO", 310000),
    ("HILUX_SR", "TOYOTA/HILUX CD SR 4X2 2.8", 2021, 2021, "PRATA", "DIESEL", "CARGA/CAMINHONETE", 185000),
    ("COROLLA", "TOYOTA/COROLLA XEI 2.0 FLEX", 2022, 2023, "PRETA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 128000),
    ("KWID", "RENAULT/KWID ZEN 1.0", 2023, 2023, "BRANCA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 62000),
    ("CRONOS", "FIAT/CRONOS DRIVE 1.3", 2023, 2023, "PRATA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 85000),
    ("SPRINTER", "M.BENZ/SPRINTER 416 CDI FURGÃO", 2021, 2021, "BRANCA", "DIESEL", "CARGA/FURGÃO", 230000),
    ("SAVEIRO_C", "VW/SAVEIRO ROBUST CD 1.6", 2021, 2022, "PRATA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 79000),
    ("COROLLACROSS", "TOYOTA/COROLLA CROSS XRE 2.0", 2023, 2023, "CINZA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 158000),
    ("DAILY", "IVECO/DAILY 35-150 CS", 2022, 2022, "BRANCA", "DIESEL", "CARGA/CAMINHÃO", 245000),
    ("CIVIC", "HONDA/CIVIC EXL 2.0", 2021, 2021, "CINZA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 118000),
    ("HRV", "HONDA/HR-V EXL 1.5", 2023, 2023, "BRANCA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 155000),
    ("TORO", "FIAT/TORO VOLCANO 2.0 DIESEL 4X4", 2023, 2023, "VERMELHA", "DIESEL", "CARGA/CAMINHONETE", 165000),
    ("AMAROK", "VW/AMAROK HIGHLINE V6 3.0", 2022, 2022, "PRETA", "DIESEL", "CARGA/CAMINHONETE", 240000),
    ("STRADA_E", "FIAT/STRADA ENDURANCE 1.3 CS", 2023, 2023, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 92000),
    ("PULSE", "FIAT/PULSE DRIVE 1.3", 2023, 2023, "CINZA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 98000),
    ("ATEGO", "M.BENZ/ATEGO 2426 6X2", 2020, 2020, "BRANCA", "DIESEL", "CARGA/CAMINHÃO", 330000),
    ("FIORINO_C", "FIAT/FIORINO ENDURANCE 1.4", 2023, 2023, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/FURGÃO", 94000),
    ("VOLVO", "VOLVO/FH 460 6X2T", 2019, 2019, "BRANCA", "DIESEL", "TRAÇÃO/CAMINHÃO TRATOR", 420000),
    ("DUCATO", "FIAT/DUCATO CARGO 2.2", 2022, 2022, "BRANCA", "DIESEL", "CARGA/FURGÃO", 190000),
    ("CONSTELLATION", "VW/CONSTELLATION 24.280", 2021, 2021, "BRANCA", "DIESEL", "CARGA/CAMINHÃO", 380000),
    ("HILUX_SRV", "TOYOTA/HILUX CD SRV 4X4 2.8", 2022, 2022, "BRANCA", "DIESEL", "CARGA/CAMINHONETE", 230000),
    ("CARGO", "FORD/CARGO 816 S", 2019, 2019, "BRANCA", "DIESEL", "CARGA/CAMINHÃO", 175000),
    ("ONIX", "GM/ONIX LT 1.0", 2022, 2022, "PRATA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 76000),
    ("MASTER_M", "RENAULT/MASTER FURGÃO L3H2", 2022, 2022, "BRANCA", "DIESEL", "CARGA/FURGÃO", 210000),
]
_WMI = {"FIAT": "9BD", "TOYOTA": "9BR", "VW": "9BW", "HYUNDAI": "9BH", "M.BENZ": "9BM", "JEEP": "988",
        "GM": "9BG", "RENAULT": "93Y", "IVECO": "93Z", "HONDA": "93H", "VOLVO": "9BV", "FORD": "9BF"}
VEICULOS = {}
for vid, mm, fab, mod, cor, comb, esp, valor in _V:
    VEICULOS[vid] = {
        "id": vid, "marca_modelo": mm, "ano_fabricacao": fab, "ano_modelo": mod, "cor": cor,
        "combustivel": comb, "especie_tipo": esp, "placa": gerar_placa(rng), "renavam": gerar_renavam(rng),
        "chassi": gerar_chassi(rng, _WMI[mm.split("/")[0]]), "valor": valor,
    }


def VEIC(vid: str) -> str:
    v = VEICULOS[vid]
    return (f"{v['marca_modelo']}, ano/modelo {v['ano_fabricacao']}/{v['ano_modelo']}, cor {v['cor'].lower()}, "
            f"placa {v['placa']}, RENAVAM {v['renavam']}, chassi {v['chassi']}")


# ------------------------------------------------------------------------------------ empresas
def _emp(eid, razao, tipo, cidade, objeto, capital, socios, **kw):
    return eid, {"id": eid, "razao_social": razao, "tipo": tipo, "cidade": cidade, "objeto": objeto,
                 "capital": capital, "socios": socios, "cnpj": gerar_cnpj(rng),
                 "nire": f"23{rng.randint(100000000, 999999999)}", **kw}


EMPRESAS = dict([
    _emp("SERTAO", "TRANSPORTES SERTÃO VERDE LTDA.", "LTDA", "Fortaleza/CE",
         "transporte rodoviário de cargas em geral, municipal, intermunicipal e interestadual", 300000,
         [("JOAO", 50), ("MARIA", 50)]),
    _emp("MANDACARU", "CONSTRUTORA MANDACARU LTDA.", "LTDA", "Fortaleza/CE",
         "construção de edifícios, obras de urbanização e incorporação de empreendimentos imobiliários", 500000,
         [("CARLOS", 60), ("LUCIANA", 40)]),
    _emp("JANGADA", "LOCADORA JANGADA LTDA.", "LTDA", "Caucaia/CE",
         "locação de automóveis sem condutor e gestão de frotas", 400000,
         [("FRANCISCO", 40), ("ANABEATRIZ", 35), ("RAIMUNDO", 25)]),
    _emp("MARACANAU", "LOGÍSTICA MARACANAÚ LTDA.", "LTDA", "Maracanaú/CE",
         "transporte rodoviário de cargas, armazenagem e operação logística", 600000,
         [("ROBERTO", 70), ("SANDRA", 30)]),
    _emp("IRACEMA", "CLÍNICA IRACEMA ODONTOLOGIA LTDA.", "LTDA", "Fortaleza/CE",
         "atividade odontológica e serviços de radiologia odontológica", 120000,
         [("PAULA", 50), ("ITALO", 50)]),
    _emp("CARIRI", "AGROPECUÁRIA CARIRI LTDA.", "LTDA", "Juazeiro do Norte/CE",
         "criação de bovinos, cultivo de culturas temporárias e comércio de produtos agropecuários", 800000,
         [("ANTONIO", 55), ("JOSEFA", 45)]),
    _emp("CAMOCIM", "PESCADOS CAMOCIM LTDA.", "LTDA", "Camocim/CE",
         "comércio atacadista de pescados e frutos do mar, beneficiamento e transporte próprio", 350000,
         [("VALDIR", 40), ("MARCIA", 35), ("OSVALDO", 25)]),
    _emp("PRIME", "NORDESTE PRIME SERVIÇOS ADMINISTRATIVOS LTDA.", "LTDA", "Fortaleza/CE",
         "serviços combinados de escritório e apoio administrativo", 240000,
         [("MARCOS", 50), ("LEONARDO", 50)]),
    _emp("TECH", "TECHNORDESTE SOLUÇÕES DIGITAIS LTDA.", "SLU", "Fortaleza/CE",
         "desenvolvimento de programas de computador sob encomenda e consultoria em tecnologia da informação",
         100000, [("RAFAEL", 100)]),
    _emp("CHAPADA", "PANIFICADORA CHAPADA DO ARARIPE LTDA.", "LTDA", "Crato/CE",
         "fabricação de produtos de panificação e comércio varejista de produtos alimentícios", 150000,
         [("JOAQUIM", 60), ("LUCIA", 40)]),
    _emp("RUSSAS", "CERÂMICA RUSSAS LTDA.", "LTDA", "Russas/CE",
         "fabricação de telhas, tijolos e outros artigos de barro cozido", 700000,
         [("HELIO", 50), ("REGINA", 50)]),
    _emp("SOBRAL", "GRÁFICA SOBRALENSE LTDA.", "LTDA", "Sobral/CE",
         "impressão de material para uso publicitário e serviços de acabamento gráfico", 200000,
         [("WAGNER", 60), ("TEREZA", 40)]),
    _emp("ARACATI", "DISTRIBUIDORA ARACATI S.A.", "SA", "Aracati/CE",
         "comércio atacadista e distribuição de bebidas", 5000000, []),
    _emp("JPSILVA", "J P DA SILVA MATERIAIS DE CONSTRUCAO", "EI", "Iguatu/CE",
         "comércio varejista de materiais de construção em geral", 80000, [("JOSUE", 100)]),
    _emp("BEIRAMAR", "BEIRA-MAR VEÍCULOS LTDA.", "LTDA", "Fortaleza/CE",
         "comércio a varejo de automóveis, camionetas e utilitários novos e usados", 1000000,
         [("EDUARDO", 60), ("FERNANDA", 40)]),
])


def RAZAO(eid: str) -> str:
    return EMPRESAS[eid]["razao_social"]


# ---------------------------------------------------------------------------------- documentos
# Cada documento: o que o redator DEVE incluir. `frases_obrigatorias` são conferidas literalmente
# (normalização de espaços) pelo verificador do corpus. O gabarito depende delas.
CARTORIOS = {
    "IRACEMA": "Cartório Iracema – 4º Tabelionato de Notas de Fortaleza (fictício)",
    "JANGADEIRO": "Tabelionato Jangadeiro de Notas e Registros – Caucaia/CE (fictício)",
    "CARIRI": "Cartório Padre Ibiapina – 2º Ofício de Notas de Juazeiro do Norte/CE (fictício)",
    "CRATO": "Tabelionato Araripe – 1º Ofício de Notas do Crato/CE (fictício)",
    "MARACANAU": "Cartório Pitaguary – 1º Ofício de Notas de Maracanaú/CE (fictício)",
    "ARACATI": "Tabelionato Jaguaribe – Ofício Único de Notas de Aracati/CE (fictício)",
}
DOCS: dict[str, dict] = {}


def doc(did, tipo, empresa, data, titulo, instrucoes, frases=(), registro=None, palavras=(900, 1600), **kw):
    DOCS[did] = {"id": did, "tipo": tipo, "empresa": empresa, "data": data, "titulo": titulo,
                 "instrucoes": list(instrucoes), "frases_obrigatorias": list(frases),
                 "registro": registro, "palavras": list(palavras), **kw}


def reg(data):
    return {"orgao": "JUCEC – Junta Comercial do Estado do Ceará", "data": data,
            "numero": f"{rng.randint(10000000, 99999999)}{rng.randint(100, 999)}"}


SEM_OUTRAS_REGRAS = ("NÃO inclua nenhuma outra regra sobre forma de assinatura, alçada de valor, alienação ou oneração "
                     "de bens, outorga de procurações ou necessidade de aprovação de sócios além das indicadas aqui.")

# --- contratos sociais e atos societários
doc("SERTAO_CS", "contrato_social", "SERTAO", "2019-05-06", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('JOAO')} (50% – R$ 150.000,00) e {N('MARIA')} (50% – R$ 150.000,00), capital integralizado em moeda corrente.",
     "Cláusula de administração (Cláusula Sétima): ambos os sócios são administradores e atuam INDISTINTAMENTE (cada um pode representar sozinho). Use a frase obrigatória.",
     "Na mesma cláusula, inclua a vedação padrão de uso do nome empresarial em avais/fianças e a restrição sobre IMÓVEIS da frase obrigatória (é uma armadilha semântica: não se aplica a veículos).",
     SEM_OUTRAS_REGRAS],
    ["que a exercerão indistintamente",
     "onerar ou alienar bens imóveis da sociedade, sem autorização dos sócios que representem três quartos do capital social"],
    registro=reg("2019-05-20"))

doc("MANDACARU_CS", "contrato_social_consolidado", "MANDACARU", "2023-03-02",
    "QUARTA ALTERAÇÃO E CONSOLIDAÇÃO DO CONTRATO SOCIAL",
    ["Documento de 4ª alteração contratual que CONSOLIDA o contrato social (a alteração em si trata apenas da mudança de endereço da sede; em seguida vem o contrato consolidado completo).",
     f"Sócios: {N('CARLOS')} (60% – R$ 300.000,00) e {N('LUCIANA')} (40% – R$ 200.000,00).",
     "Administração: ambos os sócios, SEMPRE EM CONJUNTO, com a frase obrigatória.",
     SEM_OUTRAS_REGRAS],
    ["exercida conjuntamente pelos sócios CARLOS EDUARDO BEZERRA e LUCIANA MOURA SAMPAIO",
     "sendo vedada a prática isolada de qualquer ato de alienação ou oneração de bens da sociedade"],
    registro=reg("2023-03-10"))

doc("JANGADA_CS", "contrato_social", "JANGADA", "2020-02-14", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('FRANCISCO')} (40%), {N('ANABEATRIZ')} (35%) e {N('RAIMUNDO')} (25%); capital R$ 400.000,00.",
     f"Administração EXCLUSIVA do sócio {N('FRANCISCO')}, isoladamente; os demais sócios são apenas quotistas, sem poderes de administração.",
     "Os poderes do administrador incluem expressamente alienar veículos da frota (frase obrigatória).",
     SEM_OUTRAS_REGRAS],
    ["A administração da sociedade cabe exclusivamente ao sócio FRANCISCO WELLINGTON ROCHA",
     "inclusive comprar, vender e alienar os veículos integrantes da frota da sociedade"],
    registro=reg("2020-02-27"))

doc("MARACANAU_CS", "contrato_social", "MARACANAU", "2020-08-03", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('ROBERTO')} (70%) e {N('SANDRA')} (30%); capital R$ 600.000,00, totalmente integralizado.",
     f"Os sócios NÃO são administradores. É designado administrador NÃO SÓCIO {N('GUSTAVO')} ({PESSOAS['GUSTAVO']['profissao']}, CPF {PESSOAS['GUSTAVO']['cpf']}), aprovado pela unanimidade dos sócios, por prazo indeterminado, que representa a sociedade isoladamente.",
     "Os poderes do administrador incluem expressamente comprar, vender, alienar e onerar veículos da frota (frase obrigatória).",
     "Inclua o termo de posse do administrador no próprio instrumento.",
     SEM_OUTRAS_REGRAS],
    ["administrador não sócio",
     "que representará a sociedade isoladamente, ativa e passivamente, em juízo ou fora dele",
     "comprar, vender, alienar e onerar veículos da frota"],
    registro=reg("2020-08-18"))

doc("IRACEMA_CS", "contrato_social", "IRACEMA", "2022-01-10", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('PAULA')} (50%) e {N('ITALO')} (50%); capital R$ 120.000,00.",
     "Administração: ambos os sócios são administradores, mas o contrato é OMISSO quanto à forma de atuação (NÃO use nenhuma palavra como isoladamente, indistintamente, em conjunto, conjuntamente, individualmente, separadamente, ambos devem assinar etc. na cláusula de administração).",
     SEM_OUTRAS_REGRAS],
    ["A administração da sociedade caberá aos sócios PAULA REGINA SARAIVA e ÍTALO MENEZES CAVALCANTE, com os poderes e atribuições de administradores"],
    registro=reg("2022-01-25"))

doc("CARIRI_CS", "contrato_social", "CARIRI", "2018-06-01", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('ANTONIO')} (55%) e {N('JOSEFA')} (45%); capital R$ 800.000,00.",
     "Administração: ambos os sócios, ISOLADAMENTE (frase obrigatória 1).",
     "Parágrafo com alçada por valor (frase obrigatória 2): acima de R$ 150.000,00 por unidade, exige assinatura conjunta.",
     SEM_OUTRAS_REGRAS],
    ["que a exercerão isoladamente",
     "A alienação de veículos, máquinas e implementos agrícolas de valor unitário superior a R$ 150.000,00 (cento e cinquenta mil reais) dependerá da assinatura conjunta de ambos os administradores"],
    registro=reg("2018-06-15"))

doc("CAMOCIM_CS", "contrato_social", "CAMOCIM", "2021-04-05", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('VALDIR')} (40%), {N('MARCIA')} (35%) e {N('OSVALDO')} (25%); capital R$ 350.000,00.",
     f"Administração: {N('VALDIR')} e {N('MARCIA')}, qualquer deles isoladamente (frase obrigatória 1). {N('OSVALDO')} é só quotista.",
     "Restrição (frase obrigatória 2): alienação de bens do ativo não circulante, INCLUSIVE VEÍCULOS, depende de prévia aprovação de sócios com mais da metade do capital.",
     SEM_OUTRAS_REGRAS],
    ["qualquer deles isoladamente",
     "Dependerão de prévia aprovação de sócios que representem mais da metade do capital social a alienação ou a oneração de bens do ativo não circulante da sociedade, inclusive veículos automotores, máquinas e equipamentos"],
    registro=reg("2021-04-19"))

doc("CAMOCIM_ATA", "ata_reuniao_socios", "CAMOCIM", "2026-08-28", "ATA DE REUNIÃO DE SÓCIOS",
    [f"Reunião de sócios da {RAZAO('CAMOCIM')} em 28/08/2026, na sede, convocada por {N('VALDIR')}.",
     f"Presentes {N('VALDIR')} (40%) e {N('OSVALDO')} (25%), totalizando 65% do capital; {N('MARCIA')} (35%) ausente, regularmente convocada.",
     f"Deliberação única: aprovada por unanimidade dos presentes (65% do capital) a alienação do veículo {VEIC('DELIVERY')}, pelo valor mínimo de R$ 300.000,00 (frase obrigatória), autorizando os administradores a praticar os atos necessários, inclusive assinar a ATPV-e.",
     "Encerramento, lavratura e assinaturas dos presentes. Sem registro na Junta (ata de reunião de sócios em sociedade com menos de 10 sócios pode ficar em livro)."],
    ["pelo valor mínimo de R$ 300.000,00 (trezentos mil reais)"],
    palavras=(400, 700))

doc("PRIME_CS", "contrato_social", "PRIME", "2024-02-20", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('MARCOS')} (50% – R$ 120.000,00, integralizados com a conferência do veículo descrito abaixo, avaliado em R$ 120.000,00) e {N('LEONARDO')} (50% – R$ 120.000,00, em moeda corrente).",
     f"Veículo conferido ao capital por {N('MARCOS')}: {VEIC('COROLLA')}. Descreva a conferência de bem para integralização (o sócio transfere a propriedade do veículo à sociedade).",
     "Administração: ambos os sócios, qualquer um deles isoladamente (frase obrigatória 1).",
     "Parágrafo específico na cláusula de capital ou de administração (frase obrigatória 2, adaptando placa/RENAVAM/chassi exatos): esse veículo só pode ser alienado com a assinatura do sócio MARCOS.",
     SEM_OUTRAS_REGRAS],
    ["qualquer um deles isoladamente",
     f"somente poderá ser alienado, a qualquer título, mediante a assinatura do sócio MARCOS ANTÔNIO GIRÃO, que representará a sociedade nesse ato",
     VEICULOS["COROLLA"]["placa"]],
    registro=reg("2024-03-01"))

doc("TECH_CS", "contrato_social_slu", "TECH", "2022-07-11", "ATO CONSTITUTIVO DE SOCIEDADE LIMITADA UNIPESSOAL",
    [f"Sócio único: {N('RAFAEL')}, titular de 100% do capital de R$ 100.000,00 (art. 1.052, §1º, do Código Civil).",
     "Administração pelo sócio único, isoladamente.",
     "Cláusula sobre procurações (frase obrigatória 2).",
     SEM_OUTRAS_REGRAS],
    ["sociedade limitada unipessoal",
     "As procurações outorgadas pela sociedade deverão especificar os poderes conferidos e, salvo as outorgadas para fins judiciais, terão prazo de validade não superior a 1 (um) ano"],
    registro=reg("2022-07-20"))

doc("CHAPADA_CS", "contrato_social", "CHAPADA", "2019-03-18", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('JOAQUIM')} (60%) e {N('LUCIA')} (40%); capital R$ 150.000,00.",
     f"Administração exclusiva de {N('JOAQUIM')}, isoladamente, por prazo indeterminado.",
     SEM_OUTRAS_REGRAS],
    ["A administração da sociedade será exercida exclusivamente pelo sócio JOAQUIM MOREIRA BRITO"],
    registro=reg("2019-04-01"))

doc("CHAPADA_ALT1", "alteracao_contratual", "CHAPADA", "2026-04-15", "PRIMEIRA ALTERAÇÃO DO CONTRATO SOCIAL",
    [f"{N('JOAQUIM')} renuncia ao cargo de administrador (permanece sócio com 60%).",
     f"{N('LUCIA')} passa a ser a administradora única, isoladamente (frase obrigatória).",
     "A cláusula de administração passa a ter nova redação. Permanecem inalteradas as demais cláusulas.",
     "NÃO mencione procurações nem revogação de procurações.",
     SEM_OUTRAS_REGRAS],
    ["A administração da sociedade passa a ser exercida exclusivamente pela sócia LÚCIA HELENA BRITO, isoladamente"],
    registro=reg("2026-04-28"), palavras=(500, 900))

doc("RUSSAS_CS", "contrato_social", "RUSSAS", "2018-10-22", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('HELIO')} (50%) e {N('REGINA')} (50%); capital R$ 700.000,00.",
     "Administração (Cláusula Oitava): ambos os sócios, isoladamente (frase obrigatória).",
     SEM_OUTRAS_REGRAS],
    ["os quais poderão representá-la isoladamente"],
    registro=reg("2018-11-05"))

doc("RUSSAS_ALT1", "alteracao_contratual", "RUSSAS", "2025-08-11", "PRIMEIRA ALTERAÇÃO DO CONTRATO SOCIAL",
    ["Altera APENAS a Cláusula Oitava (administração), que passa a vigorar com a redação da frase obrigatória: administração em conjunto, exigida a assinatura de ambos para alienação de bens, inclusive veículos.",
     "Permanecem inalteradas as demais cláusulas.",
     SEM_OUTRAS_REGRAS],
    ["A Cláusula Oitava passa a vigorar com a seguinte redação",
     "exigindo-se a assinatura de ambos os sócios para a alienação de bens móveis e imóveis, inclusive veículos"],
    registro=reg("2025-08-25"), palavras=(450, 800))

doc("SOBRAL_CS", "contrato_social", "SOBRAL", "2021-02-01", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('WAGNER')} (60%) e {N('TEREZA')} (40%); capital R$ 200.000,00.",
     f"Administração por {N('WAGNER')}, isoladamente, POR PRAZO DETERMINADO de 3 anos contados do registro (frase obrigatória). {N('TEREZA')} é só quotista.",
     SEM_OUTRAS_REGRAS],
    ["pelo prazo de 3 (três) anos, contados do registro deste instrumento, permitida a recondução"],
    registro=reg("2021-02-10"))

doc("ARACATI_ESTATUTO", "estatuto_social", "ARACATI", "2024-04-25", "ESTATUTO SOCIAL CONSOLIDADO",
    ["Estatuto social consolidado aprovado em Assembleia Geral Extraordinária de 25/04/2024 (companhia fechada). Capital R$ 5.000.000,00 dividido em ações ordinárias nominativas.",
     "Administração: Conselho de Administração (3 membros) e Diretoria com 3 diretores (Diretor-Presidente, Diretor Financeiro, Diretor Comercial), eleitos pelo Conselho para mandato de 2 anos, permitida a reeleição.",
     "Art. 18 (frase obrigatória 1): formas de representação: (a) 2 diretores em conjunto; (b) 1 diretor em conjunto com 1 procurador; (c) 1 ou mais procuradores, nos termos do mandato.",
     "Art. 19 (frase obrigatória 2): procurações outorgadas por 2 diretores, com poderes especificados e prazo máximo de 1 ano (salvo ad judicia).",
     "Art. 20 (frase obrigatória 3): só alienação de bens do ativo não circulante ACIMA de R$ 1.000.000,00 depende do Conselho (os veículos dos casos estão abaixo disso).",
     SEM_OUTRAS_REGRAS],
    ["por 2 (dois) Diretores em conjunto",
     "por 1 (um) Diretor em conjunto com 1 (um) procurador",
     "As procurações serão outorgadas pela Companhia mediante a assinatura de 2 (dois) Diretores",
     "de valor superior a R$ 1.000.000,00 (um milhão de reais)"],
    registro=reg("2024-05-08"), palavras=(1300, 2000))

doc("ARACATI_RCA", "ata_conselho", "ARACATI", "2025-05-02", "ATA DA REUNIÃO DO CONSELHO DE ADMINISTRAÇÃO",
    [f"Eleição da Diretoria para mandato de 2 (dois) anos: {N('MARCELO')} (Diretor-Presidente), {N('HELENA')} (Diretora Financeira) e {N('TIAGO')} (Diretor Comercial), com qualificação completa e CPF.",
     "Termos de posse lavrados em livro próprio; declarações de desimpedimento.",
     "Mandato até a reunião do Conselho que eleger a nova Diretoria em 2027 (frase obrigatória)."],
    ["com mandato de 2 (dois) anos"],
    registro=reg("2025-05-15"), palavras=(500, 900))

doc("JPSILVA_REQ", "requerimento_empresario", "JPSILVA", "2016-09-05", "REQUERIMENTO DE EMPRESÁRIO",
    [f"Requerimento de inscrição de EMPRESÁRIO INDIVIDUAL na JUCEC: nome civil {N('JOSUE')}, CPF, nome empresarial J P DA SILVA MATERIAIS DE CONSTRUCAO, CNPJ, NIRE, endereço em Iguatu/CE, objeto, capital R$ 80.000,00, início de atividades 05/09/2016.",
     "Formato de formulário (campos rotulados), com declaração de desimpedimento e assinatura do empresário.",
     "Não há sócios nem contrato social: o empresário individual é o próprio titular."],
    ["EMPRESÁRIO INDIVIDUAL"],
    registro=reg("2016-09-12"), palavras=(300, 600))

doc("BEIRAMAR_CS", "contrato_social", "BEIRAMAR", "2019-11-11", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('EDUARDO')} (60%) e {N('FERNANDA')} (40%); capital R$ 1.000.000,00. Objeto: comércio de veículos novos e usados (revenda).",
     f"Administração por {N('EDUARDO')}, isoladamente; {N('FERNANDA')} é só quotista.",
     "Restrição (frase obrigatória): alienação de bens do ATIVO IMOBILIZADO depende de aprovação de 3/4 do capital. (Os veículos para revenda são mercadoria/estoque, não ativo imobilizado — não explique isso no contrato.)",
     SEM_OUTRAS_REGRAS],
    ["A alienação de bens integrantes do ativo imobilizado da sociedade dependerá de aprovação de sócios que representem, no mínimo, três quartos do capital social"],
    registro=reg("2019-11-25"))

# --- procurações, substabelecimentos e revogação
PODERES_VEICULO = ("vender, ceder, transferir ou de qualquer forma alienar veículos automotores de propriedade da "
                   "outorgante, a quem e pelo preço que convencionar, assinar a Autorização para Transferência de "
                   "Propriedade do Veículo (ATPV/ATPV-e), receber o preço e dar quitação, requerer e assinar o que "
                   "for necessário perante o DETRAN")


def procuracao(did, data, empresa, outorgante_desc, outorgados, poderes_txt, prazo_txt, sub_txt, forma, frases,
               extra=(), cartorio="IRACEMA", firma=None):
    instr = [f"Outorgante: {outorgante_desc}.",
             "Outorgado(s): " + "; ".join(f"{N(o)} ({PESSOAS[o]['profissao']}, CPF {PESSOAS[o]['cpf']})" for o in outorgados) + ".",
             f"Poderes: {poderes_txt}.", f"Prazo: {prazo_txt}.", f"Substabelecimento: {sub_txt}.", *extra]
    if forma == "publica":
        instr.insert(0, f"PROCURAÇÃO POR INSTRUMENTO PÚBLICO lavrada em {CARTORIOS[cartorio]}, com livro e folhas, "
                        "'SAIBAM quantos este público instrumento...', identificação do tabelião/escrevente, menção ao "
                        "documento societário que comprova os poderes de quem representa a outorgante (quando PJ), "
                        "fecho com selo digital fictício e indicação de TRASLADO.")
    else:
        instr.insert(0, "PROCURAÇÃO POR INSTRUMENTO PARTICULAR (documento simples, assinado pelo outorgante). "
                        + ("Ao final, inclua carimbo de RECONHECIMENTO DE FIRMA POR AUTENTICIDADE em "
                           f"{CARTORIOS[cartorio]}." if firma else
                           "NÃO há reconhecimento de firma nem qualquer carimbo de cartório."))
    doc(did, "procuracao", empresa, data, "PROCURAÇÃO", instr, frases, palavras=(350, 800), forma=forma,
        firma_reconhecida=firma, outorgados=outorgados)


procuracao("POA_PEDRO", "2026-02-10", "JANGADA",
           f"{RAZAO('JANGADA')} (CNPJ {EMPRESAS['JANGADA']['cnpj']}), representada por seu sócio administrador {N('FRANCISCO')}",
           ["PEDRO"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "1 (um) ano a contar da data da lavratura", "permitido, no todo ou em parte, COM reserva de iguais poderes",
           "publica", ["poderes especiais e expressos", "com reserva de iguais poderes", "1 (um) ano"],
           cartorio="JANGADEIRO")
procuracao("POA_RODRIGO", "2026-03-05", "JANGADA",
           f"{RAZAO('JANGADA')} (CNPJ {EMPRESAS['JANGADA']['cnpj']}), representada por seu sócio administrador {N('FRANCISCO')}",
           ["RODRIGO"], "AMPLOS E GERAIS poderes de administração: gerir os negócios, representar a outorgante perante "
                        "repartições públicas federais, estaduais e municipais, inclusive o DETRAN, assinar requerimentos, "
                        "pagar taxas, licenciar veículos e retirar documentos. NÃO inclua NENHUM poder de vender, alienar, "
                        "transferir propriedade ou assinar ATPV/CRV (é o teste: poderes gerais não bastam para alienar)",
           "até 31 de dezembro de 2026", "omisso (não mencione)", "publica",
           ["amplos e gerais poderes"], cartorio="JANGADEIRO")
procuracao("POA_KLEBER_VENCIDA", "2025-01-20", "MANDACARU",
           f"{RAZAO('MANDACARU')} (CNPJ {EMPRESAS['MANDACARU']['cnpj']}), representada CONJUNTAMENTE por seus sócios administradores {N('CARLOS')} e {N('LUCIANA')}",
           ["KLEBER"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "6 (seis) meses a contar desta data (frase obrigatória)", "vedado (não pode substabelecer)", "publica",
           ["pelo prazo de 6 (seis) meses"])
procuracao("POA_FABIO_REVOGADA", "2025-11-03", "CARIRI",
           f"{RAZAO('CARIRI')} (CNPJ {EMPRESAS['CARIRI']['cnpj']}), representada por seu sócio administrador {N('ANTONIO')}",
           ["FABIO"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "prazo indeterminado, até revogação expressa", "omisso (não mencione)", "publica",
           ["por prazo indeterminado"], cartorio="CARIRI")
doc("REV_FABIO", "revogacao_procuracao", "CARIRI", "2026-06-12", "ESCRITURA PÚBLICA DE REVOGAÇÃO DE PROCURAÇÃO",
    [f"Lavrada em {CARTORIOS['CARIRI']}. Outorgante revogante: {RAZAO('CARIRI')}, representada por sua sócia administradora {N('JOSEFA')}.",
     f"Revoga, para todos os fins, a procuração pública outorgada a {N('FABIO')} em 03/11/2025 neste mesmo cartório (indique livro e folhas fictícios), com notificação do procurador.",
     "Fecho com selo digital fictício."],
    ["revoga", "03 de novembro de 2025"], palavras=(250, 450))
procuracao("POA_KLEBER_SO_CARLOS", "2026-04-02", "MANDACARU",
           f"{RAZAO('MANDACARU')} (CNPJ {EMPRESAS['MANDACARU']['cnpj']}), representada APENAS por seu sócio administrador {N('CARLOS')} (a sócia {N('LUCIANA')} NÃO comparece nem assina)",
           ["KLEBER"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "1 (um) ano", "omisso (não mencione)", "publica", ["poderes especiais e expressos"])
procuracao("POA_PF_JOAO", "2026-05-14", "SERTAO",
           f"{N('JOAO')}, pessoa física, em NOME PRÓPRIO (qualificação pessoal completa, CPF {PESSOAS['JOAO']['cpf']}). NÃO mencione a empresa {RAZAO('SERTAO')} nem a qualidade de sócio/administrador",
           ["KLEBER"], "poderes especiais para vender, transferir e alienar veículos de propriedade do OUTORGANTE, "
                       "assinar ATPV/ATPV-e e dar quitação (frase obrigatória)",
           "1 (um) ano", "omisso (não mencione)", "particular",
           ["veículos de propriedade do outorgante"], firma=True)
procuracao("POA_ANAPAULA_CIVIC", "2026-07-01", "TECH",
           f"{RAZAO('TECH')} (CNPJ {EMPRESAS['TECH']['cnpj']}), representada por seu sócio único e administrador {N('RAFAEL')}",
           ["ANAPAULA"], f"poderes especiais e expressos para vender e transferir EXCLUSIVAMENTE o veículo {VEIC('CIVIC')}, "
                         "assinar a respectiva ATPV-e, receber o preço e dar quitação (só esse veículo)",
           "90 (noventa) dias", "omisso (não mencione)", "publica",
           ["exclusivamente", VEICULOS["CIVIC"]["placa"]])
doc("SUB_PEDRO_ANAPAULA", "substabelecimento", "JANGADA", "2026-08-03", "SUBSTABELECIMENTO DE PROCURAÇÃO",
    [f"SUBSTABELECIMENTO POR INSTRUMENTO PÚBLICO lavrado em {CARTORIOS['JANGADEIRO']}.",
     f"Substabelecente: {N('PEDRO')}, procurador de {RAZAO('JANGADA')} conforme procuração pública de 10/02/2026 (indique livro 312-P, folhas 088/089, do mesmo cartório).",
     f"Substabelecida: {N('ANAPAULA')} ({PESSOAS['ANAPAULA']['profissao']}, CPF {PESSOAS['ANAPAULA']['cpf']}).",
     "Substabelece COM RESERVA de iguais poderes todos os poderes recebidos (frase obrigatória)."],
    ["com reserva de iguais poderes", "10 de fevereiro de 2026"], palavras=(250, 450))
procuracao("POA_IGOR", "2026-03-10", "TECH",
           f"{RAZAO('TECH')} (CNPJ {EMPRESAS['TECH']['cnpj']}), representada por seu sócio único e administrador {N('RAFAEL')}",
           ["IGOR"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "1 (um) ano", "EXPRESSAMENTE VEDADO o substabelecimento (frase obrigatória)", "publica",
           ["vedado o substabelecimento"])
doc("SUB_IGOR_KLEBER", "substabelecimento", "TECH", "2026-08-20", "SUBSTABELECIMENTO",
    ["SUBSTABELECIMENTO POR INSTRUMENTO PARTICULAR com reconhecimento de firma por autenticidade (carimbo de cartório fictício).",
     f"Substabelecente: {N('IGOR')}, procurador de {RAZAO('TECH')} conforme procuração pública de 10/03/2026 do {CARTORIOS['IRACEMA']}.",
     f"Substabelecido: {N('KLEBER')} (CPF {PESSOAS['KLEBER']['cpf']}).",
     "Substabelece com reserva os poderes para vender veículos da outorgante e assinar ATPV-e. NÃO mencione a vedação existente na procuração original."],
    ["com reserva"], palavras=(200, 400))
procuracao("POA_FABIO_2026", "2026-01-15", "CARIRI",
           f"{RAZAO('CARIRI')} (CNPJ {EMPRESAS['CARIRI']['cnpj']}), representada por sua sócia administradora {N('JOSEFA')}",
           ["FABIO"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "2 (dois) anos", "permitido (podendo substabelecer)", "publica",
           ["podendo substabelecer"], cartorio="CARIRI")
doc("SUB_FABIO_ANAPAULA", "substabelecimento", "CARIRI", "2026-06-30", "SUBSTABELECIMENTO DE PROCURAÇÃO",
    [f"SUBSTABELECIMENTO POR INSTRUMENTO PÚBLICO lavrado em {CARTORIOS['CARIRI']}.",
     f"Substabelecente: {N('FABIO')}, procurador de {RAZAO('CARIRI')} conforme procuração pública de 15/01/2026 do mesmo cartório (livro/folhas fictícios).",
     f"Substabelecida: {N('ANAPAULA')} (CPF {PESSOAS['ANAPAULA']['cpf']}).",
     "Substabelece SEM RESERVA de poderes (o substabelecente deixa de ter os poderes) — frase obrigatória."],
    ["sem reserva de poderes"], palavras=(250, 450))
procuracao("POA_CAMILA", "2026-08-01", "TECH",
           f"{RAZAO('TECH')} (CNPJ {EMPRESAS['TECH']['cnpj']}), representada por seu sócio único e administrador {N('RAFAEL')}",
           ["CAMILA"], f"poderes especiais e expressos para vender o veículo {VEIC('PULSE')}, assinar a ATPV-e, receber o preço e dar quitação",
           "6 (seis) meses", "omisso (não mencione)", "particular",
           ["poderes especiais e expressos", VEICULOS["PULSE"]["placa"]], firma=False)
procuracao("POA_SERGIO_BRUNA", "2026-05-20", "MARACANAU",
           f"{RAZAO('MARACANAU')} (CNPJ {EMPRESAS['MARACANAU']['cnpj']}), representada por seu administrador {N('GUSTAVO')}",
           ["SERGIO", "BRUNA"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "1 (um) ano", "omisso (não mencione)", "publica",
           ["agindo sempre em conjunto"],
           extra=["Os outorgados deverão agir SEMPRE EM CONJUNTO (frase obrigatória)."], cartorio="MARACANAU")
procuracao("POA_DAVI", "2025-12-10", "CHAPADA",
           f"{RAZAO('CHAPADA')} (CNPJ {EMPRESAS['CHAPADA']['cnpj']}), representada por seu sócio administrador {N('JOAQUIM')}",
           ["DAVI"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "válida até 10 de dezembro de 2026 (frase obrigatória)", "omisso (não mencione)", "publica",
           ["10 de dezembro de 2026"], cartorio="CRATO")
procuracao("POA_SERGIO_SA", "2026-02-18", "ARACATI",
           f"{RAZAO('ARACATI')} (CNPJ {EMPRESAS['ARACATI']['cnpj']}), representada por seus Diretores {N('MARCELO')} (Diretor-Presidente) e {N('HELENA')} (Diretora Financeira), na forma do art. 19 do Estatuto",
           ["SERGIO"], "poderes especiais e expressos para, SEMPRE EM CONJUNTO COM UM DIRETOR da Companhia, vender, "
                       "ceder e transferir veículos automotores de propriedade da outorgante, assinar a ATPV-e, receber "
                       "o preço e dar quitação (frase obrigatória)",
           "1 (um) ano", "vedado", "publica", ["sempre em conjunto com um Diretor"], cartorio="ARACATI")
procuracao("POA_BRUNA_2023", "2023-03-15", "MARACANAU",
           f"{RAZAO('MARACANAU')} (CNPJ {EMPRESAS['MARACANAU']['cnpj']}), representada por seu administrador {N('GUSTAVO')}",
           ["BRUNA"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "prazo indeterminado", "omisso (não mencione)", "publica", ["prazo indeterminado"], cartorio="MARACANAU")

# ------------------------------------------------------------------------------------- casos
CASOS: list[dict] = []


def caso(cid, titulo, categoria, objetivo, empresa, docs, veiculo, data_venda, assinantes, veredito, faixas,
         conjuntos, fundamentos, crlv_proprietario=None, valor="padrao", ocr=False, ce=None):
    v = VEICULOS[veiculo]
    CASOS.append({
        "id": cid, "titulo": titulo, "categoria": categoria, "objetivo": objetivo, "empresa": empresa,
        "documentos": docs, "veiculo": veiculo, "ocr": ocr,
        "crlv_proprietario": crlv_proprietario or {"tipo": "PJ", "empresa": empresa},
        "transacao": {
            "data_venda": data_venda,
            "valor": v["valor"] if valor == "padrao" else valor,
            "assinantes": assinantes,
        },
        "esperado": {"veredito": veredito, "faixas_aceitaveis": faixas, "conjuntos_minimos": conjuntos,
                     "fundamentos": fundamentos},
        # quando a exigência administrativa do DETRAN-CE muda o resultado (procuração pública, até 1 ano)
        "esperado_ce": ce,
    })


def A(pid, nome=None, cpf=True):
    """Assinante como digitado no pedido (nome pode vir abreviado/sem acento)."""
    return {"pessoa": pid, "nome": nome or N(pid), "cpf": PESSOAS[pid]["cpf"] if cpf else None}


caso("C01", "Administração 'indistintamente' — um sócio assina", "administracao",
     "Semântica: 'indistintamente' = cada administrador assina sozinho; restrição sobre imóveis não alcança veículo; nome digitado abreviado.",
     "SERTAO", ["SERTAO_CS"], "STRADA", "2026-09-10", [A("JOAO", "JOAO B ANDRADE")],
     "PODE", ["VERDE"], [["JOAO"], ["MARIA"]], ["CC art. 1.013", "CC art. 1.060"])
caso("C02", "Assinatura conjunta exigida — só um assina", "administracao",
     "Regra de assinatura conjunta: um sócio sozinho não pode.",
     "MANDACARU", ["MANDACARU_CS"], "HILUX", "2026-09-15", [A("CARLOS")],
     "NAO_PODE", ["VERMELHO"], [["CARLOS", "LUCIANA"]], ["CC art. 1.014", "CC art. 47"])
caso("C03", "Assinatura conjunta — os dois assinam", "administracao",
     "'Se as duas partes estão, tudo está valendo.'",
     "MANDACARU", ["MANDACARU_CS"], "SAVEIRO_M", "2026-09-15", [A("CARLOS"), A("LUCIANA")],
     "PODE", ["VERDE"], [["CARLOS", "LUCIANA"]], ["CC art. 1.014"])
caso("C04", "Sócia quotista sem poder de administração assina", "administracao",
     "Ser sócio não dá poder de representação; só o administrador designado.",
     "JANGADA", ["JANGADA_CS"], "HB20", "2026-09-04", [A("ANABEATRIZ")],
     "NAO_PODE", ["VERMELHO"], [["FRANCISCO"]], ["CC art. 1.060", "CC art. 1.064"])
caso("C05", "Administrador não sócio assina", "administracao",
     "Administrador não sócio designado no contrato tem poder (art. 1.061).",
     "MARACANAU", ["MARACANAU_CS"], "ACCELO", "2026-09-21", [A("GUSTAVO")],
     "PODE", ["VERDE"], [["GUSTAVO"]], ["CC art. 1.061"])
caso("C06", "Sócio majoritário (70%) que não é administrador", "administracao",
     "Maioria do capital não substitui poder de administração.",
     "MARACANAU", ["MARACANAU_CS"], "FIORINO_M", "2026-09-21", [A("ROBERTO")],
     "NAO_PODE", ["VERMELHO"], [["GUSTAVO"]], ["CC art. 1.060", "CC art. 1.064"])
caso("C07", "Contrato omisso sobre a forma de atuação", "administracao",
     "Dois administradores sem 'isolada/conjunta': regra supletiva (art. 1.013) indica atuação separada, mas é zona cinzenta.",
     "IRACEMA", ["IRACEMA_CS"], "COMPASS", "2026-09-09", [A("PAULA")],
     "PODE", ["AMARELO"], [["PAULA"], ["ITALO"]], ["CC art. 1.013", "CC art. 1.014"])
caso("C08", "Alçada por valor — abaixo do limite", "alcada",
     "Veículo de R$ 112 mil, limite R$ 150 mil: assinatura isolada vale.",
     "CARIRI", ["CARIRI_CS"], "MONTANA", "2026-09-17", [A("JOSEFA")],
     "PODE", ["VERDE"], [["ANTONIO"], ["JOSEFA"]], ["CC art. 1.015"])
caso("C09", "Alçada por valor — acima do limite", "alcada",
     "Veículo de R$ 215 mil, limite R$ 150 mil: exige os dois.",
     "CARIRI", ["CARIRI_CS"], "S10", "2026-09-17", [A("ANTONIO")],
     "NAO_PODE", ["VERMELHO"], [["ANTONIO", "JOSEFA"]], ["CC art. 47"])
caso("C10", "Alçada por valor — valor não informado", "alcada",
     "Sem o valor do veículo não dá para saber qual regra vale: faixa intermediária.",
     "CARIRI", ["CARIRI_CS"], "SW4", "2026-09-17", [A("ANTONIO")],
     "INDETERMINADO", ["AMARELO"], None, ["CC art. 47"])
caso("C11", "Ativo não circulante (inclui veículos) sem deliberação", "deliberacao",
     "Administrador tem poder, mas falta a aprovação prévia exigida (mais da metade do capital).",
     "CAMOCIM", ["CAMOCIM_CS"], "MASTER_C", "2026-09-24", [A("VALDIR")],
     "INDETERMINADO", ["AMARELO"], [["VALDIR"], ["MARCIA"]], ["CC art. 1.015", "CC art. 1.072"])
caso("C12", "Ativo não circulante com ata aprovando a venda", "deliberacao",
     "Ata com 65% do capital aprova a venda por no mínimo R$ 300 mil; venda por R$ 310 mil.",
     "CAMOCIM", ["CAMOCIM_CS", "CAMOCIM_ATA"], "DELIVERY", "2026-09-24", [A("MARCIA")],
     "PODE", ["VERDE"], [["VALDIR"], ["MARCIA"]], ["CC art. 1.072"])
caso("C13", "Carro integralizado pelo sócio — o OUTRO sócio vende sozinho", "bem_integralizado",
     "Exemplo do áudio: cláusula específica do veículo prevalece sobre a regra geral 'isoladamente'.",
     "PRIME", ["PRIME_CS"], "COROLLA", "2026-09-11", [A("LEONARDO")],
     "NAO_PODE", ["VERMELHO"], [["MARCOS"]], ["CC art. 997", "CC art. 47"])
caso("C14", "Carro integralizado pelo sócio — ele mesmo vende", "bem_integralizado",
     "Exemplo do áudio: só quem integralizou pode assinar, e é ele quem assina.",
     "PRIME", ["PRIME_CS"], "COROLLA", "2026-09-11", [A("MARCOS")],
     "PODE", ["VERDE"], [["MARCOS"]], ["CC art. 997"])
caso("C15", "Carro integralizado, mas o CRLV ainda está no CPF do sócio", "bem_integralizado",
     "Titularidade registral divergente: o ATPV sai em nome do proprietário no DETRAN.",
     "PRIME", ["PRIME_CS"], "COROLLA", "2026-09-11", [A("MARCOS")],
     "INDETERMINADO", ["AMARELO"], [["MARCOS"]], ["CTB art. 123"],
     crlv_proprietario={"tipo": "PF", "pessoa": "MARCOS"})
caso("C16", "Procuração pública válida com poderes especiais", "procuracao",
     "Delegação correta: outorgada pela PJ, poderes especiais e expressos, no prazo.",
     "JANGADA", ["JANGADA_CS", "POA_PEDRO"], "KWID", "2026-09-18", [A("PEDRO")],
     "PODE", ["VERDE"], [["FRANCISCO"], ["PEDRO"]], ["CC art. 661, §1º", "CC art. 1.018"])
caso("C17", "Procuração só com poderes gerais de administração", "procuracao",
     "'Amplos e gerais poderes', 'perante o DETRAN' — mas sem poder de alienar (art. 661).",
     "JANGADA", ["JANGADA_CS", "POA_RODRIGO"], "CRONOS", "2026-09-18", [A("RODRIGO")],
     "NAO_PODE", ["VERMELHO"], [["FRANCISCO"]], ["CC art. 661, caput e §1º"])
caso("C18", "Procuração vencida", "procuracao",
     "Prazo de 6 meses expirado antes da venda.",
     "MANDACARU", ["MANDACARU_CS", "POA_KLEBER_VENCIDA"], "SPRINTER", "2026-09-15", [A("KLEBER")],
     "NAO_PODE", ["VERMELHO"], [["CARLOS", "LUCIANA"]], ["CC art. 682, IV"])
caso("C19", "Procuração revogada", "procuracao",
     "Revogada por escritura pública antes da venda (revogada por outra administradora: vale, pois a outorgante é a PJ).",
     "CARIRI", ["CARIRI_CS", "POA_FABIO_REVOGADA", "REV_FABIO"], "SAVEIRO_C", "2026-09-20", [A("FABIO")],
     "NAO_PODE", ["VERMELHO"], [["ANTONIO"], ["JOSEFA"]], ["CC art. 682, I", "CC art. 686"])
caso("C20", "Procuração outorgada por quem não tinha poder sozinho", "procuracao",
     "Contrato exige os dois administradores; só um outorgou: ninguém delega mais poder do que tem.",
     "MANDACARU", ["MANDACARU_CS", "POA_KLEBER_SO_CARLOS"], "COROLLACROSS", "2026-09-25", [A("KLEBER")],
     "NAO_PODE", ["VERMELHO", "AMARELO"], [["CARLOS", "LUCIANA"]], ["CC art. 1.014", "CC art. 47"])
caso("C21", "Procuração do sócio em nome próprio (PF), não da empresa", "procuracao",
     "Semântica: o sócio outorgou como pessoa física para 'veículos de propriedade do outorgante'; o carro é da PJ.",
     "SERTAO", ["SERTAO_CS", "POA_PF_JOAO"], "DAILY", "2026-09-26", [A("KLEBER")],
     "NAO_PODE", ["VERMELHO", "AMARELO"], [["JOAO"], ["MARIA"]], ["CC art. 1.018", "CC art. 47"])
caso("C22", "Procuração para OUTRO veículo específico", "procuracao",
     "Procuração só para o Civic; a venda é do HR-V.",
     "TECH", ["TECH_CS", "POA_ANAPAULA_CIVIC"], "HRV", "2026-09-12", [A("ANAPAULA")],
     "NAO_PODE", ["VERMELHO"], [["RAFAEL"]], ["CC art. 661, §1º"])
caso("C23", "Substabelecimento com reserva, permitido", "substabelecimento",
     "Cadeia empresa → procurador → substabelecida, toda válida.",
     "JANGADA", ["JANGADA_CS", "POA_PEDRO", "SUB_PEDRO_ANAPAULA"], "TORO", "2026-09-18", [A("ANAPAULA")],
     "PODE", ["VERDE"], [["FRANCISCO"], ["PEDRO"], ["ANAPAULA"]], ["CC art. 667"])
caso("C24", "Substabelecimento vedado na procuração", "substabelecimento",
     "A procuração proíbe substabelecer: atos do substabelecido não obrigam a outorgante.",
     "TECH", ["TECH_CS", "POA_IGOR", "SUB_IGOR_KLEBER"], "AMAROK", "2026-09-22", [A("KLEBER")],
     "NAO_PODE", ["VERMELHO"], [["RAFAEL"], ["IGOR"]], ["CC art. 667, §3º"])
caso("C25", "Substabelecimento sem reserva — o procurador original assina", "substabelecimento",
     "Quem substabelece sem reserva perde os poderes.",
     "CARIRI", ["CARIRI_CS", "POA_FABIO_2026", "SUB_FABIO_ANAPAULA"], "STRADA_E", "2026-09-10", [A("FABIO")],
     "NAO_PODE", ["VERMELHO"], [["ANTONIO"], ["JOSEFA"], ["ANAPAULA"]], ["CC art. 667"])
caso("C26", "Procuração particular sem firma reconhecida", "forma",
     "Poderes corretos, mas a forma não é aceita pelo DETRAN/cartório sem reconhecimento: revisão.",
     "TECH", ["TECH_CS", "POA_CAMILA"], "PULSE", "2026-09-12", [A("CAMILA")],
     "PODE", ["AMARELO"], [["RAFAEL"], ["CAMILA"]], ["CC art. 654, §2º"],
     ce={"veredito": "NAO_PODE", "faixas_aceitaveis": ["VERMELHO"], "conjuntos_minimos": [["RAFAEL"]],
         "fundamentos": ["DETRAN-CE: procuração pública e específica"]})
caso("C27", "Procuradores que devem agir em conjunto — só um assina", "procuracao",
     "A procuração exige os dois outorgados juntos.",
     "MARACANAU", ["MARACANAU_CS", "POA_SERGIO_BRUNA"], "ATEGO", "2026-09-29", [A("SERGIO")],
     "NAO_PODE", ["VERMELHO"], [["GUSTAVO"], ["SERGIO", "BRUNA"]], ["CC art. 672"])
caso("C28", "Administrador que outorgou saiu da administração depois", "procuracao",
     "Mandato outorgado pela PJ não se extingue com a troca do administrador (art. 682).",
     "CHAPADA", ["CHAPADA_CS", "POA_DAVI", "CHAPADA_ALT1"], "FIORINO_C", "2026-09-08", [A("DAVI")],
     "PODE", ["VERDE", "AMARELO"], [["LUCIA"], ["DAVI"]], ["CC art. 682"])
caso("C29", "Alteração contratual mudou de isolada para conjunta", "temporal",
     "Vale a regra em vigor na data da venda (alteração de 2025), não a do contrato original.",
     "RUSSAS", ["RUSSAS_CS", "RUSSAS_ALT1"], "VOLVO", "2026-09-14", [A("HELIO")],
     "NAO_PODE", ["VERMELHO"], [["HELIO", "REGINA"]], ["CC art. 1.071", "Lei 8.934/94 art. 36"])
caso("C30", "Administrador com mandato por prazo determinado vencido", "temporal",
     "Prazo de 3 anos venceu em 2024 sem recondução nos documentos (art. 1.063).",
     "SOBRAL", ["SOBRAL_CS"], "DUCATO", "2026-09-16", [A("WAGNER")],
     "NAO_PODE", ["VERMELHO", "AMARELO"], [], ["CC art. 1.063"])
caso("C31", "Sociedade limitada unipessoal — sócio único assina", "estrutura",
     "SLU: o sócio único administrador assina.",
     "TECH", ["TECH_CS"], "CIVIC", "2026-09-12", [A("RAFAEL")],
     "PODE", ["VERDE"], [["RAFAEL"]], ["CC art. 1.052, §1º"])
caso("C32", "S.A. — um diretor sozinho", "estrutura",
     "Estatuto exige 2 diretores ou diretor + procurador.",
     "ARACATI", ["ARACATI_ESTATUTO", "ARACATI_RCA"], "CONSTELLATION", "2026-09-23", [A("MARCELO")],
     "NAO_PODE", ["VERMELHO"], [["MARCELO", "HELENA"], ["MARCELO", "TIAGO"], ["HELENA", "TIAGO"]],
     ["Lei 6.404/76 art. 144"])
caso("C33", "S.A. — diretor + procurador com procuração válida", "estrutura",
     "Combinação mista do estatuto: 1 diretor + 1 procurador.",
     "ARACATI", ["ARACATI_ESTATUTO", "ARACATI_RCA", "POA_SERGIO_SA"], "HILUX_SRV", "2026-09-23",
     [A("TIAGO"), A("SERGIO")],
     "PODE", ["VERDE"], [["MARCELO", "HELENA"], ["MARCELO", "TIAGO"], ["HELENA", "TIAGO"],
                         ["MARCELO", "SERGIO"], ["HELENA", "SERGIO"], ["TIAGO", "SERGIO"]],
     ["Lei 6.404/76 art. 144"])
caso("C34", "Empresário individual", "estrutura",
     "EI não é sociedade: o titular assina pelo CNPJ.",
     "JPSILVA", ["JPSILVA_REQ"], "CARGO", "2026-09-19", [A("JOSUE")],
     "PODE", ["VERDE"], [["JOSUE"]], ["CC art. 966"])
caso("C35", "Revendedora: restrição a ativo imobilizado x estoque", "deliberacao",
     "Venda de veículo é a atividade-fim da revendedora; se o carro é estoque, a restrição do imobilizado não se aplica — mas é preciso confirmar.",
     "BEIRAMAR", ["BEIRAMAR_CS"], "ONIX", "2026-09-27", [A("EDUARDO")],
     "PODE", ["AMARELO", "VERDE"], [["EDUARDO"]], ["CC art. 1.015"])
caso("C36", "Procuração válida — documentos ESCANEADOS (OCR)", "ocr",
     "Mesmo caso C16, mas a partir de imagens digitalizadas.",
     "JANGADA", ["JANGADA_CS", "POA_PEDRO"], "KWID", "2026-09-18", [A("PEDRO")],
     "PODE", ["VERDE", "AMARELO"], [["FRANCISCO"], ["PEDRO"]], ["CC art. 661, §1º"], ocr=True)
caso("C37", "Procuração antiga sem prazo (3 anos)", "forma",
     "Válida (sem prazo e não revogada), mas antiga: pedir certidão atualizada.",
     "MARACANAU", ["MARACANAU_CS", "POA_BRUNA_2023"], "MASTER_M", "2026-09-30", [A("BRUNA")],
     "PODE", ["AMARELO"], [["GUSTAVO"], ["BRUNA"]], ["CC art. 682"],
     ce={"veredito": "NAO_PODE", "faixas_aceitaveis": ["VERMELHO"], "conjuntos_minimos": [["GUSTAVO"]],
         "fundamentos": ["DETRAN-CE: validade de até 1 ano da expedição"]})
caso("C38", "Todos os sócios assinam (com exigência de deliberação)", "deliberacao",
     "'Se as duas partes estão, tudo está valendo': os 3 sócios (100%) assinando suprem a aprovação prévia.",
     "CAMOCIM", ["CAMOCIM_CS"], "HILUX_SR", "2026-09-24", [A("VALDIR"), A("MARCIA"), A("OSVALDO")],
     "PODE", ["VERDE", "AMARELO"], [["VALDIR"], ["MARCIA"]], ["CC art. 1.072"])


# =========================================================================== VALIDAÇÃO CEGA
# Cenários novos, com redações que o sistema nunca viu, criados DEPOIS do ajuste do motor e dos prompts.
# Gerados com RNG próprio (não alteram nenhum número dos cenários acima). Não ajustar o sistema com base neles.
rng_h = random.Random(4242)
_PH = [
    ("RAQUEL", "Raquel Mendes Bastos", "f", "casada", "empresária", "Tianguá/CE"),
    ("OTAVIO", "Otávio Bastos Neto", "m", "casado", "empresário", "Tianguá/CE"),
    ("LUCAS", "Lucas Ferreira Paz", "m", "casado", "designer de móveis", "Sobral/CE"),
    ("RENATA", "Renata Albuquerque Paz", "f", "casada", "arquiteta", "Sobral/CE"),
    ("CAIO", "Caio Ferreira Paz", "m", "solteiro", "marceneiro", "Sobral/CE"),
    ("IVAN", "Ivan Cordeiro Mota", "m", "casado", "transportador", "Aracati/CE"),
    ("SOLANGE", "Solange Prado Mota", "f", "casada", "empresária", "Aracati/CE"),
    ("HUGO", "Hugo Leitão Damasceno", "m", "divorciado", "empresário", "Fortaleza/CE"),
    ("PRISCILA", "Priscila Damasceno Rios", "f", "solteira", "gestora financeira", "Fortaleza/CE"),
    ("NILTON", "Nilton Arruda Coelho", "m", "casado", "despachante documentalista", "Fortaleza/CE"),
    ("VERA", "Vera Lúcia Holanda", "f", "viúva", "empresária", "Quixadá/CE"),
    ("JONAS", "Jonas Holanda Freire", "m", "solteiro", "engenheiro agrônomo", "Quixadá/CE"),
    ("TALITA", "Talita Freire Gurgel", "f", "solteira", "contadora", "Quixadá/CE"),
    ("BRENO", "Breno Sampaio Tavares", "m", "casado", "empresário", "Eusébio/CE"),
    ("CLARICE", "Clarice Tavares Mourão", "f", "casada", "empresária", "Eusébio/CE"),
]
for pid, nome, g, ec, prof, cid in _PH:
    PESSOAS[pid] = {"id": pid, "nome": nome, "genero": g, "nacionalidade": "brasileiro" if g == "m" else "brasileira",
                    "estado_civil": ec, "profissao": prof, "cidade": cid, "cpf": gerar_cpf(rng_h),
                    "rg": f"{rng_h.randint(1000000, 99999999)} SSP/CE"}
for vid, mm, fab, mod, cor, comb, esp, valor in [
    ("H_MASTER", "RENAULT/MASTER MINIBUS L3H2", 2023, 2023, "BRANCA", "DIESEL", "PASSAGEIRO/MICRO-ÔNIBUS", 285000),
    ("H_SAVEIRO", "VW/SAVEIRO CS 1.6", 2022, 2022, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 74000),
    ("H_ACTROS", "M.BENZ/ACTROS 2651 S 6X4", 2021, 2021, "PRATA", "DIESEL", "TRAÇÃO/CAMINHÃO TRATOR", 520000),
    ("H_RANGER", "FORD/RANGER XLS 2.2 4X4", 2022, 2022, "CINZA", "DIESEL", "CARGA/CAMINHONETE", 178000),
    ("H_DUSTER", "RENAULT/DUSTER INTENSE 1.6", 2022, 2023, "VERMELHA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 96000),
    ("H_L200", "MITSUBISHI/L200 TRITON SPORT HPE", 2023, 2023, "BRANCA", "DIESEL", "CARGA/CAMINHONETE", 245000),
    ("H_STRADA", "FIAT/STRADA VOLCANO 1.3 CD", 2024, 2024, "CINZA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 112000),
    ("H_ARRIZO", "CAOA CHERY/ARRIZO 6 PRO 1.5T", 2023, 2023, "PRETA", "GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 132000),
]:
    VEICULOS[vid] = {"id": vid, "marca_modelo": mm, "ano_fabricacao": fab, "ano_modelo": mod, "cor": cor, "combustivel": comb,
                     "especie_tipo": esp, "placa": gerar_placa(rng_h), "renavam": gerar_renavam(rng_h),
                     "chassi": gerar_chassi(rng_h, {"RENAULT": "93Y", "VW": "9BW", "M.BENZ": "9BM", "FORD": "9BF",
                                                    "MITSUBISHI": "93X", "FIAT": "9BD", "CAOA CHERY": "99A"}[mm.split("/")[0]]),
                     "valor": valor}
for eid, razao, tipo, cidade, objeto, capital, socios in [
    ("IBIAPABA", "LATICÍNIOS SERRA DA IBIAPABA LTDA.", "LTDA", "Tianguá/CE", "fabricação de laticínios e transporte refrigerado próprio", 450000, [("RAQUEL", 50), ("OTAVIO", 50)]),
    ("MOVEIS", "MÓVEIS SOBRAL DESIGN LTDA.", "LTDA", "Sobral/CE", "fabricação e comércio de móveis planejados", 300000, [("LUCAS", 40), ("RENATA", 35), ("CAIO", 25)]),
    ("LITORAL", "TRANSPORTADORA LITORAL LESTE LTDA.", "LTDA", "Aracati/CE", "transporte rodoviário de cargas", 900000, [("IVAN", 60), ("SOLANGE", 40)]),
    ("DAMASCENO", "DAMASCENO PARTICIPAÇÕES E SERVIÇOS LTDA.", "LTDA", "Fortaleza/CE", "gestão de ativos próprios e serviços de apoio administrativo", 1200000, [("HUGO", 70), ("PRISCILA", 30)]),
    ("SERTANEJA", "AGRÍCOLA SERTANEJA DE QUIXADÁ LTDA.", "LTDA", "Quixadá/CE", "cultivo de frutas e comércio de insumos agrícolas", 650000, [("VERA", 50), ("JONAS", 25), ("TALITA", 25)]),
    ("TAVARES", "TAVARES & MOURÃO EVENTOS LTDA.", "LTDA", "Eusébio/CE", "organização de eventos e locação de estruturas", 220000, [("BRENO", 50), ("CLARICE", 50)]),
]:
    EMPRESAS[eid] = {"id": eid, "razao_social": razao, "tipo": tipo, "cidade": cidade, "objeto": objeto, "capital": capital,
                     "socios": socios, "cnpj": gerar_cnpj(rng_h), "nire": f"23{rng_h.randint(100000000, 999999999)}"}


def reg_h(data):
    return {"orgao": "JUCEC – Junta Comercial do Estado do Ceará", "data": data,
            "numero": f"{rng_h.randint(10000000, 99999999)}{rng_h.randint(100, 999)}"}


doc("IBIAPABA_CS", "contrato_social", "IBIAPABA", "2020-10-05", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('RAQUEL')} (50%) e {N('OTAVIO')} (50%).",
     "Administração pelos dois sócios, cada um de per si (frase obrigatória) — significa atuação isolada.",
     SEM_OUTRAS_REGRAS], ["podendo cada um deles, de per si, representar a sociedade"], registro=reg_h("2020-10-19"))
doc("MOVEIS_CS", "contrato_social", "MOVEIS", "2021-06-14", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('LUCAS')} (40%), {N('RENATA')} (35%) e {N('CAIO')} (25%), os três administradores.",
     "Representação: quaisquer dois dos três administradores em conjunto (frase obrigatória).", SEM_OUTRAS_REGRAS],
    ["mediante a assinatura conjunta de quaisquer dois dos três administradores"], registro=reg_h("2021-06-28"))
doc("LITORAL_CS", "contrato_social", "LITORAL", "2019-08-26", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('IVAN')} (60%) e {N('SOLANGE')} (40%), ambos administradores com atuação isolada em geral (frase 1).",
     "Parágrafo específico para veículos da frota, sem valor: venda só com assinatura conjunta dos dois (frase 2).",
     SEM_OUTRAS_REGRAS],
    ["qualquer deles poderá praticar isoladamente os atos de gestão",
     "Os veículos integrantes da frota somente poderão ser vendidos mediante a assinatura conjunta de ambos os sócios administradores"],
    registro=reg_h("2019-09-09"))
doc("DAMASCENO_CS", "contrato_social", "DAMASCENO", "2022-03-21", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('HUGO')} (70%, administrador isolado) e {N('PRISCILA')} (30%, quotista).",
     "Restrição (frase obrigatória): imóveis e participações societárias dependem de 3/4 do capital (não fala de veículos).",
     SEM_OUTRAS_REGRAS],
    ["a alienação de bens imóveis e de participações societárias detidas pela sociedade dependerá de deliberação de sócios representando três quartos do capital social"],
    registro=reg_h("2022-04-04"))
doc("SERTANEJA_CS", "contrato_social", "SERTANEJA", "2018-02-12", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('VERA')} (50%), {N('JONAS')} (25%) e {N('TALITA')} (25%). Administradora única: {N('VERA')}, isoladamente.",
     SEM_OUTRAS_REGRAS], ["A administração da sociedade compete exclusivamente à sócia VERA LÚCIA HOLANDA"], registro=reg_h("2018-02-26"))
doc("SERTANEJA_ALT2", "alteracao_contratual", "SERTANEJA", "2026-03-09", "SEGUNDA ALTERAÇÃO DO CONTRATO SOCIAL",
    [f"{N('VERA')} deixa a administração (continua sócia). {N('JONAS')} passa a ser o administrador único, isoladamente (frase obrigatória).",
     "Mencione que a primeira alteração (2022) tratou apenas de endereço. Demais cláusulas inalteradas.", SEM_OUTRAS_REGRAS],
    ["passa a ser exercida exclusivamente pelo sócio JONAS HOLANDA FREIRE"], registro=reg_h("2026-03-20"), palavras=(500, 900))
doc("TAVARES_CS", "contrato_social", "TAVARES", "2023-05-02", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('BRENO')} (50%) e {N('CLARICE')} (50%), administradores que assinam sempre em conjunto (frase 1).",
     "Procurações da sociedade: outorgadas pelos dois administradores em conjunto, com prazo máximo de 12 meses (frase 2).",
     SEM_OUTRAS_REGRAS],
    ["a sociedade somente se obriga pela assinatura conjunta de ambos os administradores",
     "As procurações em nome da sociedade serão outorgadas pelos dois administradores em conjunto e terão prazo não superior a 12 (doze) meses"],
    registro=reg_h("2023-05-16"))
procuracao("POA_H_NILTON_12M", "2025-08-20", "LITORAL",
           f"{RAZAO('LITORAL')} (CNPJ {EMPRESAS['LITORAL']['cnpj']}), representada CONJUNTAMENTE por {N('IVAN')} e {N('SOLANGE')}",
           ["NILTON"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "pelo período de doze meses contados desta data (frase obrigatória)", "omisso (não mencione)", "publica",
           ["pelo período de doze meses"])
procuracao("POA_H_PRISCILA_SEMSUB", "2026-04-10", "DAMASCENO",
           f"{RAZAO('DAMASCENO')} (CNPJ {EMPRESAS['DAMASCENO']['cnpj']}), representada por seu sócio administrador {N('HUGO')}",
           ["PRISCILA"], f"poderes especiais e expressos para {PODERES_VEICULO}",
           "1 (um) ano", "sem direito de substabelecer (frase obrigatória)", "publica", ["sem direito de substabelecer"])
doc("SUB_H_PRISCILA_NILTON", "substabelecimento", "DAMASCENO", "2026-08-25", "SUBSTABELECIMENTO DE PROCURAÇÃO",
    [f"SUBSTABELECIMENTO POR INSTRUMENTO PÚBLICO em {CARTORIOS['IRACEMA']}.",
     f"Substabelecente: {N('PRISCILA')}, procuradora de {RAZAO('DAMASCENO')} pela procuração pública de 10/04/2026 do mesmo cartório (livro/folhas fictícios).",
     f"Substabelecido: {N('NILTON')} (CPF {PESSOAS['NILTON']['cpf']}). Com reserva de poderes. NÃO mencione a restrição da procuração original."],
    ["com reserva"], palavras=(200, 400))
procuracao("POA_H_TAVARES_ARRIZO", "2026-06-15", "TAVARES",
           f"{RAZAO('TAVARES')} (CNPJ {EMPRESAS['TAVARES']['cnpj']}), representada CONJUNTAMENTE por seus administradores {N('BRENO')} e {N('CLARICE')}",
           ["NILTON"], f"poderes especiais e expressos para vender o veículo {VEIC('H_ARRIZO')}, assinar a respectiva ATPV-e, receber o preço e dar quitação",
           "6 (seis) meses", "omisso (não mencione)", "publica", [VEICULOS["H_ARRIZO"]["placa"]])

CASOS_HOLDOUT: list[dict] = []
_casos_principais = CASOS
CASOS = CASOS_HOLDOUT
caso("H01", "‘De per si’ — um administrador assina", "administracao", "Sinônimo novo de atuação isolada.",
     "IBIAPABA", ["IBIAPABA_CS"], "H_MASTER", "2026-09-15", [A("OTAVIO")], "PODE", ["VERDE"], [["RAQUEL"], ["OTAVIO"]], [])
caso("H02", "Quaisquer dois dos três administradores — um assina", "administracao", "k-de-n com redação nova.",
     "MOVEIS", ["MOVEIS_CS"], "H_SAVEIRO", "2026-09-16", [A("RENATA")], "NAO_PODE", ["VERMELHO"],
     [["LUCAS", "RENATA"], ["LUCAS", "CAIO"], ["RENATA", "CAIO"]], [])
caso("H03", "Veículos da frota exigem os dois (sem valor) — um assina", "alcada", "Cláusula específica de veículos sem alçada.",
     "LITORAL", ["LITORAL_CS"], "H_ACTROS", "2026-09-17", [A("IVAN")], "NAO_PODE", ["VERMELHO"], [["IVAN", "SOLANGE"]], [])
caso("H04", "Procuração ‘pelo período de doze meses’ vencida", "procuracao", "Prazo escrito de forma nova; venceu.",
     "LITORAL", ["LITORAL_CS", "POA_H_NILTON_12M"], "H_RANGER", "2026-09-05", [A("NILTON")], "NAO_PODE", ["VERMELHO"],
     [["IVAN", "SOLANGE"]], [])
caso("H05", "‘Sem direito de substabelecer’ e houve substabelecimento", "substabelecimento", "Vedação com redação nova.",
     "DAMASCENO", ["DAMASCENO_CS", "POA_H_PRISCILA_SEMSUB", "SUB_H_PRISCILA_NILTON"], "H_DUSTER", "2026-09-22", [A("NILTON")],
     "NAO_PODE", ["VERMELHO"], [["HUGO"], ["PRISCILA"]], [])
caso("H06", "Procuração conjunta, veículo identificado, no prazo", "procuracao", "Outorga correta pelos dois administradores.",
     "TAVARES", ["TAVARES_CS", "POA_H_TAVARES_ARRIZO"], "H_ARRIZO", "2026-09-25", [A("NILTON")], "PODE", ["VERDE"],
     [["BRENO", "CLARICE"], ["NILTON"]], [])
caso("H07", "Antiga administradora assina depois da troca", "temporal", "Segunda alteração mudou o administrador.",
     "SERTANEJA", ["SERTANEJA_CS", "SERTANEJA_ALT2"], "H_L200", "2026-09-18", [A("VERA")], "NAO_PODE", ["VERMELHO"], [["JONAS"]], [])
caso("H08", "Restrição a imóveis e participações; veículo de R$ 320 mil", "administracao", "Armadilha: nada sobre veículos.",
     "DAMASCENO", ["DAMASCENO_CS"], "H_STRADA", "2026-09-29", [A("HUGO")], "PODE", ["VERDE"], [["HUGO"]], [], valor=320000)
CASOS = _casos_principais


# =========================================================================== LOTE ATPV-e (respostas do chefe, 17/10/2026)
# "antes de assinar a ATPV-e saber se a pessoa tem o poder de assinar vendendo ou comprando"; "todos os tipos de
# empresas"; "foque só no digital". Comprador PJ, PJ dos dois lados, cooperativa, associação, MEI, EIRELI e sociedade
# simples; a ATPV-e simulada é a entrada principal (o pedido traz só quem vai assinar). RNG próprio: não altera nenhum
# número acima. A primeira rodada da IA nestes documentos é medição cega da leitura.
rng_a = random.Random(1710)
_PA = [
    ("GILBERTO", "Gilberto Araújo Nunes", "m", "casado", "comerciante", "Fortaleza/CE"),
    ("SIMONE", "Simone Batista Nunes", "f", "casada", "comerciante", "Fortaleza/CE"),
    ("ELIAS", "Elias Rodrigues Maia", "m", "solteiro", "gerente de compras", "Caucaia/CE"),
    ("MANOEL", "Manoel Messias Freitas", "m", "casado", "motorista profissional", "Limoeiro do Norte/CE"),
    ("JOANA", "Joana Darc Ribeiro", "f", "casada", "motorista profissional", "Limoeiro do Norte/CE"),
    ("CICERO", "Cícero Romão Bezerra", "m", "casado", "motorista profissional", "Russas/CE"),
    ("EXPEDITO", "Expedito Lima Cordeiro", "m", "viúvo", "técnico em contabilidade", "Limoeiro do Norte/CE"),
    ("SOCORRO", "Maria do Socorro Viana", "f", "casada", "assistente social", "Quixeramobim/CE"),
    ("FRANCISCA", "Francisca Lúcia Matos", "f", "solteira", "professora", "Quixeramobim/CE"),
    ("PAULO", "Paulo Sérgio Viana", "m", "casado", "comerciante", "Quixeramobim/CE"),
    ("ROGERIO", "Rogério Fernandes Lima", "m", "casado", "motorista autônomo", "Maranguape/CE"),
    ("CLAUDIA", "Cláudia Mendes Lima", "f", "casada", "costureira", "Maranguape/CE"),
    ("WELLINGTON", "Wellington Oliveira Sá", "m", "casado", "engenheiro civil", "Juazeiro do Norte/CE"),
    ("LARISSA", "Larissa Gomes Pinho", "f", "solteira", "fisioterapeuta", "Fortaleza/CE"),
    ("THIAGO", "Thiago Pinho Arruda", "m", "casado", "fisioterapeuta", "Fortaleza/CE"),
    ("NADIA", "Nádia Rocha Bessa", "f", "solteira", "professora", "Fortaleza/CE"),
    ("DEBORA", "Débora Lins Moura", "f", "casada", "enfermeira", "Fortaleza/CE"),
]
for pid, nome, g, ec, prof, cid in _PA:
    PESSOAS[pid] = {"id": pid, "nome": nome, "genero": g, "nacionalidade": "brasileiro" if g == "m" else "brasileira",
                    "estado_civil": ec, "profissao": prof, "cidade": cid, "cpf": gerar_cpf(rng_a),
                    "rg": f"{rng_a.randint(1000000, 99999999)} SSP/CE"}
for vid, mm, fab, mod, cor, comb, esp, valor in [
    ("A_ONIX", "GM/ONIX PLUS LTZ 1.0 TURBO", 2023, 2023, "PRATA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 89000),
    ("A_HILUX", "TOYOTA/HILUX CD SRX 4X4 2.8", 2024, 2024, "BRANCA", "DIESEL", "CARGA/CAMINHONETE", 289000),
    ("A_TORO", "FIAT/TORO ENDURANCE 1.3 TURBO", 2023, 2023, "CINZA", "ÁLCOOL/GASOLINA", "CARGA/CAMINHONETE", 135000),
    ("A_DUCATO", "FIAT/DUCATO MAXICARGO 2.3", 2022, 2022, "BRANCA", "DIESEL", "CARGA/FURGÃO", 185000),
    ("A_ARGO", "FIAT/ARGO DRIVE 1.0", 2023, 2023, "VERMELHA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 79000),
    ("A_SAVEIRO", "VW/SAVEIRO ROBUST CS 1.6", 2023, 2023, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 86000),
    ("A_S10", "GM/S10 CD LT 2.8 4X4", 2022, 2022, "PRATA", "DIESEL", "CARGA/CAMINHONETE", 198000),
    ("A_VOLARE", "MARCOPOLO/VOLARE W9 ESCOLAR", 2021, 2021, "AMARELA", "DIESEL", "PASSAGEIRO/MICRO-ÔNIBUS", 310000),
    ("A_SPRINTER", "M.BENZ/SPRINTER 516 ESCOLAR", 2020, 2020, "AMARELA", "DIESEL", "PASSAGEIRO/MICRO-ÔNIBUS", 240000),
    ("A_SPIN", "GM/SPIN PREMIER 1.8", 2023, 2023, "BRANCA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 98000),
    ("A_FIORINO", "FIAT/FIORINO ENDURANCE 1.4", 2022, 2022, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/FURGÃO", 82000),
    ("A_STRADA", "FIAT/STRADA ENDURANCE 1.3 CS", 2024, 2024, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 99000),
    ("A_RANGER", "FORD/RANGER XLT 3.2 4X4", 2021, 2021, "PRETA", "DIESEL", "CARGA/CAMINHONETE", 195000),
    ("A_RENEGADE", "JEEP/RENEGADE LONGITUDE 1.3 T270", 2023, 2023, "CINZA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 128000),
]:
    VEICULOS[vid] = {"id": vid, "marca_modelo": mm, "ano_fabricacao": fab, "ano_modelo": mod, "cor": cor, "combustivel": comb,
                     "especie_tipo": esp, "placa": gerar_placa(rng_a), "renavam": gerar_renavam(rng_a),
                     "chassi": gerar_chassi(rng_a, {"GM": "9BG", "TOYOTA": "9BR", "FIAT": "9BD", "VW": "9BW", "MARCOPOLO": "9BS",
                                                    "M.BENZ": "9BM", "FORD": "9BF", "JEEP": "988"}[mm.split("/")[0]]),
                     "valor": valor}
for eid, razao, tipo, cidade, objeto, capital, socios in [
    ("BOMJARDIM", "COMERCIAL BOM JARDIM LTDA.", "LTDA", "Fortaleza/CE",
     "comércio atacadista de produtos alimentícios e distribuição com frota própria", 400000, [("GILBERTO", 50), ("SIMONE", 50)]),
    ("COOPVALE", "COOPERATIVA DE TRANSPORTE ESCOLAR DO VALE DO JAGUARIBE – COOPVALE", "COOPERATIVA", "Limoeiro do Norte/CE",
     "prestação de serviços de transporte escolar e de passageiros por meio dos cooperados", 60000, []),
    ("ASSOC", "ASSOCIAÇÃO COMUNITÁRIA AMIGOS DO SERTÃO CENTRAL", "ASSOCIACAO", "Quixeramobim/CE",
     "assistência social e promoção de atividades educativas, culturais e de saúde comunitária, sem fins lucrativos", 0, []),
    ("MEI", "", "EI", "Maranguape/CE", "transporte municipal de cargas não perigosas (carreto) e de mudanças", 5000, [("ROGERIO", 100)]),
    ("EIRELI", "OLIVEIRA SÁ ENGENHARIA EIRELI", "EIRELI", "Juazeiro do Norte/CE",
     "serviços de engenharia civil, elaboração de projetos e gerenciamento de obras", 150000, [("WELLINGTON", 100)]),
    ("PINHO", "PINHO & ARRUDA FISIOTERAPIA S/S", "SS", "Fortaleza/CE",
     "prestação de serviços de fisioterapia e reabilitação, exercidos pessoalmente pelos sócios", 80000, [("LARISSA", 50), ("THIAGO", 50)]),
]:
    EMPRESAS[eid] = {"id": eid, "razao_social": razao, "tipo": tipo, "cidade": cidade, "objeto": objeto, "capital": capital,
                     "socios": socios, "cnpj": gerar_cnpj(rng_a), "nire": f"23{rng_a.randint(100000000, 999999999)}"}
# MEI: o nome empresarial é a raiz do CNPJ seguida do nome civil do titular, sem acentos
EMPRESAS["MEI"]["razao_social"] = f"{EMPRESAS['MEI']['cnpj'][:10]} ROGERIO FERNANDES LIMA"
EMPRESAS["MEI"]["nome_fantasia"] = "ROGÉRIO FRETES E MUDANÇAS"
CARTORIOS["RCPJ_QXB"] = "Cartório Dom Bosco – Registro Civil das Pessoas Jurídicas de Quixeramobim/CE (fictício)"
CARTORIOS["RCPJ_FOR"] = "Cartório Alencar – 2º Registro Civil das Pessoas Jurídicas de Fortaleza (fictício)"


def reg_a(data):
    return {"orgao": "JUCEC – Junta Comercial do Estado do Ceará", "data": data,
            "numero": f"{rng_a.randint(10000000, 99999999)}{rng_a.randint(100, 999)}"}


def reg_rcpj(data, cartorio):
    return {"orgao": CARTORIOS[cartorio], "data": data, "numero": f"{rng_a.randint(10000, 99999)}"}


CHANCELA_RCPJ = ("Em vez da chancela da Junta Comercial, termine com a certidão de registro do cartório de pessoas jurídicas, "
                 "neste formato: 'REGISTRO CIVIL DAS PESSOAS JURÍDICAS' / nome do cartório / 'Protocolado e registrado sob o nº "
                 "<registro.numero>, no Livro A, em DD/MM/AAAA' / nome do oficial (fictício) / selo digital inventado.")

doc("BOMJARDIM_CS", "contrato_social", "BOMJARDIM", "2021-09-13", "CONTRATO SOCIAL DE CONSTITUIÇÃO",
    [f"Sócios: {N('GILBERTO')} (50% – R$ 200.000,00) e {N('SIMONE')} (50% – R$ 200.000,00), capital integralizado em moeda corrente.",
     "Administração (frase obrigatória 1): os dois sócios são administradores e atuam isoladamente em todos os atos de gestão, inclusive a venda de bens da sociedade.",
     "Parágrafo da cláusula de administração (frase obrigatória 2): a COMPRA de veículos, máquinas e equipamentos acima de R$ 100.000,00 por unidade exige a assinatura dos dois administradores. Atenção: a restrição é só para ADQUIRIR; NÃO crie restrição para vender.",
     SEM_OUTRAS_REGRAS],
    ["que a exercerão isoladamente, cada um deles com plenos poderes de gestão",
     "A aquisição de veículos, máquinas e equipamentos de valor unitário superior a R$ 100.000,00 (cem mil reais) dependerá da assinatura conjunta de ambos os administradores"],
    registro=reg_a("2021-09-24"))

procuracao("POA_ELIAS_COMPRA", "2026-07-20", "JANGADA",
           f"{RAZAO('JANGADA')} (CNPJ {EMPRESAS['JANGADA']['cnpj']}), representada por seu sócio administrador {N('FRANCISCO')}",
           ["ELIAS"],
           "poderes especiais e expressos para comprar, adquirir ou receber em transferência veículos automotores para a "
           "outorgante, em nome dela, pelo preço e condições que ajustar, assinar como comprador a Autorização para "
           "Transferência de Propriedade do Veículo (ATPV-e), pagar o preço, receber os veículos e seus documentos e requerer "
           "perante o DETRAN a transferência para o nome da outorgante (frase obrigatória 1). Inclua também a frase "
           "obrigatória 2, que deixa claro que NÃO há poder de venda",
           "1 (um) ano", "omisso (não mencione)", "publica",
           ["assinar como comprador a Autorização para Transferência de Propriedade do Veículo (ATPV-e)",
            "Esta procuração não confere poderes para vender, alienar ou onerar bens da outorgante"],
           cartorio="JANGADEIRO")

doc("COOPVALE_ESTATUTO", "estatuto_social", "COOPVALE", "2019-04-26", "ESTATUTO SOCIAL",
    ["Estatuto de cooperativa singular de trabalho/serviços regida pela Lei nº 5.764/1971 e pelos arts. 1.093 a 1.096 do Código Civil. Capítulos e artigos (Art. 1º...): denominação, sede, área de ação, objeto, cooperados (admissão, deveres, eliminação), capital social em quotas-partes, Assembleia Geral (ordinária e extraordinária), Conselho de Administração, Conselho Fiscal, fundos (Reserva e FATES), balanço e sobras, dissolução.",
     "O Conselho de Administração é composto por Diretor-Presidente, Vice-Presidente, Secretário e Diretor Financeiro, eleitos pela Assembleia Geral para mandato de 4 (quatro) anos, com renovação obrigatória de, no mínimo, 1/3 (um terço) (frase obrigatória 1). NÃO nomeie as pessoas: os diretores são eleitos em ata separada.",
     "Representação (frase obrigatória 2): o Diretor-Presidente representa a Cooperativa, mas documentos que criem obrigações ou importem alienação de bens são assinados pelo Diretor-Presidente EM CONJUNTO com o Diretor Financeiro.",
     "Competência da Assembleia Geral (frase obrigatória 3): só para bens IMÓVEIS (é uma armadilha semântica: não alcança veículos).",
     "Atas e alterações estatutárias são arquivadas na Junta Comercial (cooperativas registram-se na JUCEC).",
     SEM_OUTRAS_REGRAS],
    ["eleitos pela Assembleia Geral para mandato de 4 (quatro) anos",
     "serão assinados pelo Diretor-Presidente em conjunto com o Diretor Financeiro",
     "deliberar sobre a alienação ou oneração de bens imóveis da Cooperativa"],
    registro=reg_a("2019-05-10"), palavras=(1200, 2000))

doc("COOPVALE_ATA_AGO", "ata_assembleia", "COOPVALE", "2025-03-28", "ATA DA ASSEMBLEIA GERAL ORDINÁRIA",
    [f"Assembleia Geral Ordinária da {RAZAO('COOPVALE')} realizada em 28/03/2025, às 19h, em terceira convocação, com 23 cooperados presentes de 41 (lista anexa), presidida pelo Diretor-Presidente em fim de mandato (invente um nome que NÃO é eleito agora) e secretariada por um cooperado.",
     "Ordem do dia: prestação de contas de 2024, destinação das sobras e eleição do Conselho de Administração e do Conselho Fiscal.",
     f"Eleição (frase obrigatória): eleitos para o Conselho de Administração, para o mandato de 4 (quatro) anos, até a AGO de 2029: Diretor-Presidente {N('MANOEL')} (CPF {PESSOAS['MANOEL']['cpf']}); Vice-Presidente {N('JOANA')} (CPF {PESSOAS['JOANA']['cpf']}); Secretário {N('CICERO')} (CPF {PESSOAS['CICERO']['cpf']}); Diretor Financeiro {N('EXPEDITO')} (CPF {PESSOAS['EXPEDITO']['cpf']}). Termo de posse na mesma data.",
     "Inclua também a eleição de 3 membros efetivos do Conselho Fiscal (invente nomes; não são administradores).",
     "Encerramento, lavratura, assinaturas e chancela da JUCEC (ata de eleição de cooperativa é arquivada na Junta)."],
    ["para o mandato de 4 (quatro) anos"], registro=reg_a("2025-04-08"), palavras=(600, 1000))

doc("ASSOC_ESTATUTO", "estatuto_social", "ASSOC", "2017-08-05", "ESTATUTO SOCIAL",
    ["Estatuto de associação civil sem fins lucrativos (Código Civil, arts. 53 a 61): denominação, sede, finalidades, associados (admissão, direitos, deveres, exclusão), fontes de recursos, órgãos (Assembleia Geral, Diretoria e Conselho Fiscal), patrimônio, prestação de contas, dissolução com destinação do patrimônio a entidade congênere.",
     "Diretoria composta por Presidente, Vice-Presidente, Secretário e Tesoureiro, eleitos pela Assembleia Geral para mandato de 3 (três) anos; NÃO nomeie as pessoas (são eleitas em ata separada).",
     "Competências do Presidente (frase obrigatória 1): representar a Associação, sozinho, ativa e passivamente.",
     "Restrição (frase obrigatória 2): só bens IMÓVEIS dependem da Assembleia (armadilha semântica: não alcança veículos).",
     "Os associados não respondem, nem subsidiariamente, pelas obrigações da Associação.",
     CHANCELA_RCPJ, SEM_OUTRAS_REGRAS],
    ["Compete ao Presidente representar a Associação ativa e passivamente, judicial e extrajudicialmente",
     "A alienação ou oneração de bens imóveis da Associação dependerá de aprovação da Assembleia Geral"],
    registro=reg_rcpj("2017-08-21", "RCPJ_QXB"), palavras=(1000, 1800))

doc("ASSOC_ATA_ELEICAO", "ata_assembleia", "ASSOC", "2024-02-17", "ATA DA ASSEMBLEIA GERAL DE ELEIÇÃO",
    [f"Assembleia Geral da {RAZAO('ASSOC')} realizada em 17/02/2024, com 58 associados presentes, para eleição e posse da Diretoria e do Conselho Fiscal.",
     f"Eleição (frase obrigatória): chapa única eleita por aclamação para o triênio 2024/2027: Presidente {N('SOCORRO')} (CPF {PESSOAS['SOCORRO']['cpf']}); Vice-Presidente {N('FRANCISCA')} (CPF {PESSOAS['FRANCISCA']['cpf']}); Tesoureiro {N('PAULO')} (CPF {PESSOAS['PAULO']['cpf']}); Secretária (invente um nome). Mandato até 16/02/2027. Posse imediata.",
     "Conselho Fiscal com 3 membros (invente nomes).",
     CHANCELA_RCPJ],
    ["para o triênio 2024/2027"], registro=reg_rcpj("2024-03-01", "RCPJ_QXB"), palavras=(450, 800))

doc("MEI_CCMEI", "requerimento_empresario", "MEI", "2021-06-01", "CERTIFICADO DA CONDIÇÃO DE MICROEMPREENDEDOR INDIVIDUAL",
    ["Formulário do CCMEI (Portal do Empreendedor), com campos rotulados um por linha: Nome Empresarial; Nome do Empresário; Nome Fantasia; CNPJ; Data de Início das Atividades (01/06/2021); Situação Cadastral Vigente (ATIVA); Número do Registro (NIRE); CPF; Identidade; Forma de Atuação (estabelecimento fixo e porta a porta); Ocupação Principal ('Transportador municipal de cargas não perigosas (carreto)'); Ocupação Secundária ('Transportador de mudanças'); Endereço Comercial; Capital Social (R$ 5.000,00).",
     "Bloco de declarações do empresário (desimpedimento, enquadramento como MEI na LC 123/2006, art. 18-A) e a observação de que o CCMEI dispensa assinatura e é válido com a verificação de autenticidade no Portal.",
     "Rodapé: 'Certificado emitido em 12/08/2026' (invente o código de autenticidade). Use a frase obrigatória como título."],
    ["CERTIFICADO DA CONDIÇÃO DE MICROEMPREENDEDOR INDIVIDUAL"], palavras=(250, 550))

doc("EIRELI_ATO", "ato_constitutivo_eireli", "EIRELI", "2019-09-02",
    "ATO CONSTITUTIVO DE EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA",
    [f"Titular: {N('WELLINGTON')}, constitui EIRELI (Código Civil, art. 980-A, vigente em 2019) com capital de R$ 150.000,00, integralizado em moeda corrente.",
     "Administração (frase obrigatória 2): pelo titular, isoladamente, por prazo indeterminado.",
     "Cláusulas: nome empresarial, sede, objeto, prazo, capital, responsabilidade limitada ao capital, administração, pró-labore, exercício social, declaração de que o titular não participa de outra EIRELI, foro.",
     SEM_OUTRAS_REGRAS],
    ["EMPRESA INDIVIDUAL DE RESPONSABILIDADE LIMITADA",
     "A administração da empresa caberá ao titular WELLINGTON OLIVEIRA SÁ, que a exercerá isoladamente"],
    registro=reg_a("2019-09-16"))

doc("PINHO_CS", "contrato_social", "PINHO", "2022-05-09", "CONTRATO SOCIAL DE SOCIEDADE SIMPLES",
    [f"Sócios: {N('LARISSA')} (50%) e {N('THIAGO')} (50%), ambos fisioterapeutas com registro no CREFITO-6 (invente os números); capital R$ 80.000,00.",
     "Sociedade simples pura (Código Civil, arts. 997 a 1.038), de natureza não empresária, registrada no Registro Civil das Pessoas Jurídicas; os sócios respondem subsidiariamente pelas obrigações sociais (art. 1.023) (frase obrigatória 1).",
     "Administração (frase obrigatória 2): os dois sócios, que só obrigam a sociedade com a assinatura de ambos.",
     CHANCELA_RCPJ, SEM_OUTRAS_REGRAS],
    ["sociedade simples",
     "A administração da sociedade compete a ambos os sócios, que somente poderão obrigá-la mediante a assinatura de ambos"],
    registro=reg_rcpj("2022-05-23", "RCPJ_FOR"))

CASOS_ATPV: list[dict] = []


def caso_atpv(cid, titulo, categoria, objetivo, docs, veiculo, data_venda, vendedor, comprador, esperado, lados,
              crlv_proprietario=None, valor="padrao", assinaturas_na_atpv=False):
    """vendedor/comprador: {"empresa": EID, "assinantes": [...]} (PJ) ou {"pessoa": PID} (PF).
    esperado: resultado combinado (o elo mais fraco); lados: o esperado de cada lado PJ."""
    v = VEICULOS[veiculo]
    dono = crlv_proprietario or ({"tipo": "PJ", "empresa": vendedor["empresa"]} if "empresa" in vendedor
                                 else {"tipo": "PF", "pessoa": vendedor["pessoa"]})
    CASOS_ATPV.append({
        "id": cid, "titulo": titulo, "categoria": categoria, "objetivo": objetivo, "documentos": docs, "veiculo": veiculo,
        "ocr": False, "crlv_proprietario": dono,
        "vendedor": vendedor, "comprador": comprador, "assinaturas_na_atpv": assinaturas_na_atpv,
        "transacao": {"data_venda": data_venda, "valor": v["valor"] if valor == "padrao" else valor},
        "atpv_numero": f"{rng_a.randint(10**11, 10**12 - 1)}",
        "esperado": {"veredito": esperado[0], "faixas_aceitaveis": esperado[1], "conjuntos_minimos": None, "fundamentos": []},
        "esperado_lados": {k: {"veredito": e[0], "faixas_aceitaveis": e[1], "conjuntos_minimos": e[2], "fundamentos": []}
                           for k, e in lados.items()},
        "esperado_ce": None,
    })


def PJ(eid, *assinantes):
    return {"empresa": eid, "assinantes": list(assinantes)}


def PF(pid):
    return {"pessoa": pid}


caso_atpv("A01", "Comprador PJ: administrador assina compra abaixo da alçada", "comprador",
          "Restrição de COMPRA acima de R$ 100 mil; veículo de R$ 89 mil: um administrador basta.",
          ["BOMJARDIM_CS"], "A_ONIX", "2026-10-05", PF("NADIA"), PJ("BOMJARDIM", A("GILBERTO", "GILBERTO A NUNES")),
          ("PODE", ["VERDE"]), {"comprador": ("PODE", ["VERDE"], [["GILBERTO"], ["SIMONE"]])})
caso_atpv("A02", "Comprador PJ: compra acima da alçada com um só administrador", "comprador",
          "A aquisição acima de R$ 100 mil exige os dois administradores.",
          ["BOMJARDIM_CS"], "A_HILUX", "2026-10-06", PF("NADIA"), PJ("BOMJARDIM", A("GILBERTO")),
          ("NAO_PODE", ["VERMELHO"]), {"comprador": ("NAO_PODE", ["VERMELHO"], [["GILBERTO", "SIMONE"]])})
caso_atpv("A03", "Restrição de compra não alcança a venda", "comprador",
          "Armadilha: a mesma empresa VENDE um veículo de R$ 135 mil; a cláusula é só para aquisição.",
          ["BOMJARDIM_CS"], "A_TORO", "2026-10-07", PJ("BOMJARDIM", A("SIMONE")), PF("DEBORA"),
          ("PODE", ["VERDE"]), {"vendedor": ("PODE", ["VERDE"], [["GILBERTO"], ["SIMONE"]])})
caso_atpv("A04", "Comprador PJ por procurador com poder de compra", "comprador",
          "Procuração pública com poderes especiais para adquirir veículos e assinar a ATPV-e como comprador.",
          ["JANGADA_CS", "POA_ELIAS_COMPRA"], "A_DUCATO", "2026-10-08", PF("NADIA"), PJ("JANGADA", A("ELIAS")),
          ("PODE", ["VERDE"]), {"comprador": ("PODE", ["VERDE"], [["FRANCISCO"], ["ELIAS"]])})
caso_atpv("A05", "Procuração só de venda usada para comprar", "comprador",
          "Poderes para vender não incluem comprar (interpretação estrita do mandato).",
          ["JANGADA_CS", "POA_PEDRO"], "A_ARGO", "2026-10-09", PF("NADIA"), PJ("JANGADA", A("PEDRO")),
          ("NAO_PODE", ["VERMELHO"]), {"comprador": ("NAO_PODE", ["VERMELHO"], [["FRANCISCO"]])})
caso_atpv("A06", "PJ dos dois lados: ambos com poder", "dois_lados",
          "Vendedor e comprador PJ; documentos separados por CNPJ; os dois lados podem.",
          ["SERTAO_CS", "BOMJARDIM_CS"], "A_SAVEIRO", "2026-10-13", PJ("SERTAO", A("JOAO")), PJ("BOMJARDIM", A("SIMONE")),
          ("PODE", ["VERDE"]), {"vendedor": ("PODE", ["VERDE"], [["JOAO"], ["MARIA"]]),
                                "comprador": ("PODE", ["VERDE"], [["GILBERTO"], ["SIMONE"]])})
caso_atpv("A07", "PJ dos dois lados, assinaturas lidas da ATPV-e: comprador sem poder", "dois_lados",
          "As assinaturas já registradas na ATPV-e: vendedor correto (os dois sócios), comprador assinado por quotista.",
          ["MANDACARU_CS", "JANGADA_CS"], "A_S10", "2026-10-14", PJ("MANDACARU", A("CARLOS"), A("LUCIANA")),
          PJ("JANGADA", A("ANABEATRIZ")), ("NAO_PODE", ["VERMELHO"]),
          {"vendedor": ("PODE", ["VERDE"], [["CARLOS", "LUCIANA"]]), "comprador": ("NAO_PODE", ["VERMELHO"], [["FRANCISCO"]])},
          assinaturas_na_atpv=True)
caso_atpv("A08", "Cooperativa: Diretor-Presidente e Diretor Financeiro assinam", "tipos",
          "Estatuto sem nomes + ata da AGO elegendo a diretoria; restrição da Assembleia só para imóveis.",
          ["COOPVALE_ESTATUTO", "COOPVALE_ATA_AGO"], "A_VOLARE", "2026-10-15", PJ("COOPVALE", A("MANOEL"), A("EXPEDITO")),
          PF("DEBORA"), ("PODE", ["VERDE"]), {"vendedor": ("PODE", ["VERDE"], [["MANOEL", "EXPEDITO"]])})
caso_atpv("A09", "Cooperativa: Diretor-Presidente sozinho", "tipos",
          "Alienação exige Diretor-Presidente em conjunto com o Diretor Financeiro.",
          ["COOPVALE_ESTATUTO", "COOPVALE_ATA_AGO"], "A_SPRINTER", "2026-10-15", PJ("COOPVALE", A("MANOEL")),
          PF("DEBORA"), ("NAO_PODE", ["VERMELHO"]), {"vendedor": ("NAO_PODE", ["VERMELHO"], [["MANOEL", "EXPEDITO"]])})
caso_atpv("A10", "Associação compradora: Presidente eleita assina", "tipos",
          "Associação civil (CC arts. 53-61): Presidente representa sozinha; restrição só para imóveis.",
          ["ASSOC_ESTATUTO", "ASSOC_ATA_ELEICAO"], "A_SPIN", "2026-10-09", PF("NADIA"), PJ("ASSOC", A("SOCORRO")),
          ("PODE", ["VERDE"]), {"comprador": ("PODE", ["VERDE"], [["SOCORRO"]])})
caso_atpv("A11", "MEI vende: o titular assina", "tipos",
          "Microempreendedor individual (CCMEI): o titular responde pela empresa.",
          ["MEI_CCMEI"], "A_FIORINO", "2026-10-12", PJ("MEI", A("ROGERIO", "ROGERIO F LIMA")), PF("DEBORA"),
          ("PODE", ["VERDE"]), {"vendedor": ("PODE", ["VERDE"], [["ROGERIO"]])})
caso_atpv("A12", "MEI compra: a esposa do titular assina", "tipos",
          "Quem não é o titular do MEI não assina por ele sem procuração.",
          ["MEI_CCMEI"], "A_STRADA", "2026-10-12", PF("NADIA"), PJ("MEI", A("CLAUDIA")),
          ("NAO_PODE", ["VERMELHO"]), {"comprador": ("NAO_PODE", ["VERMELHO"], [["ROGERIO"]])})
caso_atpv("A13", "EIRELI (hoje SLU) vende: o titular assina", "tipos",
          "EIRELI de 2019, transformada em SLU pela Lei 14.195/2021: o titular administrador assina.",
          ["EIRELI_ATO"], "A_RANGER", "2026-10-16", PJ("EIRELI", A("WELLINGTON")), PF("DEBORA"),
          ("PODE", ["VERDE"]), {"vendedor": ("PODE", ["VERDE"], [["WELLINGTON"]])})
caso_atpv("A14", "Sociedade simples: um sócio assina sozinho", "tipos",
          "Sociedade simples registrada no RCPJ; administração exige a assinatura dos dois sócios.",
          ["PINHO_CS"], "A_RENEGADE", "2026-10-16", PJ("PINHO", A("LARISSA")), PF("DEBORA"),
          ("NAO_PODE", ["VERMELHO"]), {"vendedor": ("NAO_PODE", ["VERMELHO"], [["LARISSA", "THIAGO"]])})


# =========================================================================== LOTE CONSULTA POR CPF (chefe, 17/10/2026 11:40)
# "poderia ser até antes do ATPV: a pessoa coloca um CPF e, se o veículo for de PJ, verifica se esse CPF tem poder para
# vender ou comprar"; "mesmo sendo pessoa física, se botar um CPF diferente do vendedor ou do comprador, perguntar se tem
# procuração e ver na procuração se o CPF colocado tem poder de transferir o veículo". O pedido é só veículo + CPF + papel;
# o dono vem da base veicular (simulada). RNG próprio: não altera nenhum número acima.
rng_p = random.Random(1740)
_PP = [
    ("RAIMUNDA", "Raimunda Nonata Siqueira", "f", "viúva", "aposentada", "Fortaleza/CE"),
    ("ERIVAN", "Francisco Erivan Cavalcante", "m", "casado", "comerciante", "Caucaia/CE"),
    ("MARTA", "Marta Lúcia Cavalcante", "f", "casada", "professora", "Caucaia/CE"),
    ("VALERIA", "Antônia Valéria Barros", "f", "solteira", "cirurgiã-dentista", "Fortaleza/CE"),
    ("GILMAR", "Gilmar Sousa Pontes", "m", "divorciado", "agricultor", "Itapipoca/CE"),
    ("JOSUELIMA", "Josué Lima Ferreira", "m", "casado", "despachante documentalista", "Fortaleza/CE"),
    ("PATRICIA", "Patrícia Moura Leal", "f", "solteira", "despachante documentalista", "Fortaleza/CE"),
    ("EDVALDO", "Edvaldo Pinheiro Neto", "m", "casado", "corretor de veículos", "Maracanaú/CE"),
    ("LUANA", "Luana Castro Ribeiro", "f", "solteira", "estudante", "Fortaleza/CE"),
]
for pid, nome, g, ec, prof, cid in _PP:
    PESSOAS[pid] = {"id": pid, "nome": nome, "genero": g, "nacionalidade": "brasileiro" if g == "m" else "brasileira",
                    "estado_civil": ec, "profissao": prof, "cidade": cid, "cpf": gerar_cpf(rng_p),
                    "rg": f"{rng_p.randint(1000000, 99999999)} SSP/CE"}
for vid, mm, fab, mod, cor, comb, esp, valor in [
    ("P_HB20", "HYUNDAI/HB20 1.0 COMFORT", 2020, 2021, "PRATA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 64000),
    ("P_STRADA", "FIAT/STRADA WORKING 1.4", 2019, 2020, "BRANCA", "ÁLCOOL/GASOLINA", "CARGA/CAMIONETA", 72000),
    ("P_ONIX", "GM/ONIX 1.0 LT", 2021, 2021, "PRETA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 69000),
    ("P_TORO", "FIAT/TORO FREEDOM 1.8 AT6", 2020, 2020, "VERMELHA", "ÁLCOOL/GASOLINA", "CARGA/CAMINHONETE", 108000),
    ("P_KWID", "RENAULT/KWID ZEN 1.0", 2022, 2022, "BRANCA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 58000),
    ("P_SPRINTER", "M.BENZ/SPRINTER 415 CDI VAN", 2021, 2021, "BRANCA", "DIESEL", "PASSAGEIRO/MICRO-ÔNIBUS", 235000),
    ("P_CRETA", "HYUNDAI/CRETA 1.6 ACTION", 2021, 2022, "CINZA", "ÁLCOOL/GASOLINA", "PASSAGEIRO/AUTOMÓVEL", 95000),
]:
    VEICULOS[vid] = {"id": vid, "marca_modelo": mm, "ano_fabricacao": fab, "ano_modelo": mod, "cor": cor, "combustivel": comb,
                     "especie_tipo": esp, "placa": gerar_placa(rng_p), "renavam": gerar_renavam(rng_p),
                     "chassi": gerar_chassi(rng_p, {"HYUNDAI": "9BH", "FIAT": "9BD", "GM": "9BG", "RENAULT": "93Y",
                                                    "M.BENZ": "9BM"}[mm.split("/")[0]]),
                     "valor": valor}


def QPF(pid):
    """Qualificação de pessoa física outorgante, em nome próprio."""
    q = PESSOAS[pid]
    return (f"{q['nome']}, {q['nacionalidade']}, {q['estado_civil']}, {q['profissao']}, RG {q['rg']}, CPF {q['cpf']}, "
            f"residente em {q['cidade']}, pessoa física, em NOME PRÓPRIO")


PODERES_PF = ("vender, ceder, transferir ou de qualquer forma alienar, a quem e pelo preço que convencionar, o veículo {v}, de "
              "propriedade do(a) outorgante, assinar a Autorização para Transferência de Propriedade do Veículo (ATPV-e), "
              "receber o preço e dar quitação, requerer e assinar o que for necessário perante o DETRAN")

procuracao("POA_PF_HB20", "2026-08-12", None, QPF("RAIMUNDA"), ["JOSUELIMA"],
           "poderes especiais e expressos para " + PODERES_PF.format(v=VEIC("P_HB20")),
           "1 (um) ano", "omisso (não mencione)", "publica", ["poderes especiais e expressos", VEICULOS["P_HB20"]["placa"]])
doc("SUB_PF_JOSUE_PATRICIA", "substabelecimento", None, "2026-09-30", "SUBSTABELECIMENTO DE PROCURAÇÃO",
    [f"SUBSTABELECIMENTO POR INSTRUMENTO PÚBLICO lavrado em {CARTORIOS['IRACEMA']}.",
     f"Substabelecente: {N('JOSUELIMA')} (CPF {PESSOAS['JOSUELIMA']['cpf']}), procurador de {N('RAIMUNDA')} (CPF {PESSOAS['RAIMUNDA']['cpf']}) pela procuração pública de 12/08/2026 do mesmo cartório (indique livro e folhas fictícios), para a venda do veículo {VEIC('P_HB20')}.",
     f"Substabelecida: {N('PATRICIA')} ({PESSOAS['PATRICIA']['profissao']}, CPF {PESSOAS['PATRICIA']['cpf']}).",
     "Substabelece COM RESERVA de iguais poderes todos os poderes recebidos (frase obrigatória)."],
    ["com reserva de iguais poderes", "12 de agosto de 2026"], palavras=(250, 450))
procuracao("POA_PF_VENCIDA", "2025-10-01", None, QPF("RAIMUNDA"), ["EDVALDO"],
           "poderes especiais e expressos para vender, ceder e transferir quaisquer veículos automotores de propriedade da "
           "outorgante, assinar a ATPV-e, receber o preço e dar quitação",
           "6 (seis) meses contados desta data (frase obrigatória)", "omisso (não mencione)", "publica",
           ["6 (seis) meses"])
procuracao("POA_PF_ADMIN", "2026-04-15", None, QPF("ERIVAN"), ["PATRICIA"],
           "amplos e gerais poderes para representá-lo perante o DETRAN-CE e demais repartições públicas em tudo o que for "
           "necessário relativo aos veículos de sua propriedade: licenciamento, vistoria, pagamento de IPVA, taxas e multas, "
           "segunda via de documentos, indicação de condutor e defesa de autuações. NÃO inclua poder de vender, alienar, "
           "transferir propriedade ou assinar ATPV (armadilha: são só poderes de administração), e também NÃO escreva frases "
           "negando esses poderes", "1 (um) ano", "omisso (não mencione)", "publica",
           ["amplos e gerais poderes", "em tudo o que for necessário"])
procuracao("POA_PF_ONIX", "2026-07-20", None, QPF("ERIVAN"), ["JOSUELIMA"],
           "poderes especiais e expressos para " + PODERES_PF.format(v=VEIC("P_ONIX")) + ". A procuração é SÓ para esse veículo",
           "1 (um) ano", "omisso (não mencione)", "publica", [VEICULOS["P_ONIX"]["placa"]])
procuracao("POA_PF_PARTICULAR", "2026-09-05", None, QPF("ERIVAN"), ["EDVALDO"],
           "poderes especiais e expressos para " + PODERES_PF.format(v=VEIC("P_STRADA")),
           "1 (um) ano", "omisso (não mencione)", "particular", [VEICULOS["P_STRADA"]["placa"]], firma=True)
procuracao("POA_PF_CONJUGE", "2026-08-28", None,
           QPF("MARTA") + f", casada com {N('ERIVAN')} (que NÃO comparece nem assina), declarando que o veículo pertence ao casal",
           ["JOSUELIMA"], "poderes especiais e expressos para vender o veículo " + VEIC("P_STRADA") + ", assinar a ATPV-e, "
           "receber o preço e dar quitação", "1 (um) ano", "omisso (não mencione)", "publica",
           [VEICULOS["P_STRADA"]["placa"], "pertence ao casal"])
procuracao("POA_PF_TODOS_GILMAR", "2026-01-20", None, QPF("GILMAR"), ["EDVALDO"],
           "poderes especiais e expressos para vender, ceder e transferir quaisquer veículos automotores de propriedade do "
           "outorgante, assinar a ATPV-e, receber o preço e dar quitação", "por prazo indeterminado, até revogação",
           "omisso (não mencione)", "publica", ["quaisquer veículos automotores de propriedade do outorgante"])
doc("REV_PF_GILMAR", "revogacao_procuracao", None, "2026-06-10", "ESCRITURA PÚBLICA DE REVOGAÇÃO DE PROCURAÇÃO",
    [f"Lavrada em {CARTORIOS['IRACEMA']}. Revogante: {QPF('GILMAR')}.",
     f"Revoga, para todos os fins, a procuração pública que outorgou a {N('EDVALDO')} (CPF {PESSOAS['EDVALDO']['cpf']}) em 20/01/2026 neste mesmo cartório (indique livro e folhas fictícios), com notificação do procurador.",
     "Fecho com selo digital fictício."],
    ["revoga", "20 de janeiro de 2026"], palavras=(250, 450))
procuracao("POA_PF_COMPRA_VALERIA", "2026-09-10", None, QPF("VALERIA"), ["PATRICIA"],
           "poderes especiais e expressos para comprar ou adquirir, em nome da outorgante, um veículo automotor de passeio, "
           "escolher o veículo, negociar o preço, assinar como compradora a Autorização para Transferência de Propriedade do "
           "Veículo (ATPV-e), pagar o preço e requerer perante o DETRAN a transferência para o nome da outorgante (frase "
           "obrigatória)", "6 (seis) meses", "omisso (não mencione)", "publica",
           ["assinar como compradora a Autorização para Transferência de Propriedade do Veículo (ATPV-e)"])

CASOS_PF: list[dict] = []


def caso_cpf(cid, titulo, categoria, objetivo, docs, veiculo, data, papel, quem, dono, esperado, lado_esp,
             comprador=None, valor=None, ce=None):
    """Consulta antes da ATPV-e: veículo + CPF de quem vai assinar + papel. `dono`: {"tipo": "PJ", "empresa"} ou {"tipo": "PF", "pessoa"}."""
    lado = "vendedor" if papel == "vender" else "comprador"
    CASOS_PF.append({
        "id": cid, "titulo": titulo, "categoria": categoria, "objetivo": objetivo, "documentos": docs, "veiculo": veiculo,
        "ocr": False, "crlv_proprietario": dono, "papel": papel, "assinante": quem, "comprador": comprador,
        "transacao": {"data_venda": data, "valor": valor},
        "esperado": {"veredito": esperado[0], "faixas_aceitaveis": esperado[1], "conjuntos_minimos": None, "fundamentos": []},
        "esperado_lados": {lado: {"veredito": lado_esp[0], "faixas_aceitaveis": lado_esp[1], "conjuntos_minimos": lado_esp[2],
                                  "fundamentos": []}},
        "esperado_ce": None if ce is None else {"veredito": ce[0], "faixas_aceitaveis": ce[1], "conjuntos_minimos": None,
                                                "fundamentos": []},
        "esperado_lados_ce": None if ce is None else {lado: {"veredito": ce[0], "faixas_aceitaveis": ce[1],
                                                              "conjuntos_minimos": ce[2], "fundamentos": []}},
    })


DPF = lambda pid: {"tipo": "PF", "pessoa": pid}  # noqa: E731
DPJ = lambda eid: {"tipo": "PJ", "empresa": eid}  # noqa: E731
D = "2026-10-16"
caso_cpf("P01", "Pessoa física: o próprio dono vai assinar", "pf", "CPF do proprietário: nada a comprovar além da identidade.",
         [], "P_HB20", D, "vender", "RAIMUNDA", DPF("RAIMUNDA"), ("PODE", ["VERDE"]), ("PODE", ["VERDE"], [["RAIMUNDA"]]))
caso_cpf("P02", "Procurador com procuração pública e específica", "pf", "Procuração da dona, pública, do veículo, no prazo.",
         ["POA_PF_HB20"], "P_HB20", D, "vender", "JOSUELIMA", DPF("RAIMUNDA"), ("PODE", ["VERDE"]),
         ("PODE", ["VERDE"], [["RAIMUNDA"], ["JOSUELIMA"]]))
caso_cpf("P03", "CPF diferente do dono, sem procuração", "pf", "O sistema pergunta pela procuração (não recusa de cara).",
         [], "P_HB20", D, "vender", "LUANA", DPF("RAIMUNDA"), ("INDETERMINADO", ["AMARELO"]),
         ("INDETERMINADO", ["AMARELO"], [["RAIMUNDA"]]))
caso_cpf("P04", "Procuração só com poderes gerais (DETRAN, IPVA, multas)", "pf", "Vender exige poderes especiais e expressos (CC 661).",
         ["POA_PF_ADMIN"], "P_STRADA", D, "vender", "PATRICIA", DPF("ERIVAN"), ("NAO_PODE", ["VERMELHO"]),
         ("NAO_PODE", ["VERMELHO"], [["ERIVAN"]]))
caso_cpf("P05", "Procuração de 6 meses, vencida", "pf", "Prazo vencido antes da consulta.",
         ["POA_PF_VENCIDA"], "P_HB20", D, "vender", "EDVALDO", DPF("RAIMUNDA"), ("NAO_PODE", ["VERMELHO"]),
         ("NAO_PODE", ["VERMELHO"], [["RAIMUNDA"]]))
caso_cpf("P06", "Procuração específica de outro veículo", "pf", "A procuração é do Onix; a venda é da Strada.",
         ["POA_PF_ONIX"], "P_STRADA", D, "vender", "JOSUELIMA", DPF("ERIVAN"), ("NAO_PODE", ["VERMELHO"]),
         ("NAO_PODE", ["VERMELHO"], [["ERIVAN"]]))
caso_cpf("P07", "Compradora pessoa física representada por procuradora", "pf", "Procuração com poderes para comprar.",
         ["POA_PF_COMPRA_VALERIA"], "P_KWID", D, "comprar", "PATRICIA", DPF("LUANA"), ("PODE", ["VERDE"]),
         ("PODE", ["VERDE"], [["VALERIA"], ["PATRICIA"]]), comprador={"tipo": "PF", "pessoa": "VALERIA"})
caso_cpf("P08", "Procuração revogada", "pf", "Escritura de revogação anterior à consulta.",
         ["POA_PF_TODOS_GILMAR", "REV_PF_GILMAR"], "P_TORO", D, "vender", "EDVALDO", DPF("GILMAR"), ("NAO_PODE", ["VERMELHO"]),
         ("NAO_PODE", ["VERMELHO"], [["GILMAR"]]))
caso_cpf("P09", "Substabelecida pelo procurador, com reserva", "pf", "Cadeia dona → procurador → substabelecida, válida.",
         ["POA_PF_HB20", "SUB_PF_JOSUE_PATRICIA"], "P_HB20", D, "vender", "PATRICIA", DPF("RAIMUNDA"), ("PODE", ["VERDE"]),
         ("PODE", ["VERDE"], [["RAIMUNDA"], ["JOSUELIMA"], ["PATRICIA"]]))
caso_cpf("P10", "Procuração particular com firma reconhecida", "pf", "Vale pelo Código Civil; o DETRAN-CE exige pública.",
         ["POA_PF_PARTICULAR"], "P_STRADA", D, "vender", "EDVALDO", DPF("ERIVAN"), ("PODE", ["VERDE", "AMARELO"]),
         ("PODE", ["VERDE", "AMARELO"], [["ERIVAN"], ["EDVALDO"]]),
         ce=("NAO_PODE", ["VERMELHO"], [["ERIVAN"]]))
caso_cpf("P11", "Procuração dada pela esposa, não pelo dono registral", "pf",
         "Só o proprietário que consta no registro pode constituir procurador para assinar a ATPV-e.",
         ["POA_PF_CONJUGE"], "P_STRADA", D, "vender", "JOSUELIMA", DPF("ERIVAN"), ("NAO_PODE", ["VERMELHO"]),
         ("NAO_PODE", ["VERMELHO"], [["ERIVAN"]]))
caso_cpf("P12", "Dona é empresa: CPF do administrador", "pj", "Consulta por CPF com veículo de PJ.",
         ["JANGADA_CS"], "P_SPRINTER", D, "vender", "FRANCISCO", DPJ("JANGADA"), ("PODE", ["VERDE"]),
         ("PODE", ["VERDE"], [["FRANCISCO"]]))
caso_cpf("P13", "Dona é empresa: CPF de sócia sem poder, sem procuração", "pj",
         "Antes de recusar, o sistema pergunta se ela tem procuração da empresa.",
         ["JANGADA_CS"], "P_SPRINTER", D, "vender", "ANABEATRIZ", DPJ("JANGADA"), ("INDETERMINADO", ["AMARELO"]),
         ("INDETERMINADO", ["AMARELO"], [["FRANCISCO"]]))
caso_cpf("P14", "Dona é empresa: CPF de procurador da empresa", "pj", "Procuração pública da empresa, no prazo.",
         ["JANGADA_CS", "POA_PEDRO"], "P_SPRINTER", D, "vender", "PEDRO", DPJ("JANGADA"), ("PODE", ["VERDE"]),
         ("PODE", ["VERDE"], [["FRANCISCO"], ["PEDRO"]]))
caso_cpf("P15", "Comprador é empresa: CPF do administrador, abaixo da alçada", "pj",
         "Consulta para comprar: a alçada de compra (R$ 100 mil) não é atingida.",
         ["BOMJARDIM_CS"], "P_CRETA", D, "comprar", "GILBERTO", DPF("RAIMUNDA"), ("PODE", ["VERDE"]),
         ("PODE", ["VERDE"], [["GILBERTO"], ["SIMONE"]]), comprador={"tipo": "PJ", "empresa": "BOMJARDIM"}, valor=95000)


def main() -> None:
    dados = {"versao": 1, "aviso": "Dados 100% fictícios para avaliação.", "pessoas": PESSOAS,
             "empresas": EMPRESAS, "veiculos": VEICULOS, "cartorios": CARTORIOS, "documentos": DOCS, "casos": CASOS,
             "casos_holdout": CASOS_HOLDOUT, "casos_atpv": CASOS_ATPV, "casos_pf": CASOS_PF}
    (AQUI / "cenarios.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    linhas = ["# Cenários de avaliação (gabarito)", "",
              "Gerado por `corpus/spec.py`. Dados fictícios.", "",
              "| Caso | Cenário | Assinante(s) | Esperado | Faixa | Quem pode assinar |", "|---|---|---|---|---|---|"]
    for c in CASOS + [dict(x, titulo="[cega] " + x["titulo"]) for x in CASOS_HOLDOUT]:
        ass = ", ".join(PESSOAS[a["pessoa"]]["nome"].split()[0] for a in c["transacao"]["assinantes"])
        conj = c["esperado"]["conjuntos_minimos"]
        quem = "—" if conj is None else ("ninguém (regularizar)" if conj == [] else
                                         " ou ".join(" + ".join(PESSOAS[p]["nome"].split()[0] for p in s) for s in conj))
        linhas.append(f"| {c['id']} | {c['titulo']} | {ass} | {c['esperado']['veredito']} | "
                      f"{'/'.join(c['esperado']['faixas_aceitaveis'])} | {quem} |")
    linhas += ["", "## Lote ATPV-e (vendendo ou comprando; todos os tipos de PJ)", "",
               "| Caso | Cenário | Vendedor | Comprador | Esperado | Faixa |", "|---|---|---|---|---|---|"]

    def _lado(x):
        if "pessoa" in x:
            return PESSOAS[x["pessoa"]]["nome"].split()[0] + " (PF)"
        ass = ", ".join(PESSOAS[a["pessoa"]]["nome"].split()[0] for a in x.get("assinantes", []))
        return f"{EMPRESAS[x['empresa']]['razao_social'][:28]} — {ass}"

    for c in CASOS_ATPV:
        linhas.append(f"| {c['id']} | {c['titulo']} | {_lado(c['vendedor'])} | {_lado(c['comprador'])} | "
                      f"{c['esperado']['veredito']} | {'/'.join(c['esperado']['faixas_aceitaveis'])} |")
    linhas += ["", "## Lote consulta por CPF (antes da ATPV-e; pessoa física e procuração)", "",
               "| Caso | Cenário | Papel | Quem vai assinar | Esperado | Faixa |", "|---|---|---|---|---|---|"]
    for c in CASOS_PF:
        esp = c["esperado_ce"] or c["esperado"]
        linhas.append(f"| {c['id']} | {c['titulo']} | {c['papel']} | {PESSOAS[c['assinante']]['nome']} | "
                      f"{esp['veredito']} | {'/'.join(esp['faixas_aceitaveis'])} |")
    (AQUI / "CENARIOS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{len(CASOS)} casos + {len(CASOS_HOLDOUT)} de validação cega + {len(CASOS_ATPV)} do lote ATPV-e + {len(CASOS_PF)} "
          f"de consulta por CPF, {len(DOCS)} documentos, "
          f"{len(PESSOAS)} pessoas, {len(VEICULOS)} veículos")


if __name__ == "__main__":
    main()
