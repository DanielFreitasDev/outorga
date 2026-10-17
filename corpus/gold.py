"""Gabarito de LEITURA: a extração perfeita de cada documento, no mesmo formato do LLM.

Serve para duas coisas:
1. testar o motor jurídico isolado da IA ("modo oráculo"): com fatos corretos ele deve acertar 100%;
2. medir campo a campo a leitura do LLM contra o gabarito.

As evidências são localizadas no próprio texto do documento (literais), via expressões regulares.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from outorga import schemas as sc
from outorga.consolidate import LeituraDocumento
from outorga.ingest import carregar

AQUI = Path(__file__).parent
SPEC = json.loads((AQUI / "cenarios.json").read_text(encoding="utf-8"))
P, E, V = SPEC["pessoas"], SPEC["empresas"], SPEC["veiculos"]


@lru_cache(maxsize=None)
def _texto(did: str) -> str:
    t = (AQUI / "docs" / f"{did}.md").read_text(encoding="utf-8").replace("**", "").replace("\\_", "_")
    return re.sub(r"\s+", " ", t)


def ev(did: str, *padroes: str) -> str:
    """Primeira frase do documento que casa com um dos padrões (case-insensitive)."""
    t = _texto(did)
    for p in padroes:
        m = re.search(p, t, re.I)
        if m:
            ini = max(t.rfind(". ", 0, m.start()), t.rfind("; ", 0, m.start()))
            ini = ini + 2 if ini >= 0 and m.start() - ini < 400 else m.start()
            fim = t.find(".", m.end())
            fim = fim if 0 <= fim - m.end() < 400 else m.end()
            return t[ini:fim].strip()
    return SPEC["documentos"].get(did, {}).get("frases_obrigatorias", [""])[0] if did in SPEC["documentos"] else ""


def pref(pid: str) -> sc.PessoaRef:
    return sc.PessoaRef(nome=P[pid]["nome"].upper(), cpf=P[pid]["cpf"])


def vref(vid: str) -> sc.VeiculoRef:
    v = V[vid]
    return sc.VeiculoRef(descricao=v["marca_modelo"], placa=v["placa"], renavam=v["renavam"], chassi=v["chassi"])


def nome(pid: str) -> str:
    return P[pid]["nome"].upper()


# ----------------------------------------------------------------------------- societários
def adm(did, pid, cargo="sócio administrador", socio=True, prazo=None, termino=None):
    return sc.Administrador(evidencia=ev(did, r"administra[çc][ãa]o (da sociedade|da companhia)?.{0,300}" + re.escape(nome(pid)),
                                         re.escape(nome(pid)) + r".{0,120}(administrador|administradora|Diretor|Diretora|titular)",
                                         re.escape(nome(pid))),
                            nome=nome(pid), cpf=P[pid]["cpf"], cargo=cargo, socio=socio,
                            prazo=sc.Prazo(tipo="determinado" if prazo else "indeterminado", termino=termino, descricao=prazo))


def regra(did, evidencia, escopo, modo, pessoas=(), efeito="autoriza", cargo=None, qtd=None, combinacoes=(), valor_acima=None,
          aprov=False, quorum=None, anuencia=(), veiculo=None, clausula=None, expressao=None):
    return sc.Regra(evidencia=evidencia, clausula=clausula, expressao_modo=expressao, escopo=escopo, veiculo=veiculo,
                    efeito=efeito, modo=modo, pessoas=[nome(p) if p in P else p for p in pessoas], cargo=cargo,
                    quantidade_minima=qtd, combinacoes=list(combinacoes), valor_acima_de=valor_acima, valor_ate=None,
                    exige_aprovacao_socios=aprov, quorum_percentual=quorum,
                    exige_anuencia_de=[nome(p) if p in P else p for p in anuencia])  # cargos ("Presidente") vão como texto


def partes(did, tipo_det, emp, socios, admins, num_alt=None, altera=True, bens=()):
    d = SPEC["documentos"][did]
    e = E[emp]
    return sc.ExtracaoPartes(
        documento=sc.DadosDocumento(tipo_detalhado=tipo_det, numero_alteracao=num_alt, data_assinatura=d["data"],
                                    data_registro=d["registro"]["data"] if d.get("registro") else None,
                                    numero_registro=d["registro"]["numero"] if d.get("registro") else None),
        empresa=sc.DadosEmpresa(razao_social=e["razao_social"], cnpj=e["cnpj"],
                                tipo_societario={"ASSOCIACAO": "OUTRO"}.get(e["tipo"], e["tipo"]), objeto_social=e["objeto"],
                                comercializa_veiculos=emp == "BEIRAMAR"),
        socios=[sc.Socio(nome=nome(p), cpf=P[p]["cpf"], percentual=pct) for p, pct in socios],
        administradores=admins, bens_integralizados=list(bens),
        alteracao=sc.AlteracaoAdministracao(altera_administracao=altera, resumo=None))


SEM_RP = sc.RegrasProcuracao(evidencia=None, prazo_maximo_meses=None, exige_poderes_especificados=False, vedada_para_alienacao=False)


def regras(lst, rp=SEM_RP):
    return sc.ExtracaoRegras(regras=lst, regras_procuracao=rp)


def gold_societario(did: str):
    s = lambda emp: [(p, pct) for p, pct in E[emp]["socios"]]  # noqa: E731
    if did == "SERTAO_CS":
        return "contrato_social", partes(did, "constituicao", "SERTAO", s("SERTAO"), [adm(did, "JOAO"), adm(did, "MARIA")]), regras([
            regra(did, ev(did, "que a exercerão indistintamente"), "geral", "isolado", ["JOAO", "MARIA"], expressao="indistintamente"),
            regra(did, ev(did, "onerar ou alienar bens imóveis"), "alienacao_bens_imoveis", "nao_especificado", efeito="restringe",
                  aprov=True, quorum=75)])
    if did == "MANDACARU_CS":
        return "contrato_consolidado", partes(did, "alteracao_e_consolidacao", "MANDACARU", s("MANDACARU"),
                                              [adm(did, "CARLOS"), adm(did, "LUCIANA")], num_alt=4), regras([
            regra(did, ev(did, "exercida conjuntamente pelos sócios"), "geral", "conjunto", ["CARLOS", "LUCIANA"], expressao="conjuntamente"),
            regra(did, ev(did, "vedada a prática isolada"), "alienacao_bens", "conjunto", ["CARLOS", "LUCIANA"], efeito="restringe",
                  expressao="vedada a prática isolada")])
    if did == "JANGADA_CS":
        return "contrato_social", partes(did, "constituicao", "JANGADA", s("JANGADA"), [adm(did, "FRANCISCO")]), regras([
            regra(did, ev(did, "cabe exclusivamente ao sócio FRANCISCO"), "geral", "isolado", ["FRANCISCO"]),
            regra(did, ev(did, "inclusive comprar, vender e alienar os veículos"), "alienacao_veiculos", "isolado", ["FRANCISCO"])])
    if did == "MARACANAU_CS":
        return "contrato_social", partes(did, "constituicao", "MARACANAU", s("MARACANAU"),
                                         [adm(did, "GUSTAVO", "administrador não sócio", False)]), regras([
            regra(did, ev(did, "que representará a sociedade isoladamente"), "geral", "isolado", ["GUSTAVO"], expressao="isoladamente"),
            regra(did, ev(did, "comprar, vender, alienar e onerar veículos da frota"), "alienacao_veiculos", "isolado", ["GUSTAVO"])])
    if did == "IRACEMA_CS":
        return "contrato_social", partes(did, "constituicao", "IRACEMA", s("IRACEMA"), [adm(did, "PAULA"), adm(did, "ITALO")]), regras([
            regra(did, ev(did, "A administração da sociedade caberá aos sócios PAULA"), "geral", "nao_especificado", ["PAULA", "ITALO"])])
    if did == "CARIRI_CS":
        return "contrato_social", partes(did, "constituicao", "CARIRI", s("CARIRI"), [adm(did, "ANTONIO"), adm(did, "JOSEFA")]), regras([
            regra(did, ev(did, "que a exercerão isoladamente"), "geral", "isolado", ["ANTONIO", "JOSEFA"], expressao="isoladamente"),
            regra(did, ev(did, "valor unitário superior a R\\$ 150"), "alienacao_veiculos", "conjunto", ["ANTONIO", "JOSEFA"],
                  efeito="restringe", valor_acima=150000.0, expressao="assinatura conjunta de ambos os administradores")])
    if did == "CAMOCIM_CS":
        return "contrato_social", partes(did, "constituicao", "CAMOCIM", s("CAMOCIM"), [adm(did, "VALDIR"), adm(did, "MARCIA")]), regras([
            regra(did, ev(did, "qualquer deles isoladamente"), "geral", "isolado", ["VALDIR", "MARCIA"], expressao="qualquer deles isoladamente"),
            regra(did, ev(did, "Dependerão de prévia aprovação de sócios"), "alienacao_ativo_imobilizado", "nao_especificado",
                  efeito="restringe", aprov=True, quorum=50.01)])
    if did == "PRIME_CS":
        bem = sc.BemIntegralizado(evidencia=ev(did, "conferência à sociedade do seguinte bem", V["COROLLA"]["placa"]),
                                  socio_nome=nome("MARCOS"), descricao=V["COROLLA"]["marca_modelo"], veiculo=vref("COROLLA"))
        return "contrato_social", partes(did, "constituicao", "PRIME", s("PRIME"), [adm(did, "MARCOS"), adm(did, "LEONARDO")],
                                         bens=[bem]), regras([
            regra(did, ev(did, "qualquer um deles isoladamente"), "geral", "isolado", ["MARCOS", "LEONARDO"], expressao="qualquer um deles isoladamente"),
            regra(did, ev(did, "somente poderá ser alienado"), "veiculo_especifico", "isolado", ["MARCOS"], efeito="restringe",
                  veiculo=vref("COROLLA"))])
    if did == "TECH_CS":
        rp = sc.RegrasProcuracao(evidencia=ev(did, "As procurações outorgadas pela sociedade"), prazo_maximo_meses=12,
                                 exige_poderes_especificados=True, vedada_para_alienacao=False)
        return "ato_constitutivo_slu", partes(did, "ato_constitutivo_slu", "TECH", s("TECH"), [adm(did, "RAFAEL", "sócio único administrador")]), regras([
            regra(did, ev(did, r"administração da sociedade.{0,160}RAFAEL", r"RAFAEL NOGUEIRA BRITO.{0,120}isoladamente"), "geral",
                  "isolado", ["RAFAEL"])], rp)
    if did == "CHAPADA_CS":
        return "contrato_social", partes(did, "constituicao", "CHAPADA", s("CHAPADA"), [adm(did, "JOAQUIM")]), regras([
            regra(did, ev(did, "exercida exclusivamente pelo sócio JOAQUIM"), "geral", "isolado", ["JOAQUIM"])])
    if did == "CHAPADA_ALT1":
        return "alteracao_contratual", partes(did, "alteracao", "CHAPADA", s("CHAPADA"), [adm(did, "LUCIA", "sócia administradora")],
                                              num_alt=1), regras([
            regra(did, ev(did, "passa a ser exercida exclusivamente pela sócia"), "geral", "isolado", ["LUCIA"], expressao="isoladamente")])
    if did == "RUSSAS_CS":
        return "contrato_social", partes(did, "constituicao", "RUSSAS", s("RUSSAS"), [adm(did, "HELIO"), adm(did, "REGINA")]), regras([
            regra(did, ev(did, "os quais poderão representá-la isoladamente"), "geral", "isolado", ["HELIO", "REGINA"], expressao="isoladamente")])
    if did == "RUSSAS_ALT1":
        return "alteracao_contratual", partes(did, "alteracao", "RUSSAS", s("RUSSAS"), [adm(did, "HELIO"), adm(did, "REGINA")],
                                              num_alt=1), regras([
            regra(did, ev(did, "exigindo-se a assinatura de ambos"), "alienacao_bens", "conjunto", ["HELIO", "REGINA"],
                  expressao="assinatura de ambos os sócios", clausula="Cláusula Oitava")])
    if did == "SOBRAL_CS":
        return "contrato_social", partes(did, "constituicao", "SOBRAL", s("SOBRAL"), [
            adm(did, "WAGNER", prazo="pelo prazo de 3 (três) anos, contados do registro deste instrumento, permitida a recondução")]), regras([
            regra(did, ev(did, r"WAGNER PONTES AGUIAR.{0,200}isoladamente", r"isoladamente.{0,200}WAGNER"), "geral", "isolado", ["WAGNER"])])
    if did == "ARACATI_ESTATUTO":
        combs = [sc.Combinacao(descricao="2 diretores", grupos=[sc.Grupo(cargo="diretores", quantidade=2)]),
                 sc.Combinacao(descricao="1 diretor + 1 procurador",
                               grupos=[sc.Grupo(cargo="diretores", quantidade=1), sc.Grupo(cargo="procuradores", quantidade=1)])]
        rp = sc.RegrasProcuracao(evidencia=ev(did, "As procurações serão outorgadas pela Companhia"), prazo_maximo_meses=12,
                                 exige_poderes_especificados=True, vedada_para_alienacao=False)
        return "estatuto_social", partes(did, "estatuto", "ARACATI", [], []), regras([
            regra(did, ev(did, "por 2 \\(dois\\) Diretores em conjunto"), "geral", "misto", cargo="diretores", combinacoes=combs),
            regra(did, ev(did, "As procurações serão outorgadas pela Companhia"), "outorgar_procuracoes", "quantidade_minima",
                  cargo="diretores", qtd=2),
            regra(did, ev(did, "de valor superior a R\\$ 1.000.000"), "alienacao_ativo_imobilizado", "nao_especificado",
                  efeito="restringe", valor_acima=1000000.0, aprov=True)], rp)
    if did == "JPSILVA_REQ":
        return "requerimento_empresario", partes(did, "requerimento_empresario", "JPSILVA", s("JPSILVA"),
                                                 [adm(did, "JOSUE", "empresário titular")]), regras([])
    if did == "BEIRAMAR_CS":
        return "contrato_social", partes(did, "constituicao", "BEIRAMAR", s("BEIRAMAR"), [adm(did, "EDUARDO")]), regras([
            regra(did, ev(did, r"EDUARDO MARTINS LEAL.{0,250}isoladamente", r"isoladamente.{0,200}EDUARDO"), "geral", "isolado", ["EDUARDO"]),
            regra(did, ev(did, "integrantes do ativo imobilizado"), "alienacao_ativo_imobilizado", "nao_especificado",
                  efeito="restringe", aprov=True, quorum=75)])
    # ---- lote ATPV-e (comprador PJ e outros tipos de pessoa jurídica)
    if did == "BOMJARDIM_CS":
        return "contrato_social", partes(did, "constituicao", "BOMJARDIM", s("BOMJARDIM"),
                                         [adm(did, "GILBERTO"), adm(did, "SIMONE")]), regras([
            regra(did, ev(did, "que a exercerão isoladamente"), "geral", "isolado", ["GILBERTO", "SIMONE"], expressao="isoladamente"),
            regra(did, ev(did, "A aquisição de veículos, máquinas e equipamentos.{0,160}ambos os administradores"), "outro", "conjunto",
                  ["GILBERTO", "SIMONE"],
                  efeito="restringe", valor_acima=100000.0, expressao="assinatura conjunta de ambos os administradores")])
    if did == "COOPVALE_ESTATUTO":
        return "estatuto_social", partes(did, "estatuto", "COOPVALE", [], []), regras([
            regra(did, ev(did, r"Compete ao Diretor-Presidente representar a Cooperativa, ativa e passivamente, em juízo ou fora dele"),
                  "geral", "isolado", ["Diretor-Presidente"]),
            regra(did, ev(did, "serão assinados pelo Diretor-Presidente em conjunto com o Diretor Financeiro"), "alienacao_bens",
                  "conjunto", ["Diretor-Presidente", "Diretor Financeiro"], efeito="restringe", expressao="em conjunto"),
            regra(did, ev(did, "deliberar sobre a alienação ou oneração de bens imóveis"), "alienacao_bens_imoveis",
                  "nao_especificado", efeito="restringe", aprov=True)])
    if did == "ASSOC_ESTATUTO":
        return "estatuto_social", partes(did, "estatuto", "ASSOC", [], []), regras([
            regra(did, ev(did, "Compete ao Presidente representar a Associação.{0,120}sozinho"), "geral", "isolado", ["Presidente"]),
            regra(did, ev(did, "A alienação ou oneração de bens imóveis da Associação"), "alienacao_bens_imoveis", "nao_especificado",
                  efeito="restringe", aprov=True)])
    if did == "MEI_CCMEI":
        return "requerimento_empresario", partes(did, "requerimento_empresario", "MEI", s("MEI"),
                                                 [adm(did, "ROGERIO", "empresário titular")]), regras([])
    if did == "EIRELI_ATO":
        return "ato_constitutivo_slu", partes(did, "ato_constitutivo_slu", "EIRELI", s("EIRELI"),
                                              [adm(did, "WELLINGTON", "titular administrador")]), regras([
            regra(did, ev(did, "A administração da empresa caberá ao titular"), "geral", "isolado", ["WELLINGTON"],
                  expressao="isoladamente")])
    if did == "PINHO_CS":
        return "contrato_social", partes(did, "constituicao", "PINHO", s("PINHO"), [adm(did, "LARISSA"), adm(did, "THIAGO")]), regras([
            regra(did, ev(did, "A administração da sociedade compete a ambos os sócios"), "geral", "conjunto", ["LARISSA", "THIAGO"],
                  expressao="mediante a assinatura de ambos")])
    raise KeyError(did)


# ------------------------------------------------------------------------------------ atas
def gold_ata(did: str) -> sc.ExtracaoAta:
    if did == "CAMOCIM_ATA":
        return sc.ExtracaoAta(data="2026-08-28", orgao="reuniao_socios",
                              presentes=[sc.Socio(nome=nome("VALDIR"), cpf=P["VALDIR"]["cpf"], percentual=40),
                                         sc.Socio(nome=nome("OSVALDO"), cpf=P["OSVALDO"]["cpf"], percentual=25)],
                              deliberacoes=[sc.Deliberacao(evidencia=ev(did, "pelo valor mínimo de R\\$ 300"), assunto="alienação do VW/Delivery",
                                                           tipo="aprova_alienacao_veiculo", aprovada=True, percentual_favoravel=65,
                                                           veiculos=[vref("DELIVERY")], valor_minimo=300000.0, eleitos=[])])
    if did == "ARACATI_RCA":
        eleitos = [sc.Eleito(nome=nome(p), cpf=P[p]["cpf"], cargo=c, mandato_descricao="2 (dois) anos", mandato_termino="2027-05-02")
                   for p, c in (("MARCELO", "Diretor-Presidente"), ("HELENA", "Diretora Financeira"), ("TIAGO", "Diretor Comercial"))]
        return sc.ExtracaoAta(data="2025-05-02", orgao="conselho_administracao", presentes=[],
                              deliberacoes=[sc.Deliberacao(evidencia=ev(did, "com mandato de 2 \\(dois\\) anos"), assunto="eleição da Diretoria",
                                                           tipo="eleicao_administradores", aprovada=True, percentual_favoravel=None,
                                                           veiculos=[], valor_minimo=None, eleitos=eleitos)])
    if did == "COOPVALE_ATA_AGO":
        eleitos = [sc.Eleito(nome=nome(p), cpf=P[p]["cpf"], cargo=c, mandato_descricao="4 (quatro) anos", mandato_termino="2029-03-28")
                   for p, c in (("MANOEL", "Diretor-Presidente"), ("JOANA", "Vice-Presidente"), ("CICERO", "Secretário"),
                                ("EXPEDITO", "Diretor Financeiro"))]
        return sc.ExtracaoAta(data="2025-03-28", orgao="assembleia_socios", presentes=[],
                              deliberacoes=[sc.Deliberacao(evidencia=ev(did, "para o mandato de 4 \\(quatro\\) anos"),
                                                           assunto="eleição do Conselho de Administração", tipo="eleicao_administradores",
                                                           aprovada=True, percentual_favoravel=None, veiculos=[], valor_minimo=None,
                                                           eleitos=eleitos)])
    if did == "ASSOC_ATA_ELEICAO":
        eleitos = [sc.Eleito(nome=nome(p), cpf=P[p]["cpf"], cargo=c, mandato_descricao="triênio 2024/2027", mandato_termino="2027-02-16")
                   for p, c in (("SOCORRO", "Presidente"), ("FRANCISCA", "Vice-Presidente"), ("PAULO", "Tesoureiro"))]
        sec = re.search(r"Secretári[ao]: ([A-ZÀ-Ú ]+?), .{0,200}?CPF sob o nº ([\d.\-]+)", _texto(did))  # nome inventado pelo redator
        if sec:
            eleitos.append(sc.Eleito(nome=sec.group(1).strip(), cpf=sec.group(2), cargo="Secretária",
                                     mandato_descricao="triênio 2024/2027", mandato_termino="2027-02-16"))
        return sc.ExtracaoAta(data="2024-02-17", orgao="assembleia_socios", presentes=[],
                              deliberacoes=[sc.Deliberacao(evidencia=ev(did, "para o triênio 2024/2027"), assunto="eleição da Diretoria",
                                                           tipo="eleicao_administradores", aprovada=True, percentual_favoravel=None,
                                                           veiculos=[], valor_minimo=None, eleitos=eleitos)])
    raise KeyError(did)


# ------------------------------------------------------------------------------ procurações
def outorgante_pj(did, emp, reps):
    e = E[emp]
    return sc.Outorgante(evidencia=ev(did, r"OUTORGANTE.{0,40}" + re.escape(e["razao_social"].split()[0]), re.escape(e["razao_social"])),
                         tipo="PJ", nome=e["razao_social"], documento=e["cnpj"], representantes=[pref(r) for r in reps],
                         age_em_nome_da_empresa=False)


def poa(did, emp, reps, outorgados, *, alienar=True, gerais=False, abr="todos_veiculos_da_outorgante", veics=(), forma="publica",
        firma=None, val_tipo="prazo", fim=None, prazo=None, sub="omisso", atuacao=None, exige="nenhum", pf=None, proprio=False):
    d = SPEC["documentos"][did]
    t = _texto(did)
    livro = re.search(r"LIVRO (?:N[ºo°] ?)?([\w-]+)", t, re.I)
    folhas = re.search(r"FOLHAS? (?:N[ºo°] ?)?([\d/]+)", t, re.I)
    if pf:
        out = sc.Outorgante(evidencia=ev(did, "OUTORGANTE"), tipo="PF", nome=nome(pf), documento=P[pf]["cpf"], representantes=[],
                            age_em_nome_da_empresa=False)
    else:
        out = outorgante_pj(did, emp, reps)
    pod_ev = ev(did, "poderes especiais", "amplos e gerais poderes", "poderes")
    return sc.ExtracaoProcuracao(
        forma=forma, cartorio=None, livro=livro.group(1) if livro and forma == "publica" else None,
        folhas=folhas.group(1) if folhas and forma == "publica" else None, data_outorga=d["data"], firma_reconhecida=firma,
        outorgante=out, outorgados=[pref(o) for o in outorgados],
        atuacao_outorgados=atuacao or ("isolada" if len(outorgados) == 1 else "nao_especificada"),
        poderes=sc.Poderes(evidencia=pod_ev, alienar_veiculos=alienar, assinar_atpv=alienar, poderes_especiais_expressos=alienar,
                           apenas_administracao_geral=gerais, abrangencia=abr, veiculos=[vref(v) for v in veics],
                           bens_do_proprio_outorgante=proprio, exige_conjunto_com=exige),
        validade=sc.Validade(evidencia=ev(did, "prazo", "válid", "vigorar", "validade"), tipo=val_tipo, data_fim=fim, prazo_texto=prazo),
        substabelecimento=sc.Substab(evidencia=ev(did, "substabelec") if sub != "omisso" else None, regra=sub),
        irrevogavel=False, em_causa_propria=False)


def gold_procuracao(did: str) -> sc.ExtracaoProcuracao:
    if did == "POA_PEDRO":
        return poa(did, "JANGADA", ["FRANCISCO"], ["PEDRO"], fim="2027-02-10", prazo="1 (um) ano", sub="permitido_com_reserva")
    if did == "POA_RODRIGO":
        return poa(did, "JANGADA", ["FRANCISCO"], ["RODRIGO"], alienar=False, gerais=True, abr="nao_aplicavel", val_tipo="ate_data",
                   fim="2026-12-31")
    if did == "POA_KLEBER_VENCIDA":
        return poa(did, "MANDACARU", ["CARLOS", "LUCIANA"], ["KLEBER"], fim="2025-07-20", prazo="6 (seis) meses", sub="vedado")
    if did == "POA_FABIO_REVOGADA":
        return poa(did, "CARIRI", ["ANTONIO"], ["FABIO"], val_tipo="indeterminado")
    if did == "POA_KLEBER_SO_CARLOS":
        return poa(did, "MANDACARU", ["CARLOS"], ["KLEBER"], fim="2027-04-02", prazo="1 (um) ano")
    if did == "POA_PF_JOAO":
        return poa(did, "SERTAO", [], ["KLEBER"], forma="particular", firma=True, fim="2027-05-14", prazo="1 (um) ano", pf="JOAO",
                   proprio=True)
    if did == "POA_ANAPAULA_CIVIC":
        return poa(did, "TECH", ["RAFAEL"], ["ANAPAULA"], abr="veiculos_especificos", veics=["CIVIC"], fim="2026-09-29",
                   prazo="90 (noventa) dias")
    if did == "POA_IGOR":
        return poa(did, "TECH", ["RAFAEL"], ["IGOR"], fim="2027-03-10", prazo="1 (um) ano", sub="vedado")
    if did == "POA_FABIO_2026":
        return poa(did, "CARIRI", ["JOSEFA"], ["FABIO"], fim="2028-01-15", prazo="2 (dois) anos", sub="permitido")
    if did == "POA_CAMILA":
        return poa(did, "TECH", ["RAFAEL"], ["CAMILA"], abr="veiculos_especificos", veics=["PULSE"], forma="particular", firma=False,
                   fim="2027-02-01", prazo="6 (seis) meses")
    if did == "POA_SERGIO_BRUNA":
        return poa(did, "MARACANAU", ["GUSTAVO"], ["SERGIO", "BRUNA"], fim="2027-05-20", prazo="1 (um) ano", atuacao="conjunta")
    if did == "POA_DAVI":
        return poa(did, "CHAPADA", ["JOAQUIM"], ["DAVI"], val_tipo="ate_data", fim="2026-12-10")
    if did == "POA_SERGIO_SA":
        return poa(did, "ARACATI", ["MARCELO", "HELENA"], ["SERGIO"], fim="2027-02-18", prazo="1 (um) ano", sub="vedado", exige="diretor")
    if did == "POA_BRUNA_2023":
        return poa(did, "MARACANAU", ["GUSTAVO"], ["BRUNA"], val_tipo="indeterminado")
    # ---- lote consulta por CPF: procurações de pessoa física, em nome próprio
    if did == "POA_PF_HB20":
        return poa(did, None, [], ["JOSUELIMA"], pf="RAIMUNDA", proprio=True, abr="veiculos_especificos", veics=["P_HB20"],
                   fim="2027-08-12", prazo="1 (um) ano")
    if did == "POA_PF_VENCIDA":
        return poa(did, None, [], ["EDVALDO"], pf="RAIMUNDA", proprio=True, fim="2026-04-01", prazo="6 (seis) meses")
    if did == "POA_PF_ADMIN":
        return poa(did, None, [], ["PATRICIA"], pf="ERIVAN", proprio=True, alienar=False, gerais=True, abr="nao_aplicavel",
                   fim="2027-04-15", prazo="1 (um) ano")
    if did == "POA_PF_ONIX":
        return poa(did, None, [], ["JOSUELIMA"], pf="ERIVAN", proprio=True, abr="veiculos_especificos", veics=["P_ONIX"],
                   fim="2027-07-20", prazo="1 (um) ano")
    if did == "POA_PF_PARTICULAR":
        return poa(did, None, [], ["EDVALDO"], pf="ERIVAN", proprio=True, abr="veiculos_especificos", veics=["P_STRADA"],
                   forma="particular", firma=True, fim="2027-09-05", prazo="1 (um) ano")
    if did == "POA_PF_CONJUGE":
        return poa(did, None, [], ["JOSUELIMA"], pf="MARTA", abr="veiculos_especificos", veics=["P_STRADA"], fim="2027-08-28",
                   prazo="1 (um) ano")
    if did == "POA_PF_TODOS_GILMAR":
        return poa(did, None, [], ["EDVALDO"], pf="GILMAR", proprio=True, val_tipo="indeterminado")
    if did == "POA_PF_COMPRA_VALERIA":
        x = poa(did, None, [], ["PATRICIA"], pf="VALERIA", alienar=False, abr="nao_aplicavel", fim="2027-03-10",
                prazo="6 (seis) meses")
        x.poderes.evidencia = ev(did, r"comprar ou adquirir.{0,400}?\(ATPV-e\)", "poderes especiais")
        x.poderes.assinar_atpv = x.poderes.poderes_especiais_expressos = True
        return x
    if did == "POA_ELIAS_COMPRA":  # poder de COMPRA (e só de compra): não aliena
        x = poa(did, "JANGADA", ["FRANCISCO"], ["ELIAS"], alienar=False, abr="nao_aplicavel", fim="2027-07-20", prazo="1 (um) ano")
        x.poderes.evidencia = ev(did, r"comprar, adquirir ou receber em transferência.{0,400}?\(ATPV-e\)", "poderes especiais")
        x.poderes.assinar_atpv = x.poderes.poderes_especiais_expressos = True
        return x
    raise KeyError(did)


def gold_sub(did: str) -> sc.ExtracaoSubstabelecimento:
    t = _texto(did)
    livro = re.search(r"livro (?:n[ºo°] ?)?([\w-]+)", t, re.I)
    folhas = re.search(r"folhas? (?:n[ºo°] ?)?([\d/]+)", t, re.I)
    cfg = {"SUB_PEDRO_ANAPAULA": ("publica", None, "2026-08-03", "2026-02-10", "PEDRO", "ANAPAULA", "com_reserva", True),
           "SUB_PF_JOSUE_PATRICIA": ("publica", None, "2026-09-30", "2026-08-12", "JOSUELIMA", "PATRICIA", "com_reserva", True),
           "SUB_IGOR_KLEBER": ("particular", True, "2026-08-20", "2026-03-10", "IGOR", "KLEBER", "com_reserva", False),
           "SUB_FABIO_ANAPAULA": ("publica", None, "2026-06-30", "2026-01-15", "FABIO", "ANAPAULA", "sem_reserva", True)}[did]
    forma, firma, data, data_origem, de, para, reserva, todos = cfg
    return sc.ExtracaoSubstabelecimento(
        evidencia=ev(did, "com reserva", "sem reserva", "substabelece"), forma=forma, data=data, firma_reconhecida=firma,
        procuracao_origem=sc.RefProcuracao(data=data_origem, cartorio=None, livro=livro.group(1) if livro else None,
                                           folhas=folhas.group(1) if folhas else None, outorgante_nome=None, outorgado_nome=nome(de)),
        substabelecente=pref(de), substabelecidos=[pref(para)], reserva=reserva, todos_os_poderes=todos, alienar_veiculos=True)


def gold_revogacao(did: str) -> sc.ExtracaoRevogacao:
    t = _texto(did)
    livro = re.search(r"livro (?:n[ºo°] ?)?([\w-]+)", t, re.I)
    folhas = re.search(r"folhas? (?:n[ºo°] ?)?([\d/]+)", t, re.I)
    if did == "REV_PF_GILMAR":
        return sc.ExtracaoRevogacao(
            evidencia=ev(did, "revoga"), forma="publica", data="2026-06-10",
            revogante=sc.Outorgante(evidencia=ev(did, re.escape(nome("GILMAR"))), tipo="PF", nome=nome("GILMAR"),
                                    documento=P["GILMAR"]["cpf"], representantes=[], age_em_nome_da_empresa=False),
            procuracao_revogada=sc.RefProcuracao(data="2026-01-20", cartorio=None, livro=livro.group(1) if livro else None,
                                                 folhas=folhas.group(1) if folhas else None, outorgante_nome=nome("GILMAR"),
                                                 outorgado_nome=nome("EDVALDO")))
    return sc.ExtracaoRevogacao(
        evidencia=ev(did, "revoga"), forma="publica", data="2026-06-12", revogante=outorgante_pj(did, "CARIRI", ["JOSEFA"]),
        procuracao_revogada=sc.RefProcuracao(data="2025-11-03", cartorio=None, livro=livro.group(1) if livro else None,
                                             folhas=folhas.group(1) if folhas else None, outorgante_nome=E["CARIRI"]["razao_social"],
                                             outorgado_nome=nome("FABIO")))


def gold_crlv(caso: dict) -> sc.ExtracaoCRLV:
    v = V[caso["veiculo"]]
    dono = caso["crlv_proprietario"]
    if dono["tipo"] == "PJ":
        n, d = E[dono["empresa"]]["razao_social"], E[dono["empresa"]]["cnpj"]
    else:
        n, d = nome(dono["pessoa"]), P[dono["pessoa"]]["cpf"]
    return sc.ExtracaoCRLV(placa=v["placa"], renavam=v["renavam"], chassi=v["chassi"], marca_modelo=v["marca_modelo"],
                           ano_fabricacao=v["ano_fabricacao"], ano_modelo=v["ano_modelo"], proprietario_nome=n, proprietario_documento=d)


TITULOS = {"contrato_social": "Contrato Social", "contrato_consolidado": "Contrato Social Consolidado",
           "alteracao_contratual": "Alteração Contratual", "estatuto_social": "Estatuto Social",
           "ato_constitutivo_slu": "Ato Constitutivo (SLU)", "requerimento_empresario": "Requerimento de Empresário"}


def gold_atpv(caso: dict) -> sc.ExtracaoATPV:
    v = V[caso["veiculo"]]

    def parte(x):
        if "empresa" in x:
            return sc.ParteATPV(tipo="PJ", nome=E[x["empresa"]]["razao_social"], documento=E[x["empresa"]]["cnpj"])
        return sc.ParteATPV(tipo="PF", nome=nome(x["pessoa"]), documento=P[x["pessoa"]]["cpf"])

    ass = []
    if caso.get("assinaturas_na_atpv"):
        for lado in ("vendedor", "comprador"):
            x = caso[lado]
            pids = [a["pessoa"] for a in x.get("assinantes", [])] if "empresa" in x else [x["pessoa"]]
            ass += [sc.AssinaturaATPV(nome=nome(pid), cpf=P[pid]["cpf"], lado=lado) for pid in pids]
    t = caso["transacao"]
    return sc.ExtracaoATPV(numero=caso["atpv_numero"], placa=v["placa"], renavam=v["renavam"], chassi=v["chassi"],
                           marca_modelo=v["marca_modelo"], valor=float(t["valor"]), data=t["data_venda"],
                           vendedor=parte(caso["vendedor"]), comprador=parte(caso["comprador"]), assinaturas=ass)


def leituras_gold(caso_id: str) -> list[LeituraDocumento]:
    caso = next(c for c in SPEC["casos"] + SPEC.get("casos_holdout", []) + SPEC.get("casos_atpv", []) + SPEC.get("casos_pf", [])
                if c["id"] == caso_id)
    pasta = AQUI / "casos" / caso_id / "docs"
    out = []
    for did in caso["documentos"]:
        doc = carregar(pasta / f"{did}.pdf", did)
        d = SPEC["documentos"][did]
        tipo = d["tipo"]
        if tipo in ("procuracao",):
            cl = sc.Classificacao(tipo="procuracao", titulo=f"Procuração ({did})", data_documento=d["data"], confianca=1)
            out.append(LeituraDocumento(doc, cl, procuracao=gold_procuracao(did)))
        elif tipo == "substabelecimento":
            cl = sc.Classificacao(tipo="substabelecimento", titulo=f"Substabelecimento ({did})", data_documento=d["data"], confianca=1)
            out.append(LeituraDocumento(doc, cl, substabelecimento=gold_sub(did)))
        elif tipo == "revogacao_procuracao":
            cl = sc.Classificacao(tipo="revogacao_procuracao", titulo="Revogação de procuração", data_documento=d["data"], confianca=1)
            out.append(LeituraDocumento(doc, cl, revogacao=gold_revogacao(did)))
        elif tipo in ("ata_reuniao_socios", "ata_conselho", "ata_assembleia"):
            cl = sc.Classificacao(tipo=tipo, titulo=d["titulo"].title(), data_documento=d["data"], confianca=1)
            lt = LeituraDocumento(doc, cl, ata=gold_ata(did))
            if d.get("registro"):
                lt.partes = None
            out.append(lt)
        else:
            tipo_cl, partes_, regras_ = gold_societario(did)
            cl = sc.Classificacao(tipo=tipo_cl, titulo=f"{TITULOS.get(tipo_cl, d['titulo'].title())} ({d['data'][:4]})",
                                  data_documento=d["data"], confianca=1)
            out.append(LeituraDocumento(doc, cl, partes=partes_, regras=regras_))
    if (pasta / "CRLV.pdf").exists():  # consulta por CPF: o dono vem da base veicular, sem CRLV
        crlv = carregar(pasta / "CRLV.pdf", "CRLV")
        out.append(LeituraDocumento(crlv, sc.Classificacao(tipo="crlv", titulo="CRLV", data_documento=None, confianca=1),
                                    crlv=gold_crlv(caso)))
    if (pasta / "ATPV-e.pdf").exists():
        atpv = carregar(pasta / "ATPV-e.pdf", "ATPV-e")
        out.append(LeituraDocumento(atpv, sc.Classificacao(tipo="atpv", titulo="ATPV-e", data_documento=caso["transacao"]["data_venda"],
                                                           confianca=1), atpv=gold_atpv(caso)))
    return out
