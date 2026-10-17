"""Consolidação: leituras do LLM (por documento) → base de conhecimento única e conferida.

Etapas:
1. resolução de identidade (mesma pessoa em documentos diferentes: CPF válido > nome aproximado);
2. conversão de cada extração para o modelo de domínio (datas, chaves, veículos);
3. conferência léxica (o LLM disse "conjunto", mas a expressão citada é "indistintamente"?) — corrige e registra;
4. ancoragem de cada evidência no texto original (página/posição/score);
5. confiança por fato = ancoragem × conferência × qualidade do OCR.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from . import lexicon as lx
from .domain import (
    CRLV, Administrador, AtoSocietario, BaseConhecimento, BemIntegralizado, DeliberacaoSocios, DocumentoInfo,
    Empresa, Fonte, Grupo, Pessoa, Procuracao, RegraRep, RegrasProcuracaoEmpresa, Revogacao, Substabelecimento,
    VeiculoId, Verificacao, fator_ancoragem,
)
from .grounding import Ancorador
from .ids import cnpj_valido, cpf_valido, normalizar_nome, similaridade_nomes, so_digitos
from .ingest import Documento
from . import schemas as sc

SOCIETARIOS = {"contrato_social", "alteracao_contratual", "contrato_consolidado", "estatuto_social", "ato_constitutivo_slu",
               "requerimento_empresario"}
ATAS = {"ata_reuniao_socios", "ata_assembleia", "ata_conselho"}


@dataclass
class LeituraDocumento:
    """Tudo o que foi lido de um documento (por LLM ou gabarito)."""
    doc: Documento
    classificacao: sc.Classificacao
    partes: sc.ExtracaoPartes | None = None
    regras: sc.ExtracaoRegras | None = None
    ata: sc.ExtracaoAta | None = None
    procuracao: sc.ExtracaoProcuracao | None = None
    substabelecimento: sc.ExtracaoSubstabelecimento | None = None
    revogacao: sc.ExtracaoRevogacao | None = None
    crlv: sc.ExtracaoCRLV | None = None
    atpv: sc.ExtracaoATPV | None = None
    consistencia: dict[str, float] = field(default_factory=dict)  # concordância entre amostras (0-1)
    meta: dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------------------------- identidades
class Identidades:
    def __init__(self):
        self.pessoas: dict[str, Pessoa] = {}
        self.avisos: list[str] = []
        self._remap: dict[str, str] = {}

    def registrar(self, nome: str | None, cpf: str | None) -> str | None:
        if not nome or not nome.strip() or lx.nome_vazio(nome):
            return None
        nome = nome.strip()
        d = so_digitos(cpf)
        if d and not cpf_valido(d):
            self.avisos.append(f"CPF inválido ignorado para {nome}: {cpf}")
            d = ""
        if d:
            if d in self.pessoas:
                self.pessoas[d].aliases.add(nome)
                return d
            # já existia só pelo nome? promove para chave CPF
            for k, p in list(self.pessoas.items()):
                if k.startswith("N:") and similaridade_nomes(p.nome, nome) >= 92:
                    del self.pessoas[k]
                    p.chave, p.cpf = d, d
                    p.aliases.add(nome)
                    self.pessoas[d] = p
                    self._remap[k] = d
                    return d
            self.pessoas[d] = Pessoa(d, self._nome_bonito(nome), d, {nome})
            return d
        melhor, score = None, 0.0
        for k, p in self.pessoas.items():
            s = max(similaridade_nomes(a, nome) for a in p.aliases | {p.nome})
            if s > score:
                melhor, score = k, s
        if melhor and score >= 90:
            self.pessoas[melhor].aliases.add(nome)
            return melhor
        k = "N:" + normalizar_nome(nome)
        self.pessoas[k] = Pessoa(k, self._nome_bonito(nome), None, {nome})
        return k

    def chave(self, k: str | None) -> str | None:
        while k in self._remap:
            k = self._remap[k]
        return k

    @staticmethod
    def _nome_bonito(nome: str) -> str:
        if nome.isupper():
            minus = {"da", "de", "do", "das", "dos", "e"}
            return " ".join(w.lower() if w.lower() in minus else w.capitalize() for w in nome.split())
        return nome


# ---------------------------------------------------------------------------------- helpers
def _d(s: str | None) -> date | None:
    return lx.parse_data(s) if s else None


def _veic(v: sc.VeiculoRef | None) -> VeiculoId | None:
    if v is None or not (v.placa or v.renavam or v.chassi or v.descricao):
        return None
    return VeiculoId(v.descricao, v.placa, v.renavam, v.chassi)


class Consolidador:
    def __init__(self, leituras: list[LeituraDocumento]):
        self.leituras = leituras
        self.ids = Identidades()
        self.ancoradores = {l.doc.id: Ancorador(l.doc) for l in leituras}
        self.avisos: list[str] = []

    # fonte ancorada
    def fonte(self, leitura: LeituraDocumento, trecho: str | None, clausula: str | None = None) -> Fonte:
        a = self.ancoradores[leitura.doc.id].ancorar(trecho) if trecho else None
        return Fonte(leitura.doc.id, leitura.classificacao.titulo or leitura.doc.nome, trecho, clausula,
                     a.score if a else None, a.pagina if a else None, a.inicio if a else None, a.fim if a else None)

    def _fator_ocr(self, leitura: LeituraDocumento) -> float:
        c = leitura.doc.ocr_confianca
        if c is None:
            return 1.0
        return max(0.5, min(1.0, 0.55 + c / 200))  # 90% => 1.0; 70% => 0.9; 40% => 0.75

    def _conf(self, leitura: LeituraDocumento, fonte: Fonte | None, divergencias: int = 0, chave_consist: str | None = None) -> float:
        anc = fator_ancoragem(fonte.ancoragem) if fonte and fonte.trecho else 0.7
        c = anc * (0.8 ** divergencias) * self._fator_ocr(leitura)
        if chave_consist and chave_consist in leitura.consistencia:
            c *= 0.5 + 0.5 * leitura.consistencia[chave_consist]
        return round(min(1.0, c), 3)

    # --------------------------------------------------------------------------- pessoas
    def _registrar_pessoas(self) -> None:
        for l in self.leituras:
            if l.partes:
                for s in l.partes.socios:
                    self.ids.registrar(s.nome, s.cpf)
                for a in l.partes.administradores:
                    self.ids.registrar(a.nome, a.cpf)
            if l.ata:
                for p in l.ata.presentes:
                    self.ids.registrar(p.nome, p.cpf)
                for dlb in l.ata.deliberacoes:
                    for e in dlb.eleitos:
                        self.ids.registrar(e.nome, e.cpf)
            if l.procuracao:
                for r in l.procuracao.outorgante.representantes:
                    self.ids.registrar(r.nome, r.cpf)
                if l.procuracao.outorgante.tipo == "PF":
                    self.ids.registrar(l.procuracao.outorgante.nome, l.procuracao.outorgante.documento)
                for o in l.procuracao.outorgados:
                    self.ids.registrar(o.nome, o.cpf)
            if l.substabelecimento:
                self.ids.registrar(l.substabelecimento.substabelecente.nome, l.substabelecimento.substabelecente.cpf)
                for o in l.substabelecimento.substabelecidos:
                    self.ids.registrar(o.nome, o.cpf)
            if l.revogacao:
                for r in l.revogacao.revogante.representantes:
                    self.ids.registrar(r.nome, r.cpf)

    def k(self, nome: str | None, cpf: str | None = None) -> str | None:
        return self.ids.chave(self.ids.registrar(nome, cpf))

    # ---------------------------------------------------------------------------- empresa
    def _empresa(self) -> Empresa:
        candidatos = [l for l in self.leituras if l.partes]
        candidatos.sort(key=lambda l: _d(l.partes.documento.data_assinatura) or date.min)
        if not candidatos:
            # sem ato societário: tenta pela procuração/CRLV
            l = next((l for l in self.leituras if l.procuracao and l.procuracao.outorgante.tipo == "PJ"), None)
            if l:
                o = l.procuracao.outorgante
                return Empresa(o.nome, o.documento, "OUTRO", "", False)
            return Empresa("(empresa não identificada)", None, "OUTRO", "", False)
        ult = candidatos[-1].partes.empresa
        cnpjs = {so_digitos(l.partes.empresa.cnpj) for l in candidatos if l.partes.empresa.cnpj and cnpj_valido(l.partes.empresa.cnpj)}
        if len(cnpjs) > 1:
            self.avisos.append("Documentos societários com CNPJs diferentes: " + ", ".join(sorted(cnpjs)))
        cnpj = ult.cnpj if ult.cnpj and cnpj_valido(ult.cnpj) else next(iter(cnpjs), ult.cnpj)
        tipo = ult.tipo_societario
        if any(l.partes.empresa.tipo_societario == "SLU" for l in candidatos) and tipo == "LTDA":
            tipo = "SLU"
        subtipo = None
        nome_t = lx.norm(ult.razao_social + " " + " ".join(l.classificacao.titulo or "" for l in candidatos))
        textos = lx.norm(" ".join(l.doc.texto[:3000] for l in candidatos))
        if tipo == "EIRELI" or "eireli" in nome_t or "empresa individual de responsabilidade limitada" in textos:
            tipo, subtipo = "SLU", "EIRELI"   # Lei 14.195/2021, art. 41: EIRELI virou SLU
        elif "microempreendedor individual" in textos or "ccmei" in textos:
            tipo, subtipo = "EI", "MEI"
        elif "cooperativa" in nome_t or tipo == "COOPERATIVA":
            tipo, subtipo = "COOPERATIVA", "COOPERATIVA"
        elif re.search(r"\b(associacao|fundacao|instituto|igreja|organizacao religiosa)\b", nome_t):
            tipo, subtipo = "ASSOCIACAO", ("FUNDACAO" if "fundacao" in nome_t else "ASSOCIACAO")
        elif tipo == "SS" or "sociedade simples" in textos:
            subtipo = "SS"
        return Empresa(ult.razao_social, cnpj, tipo, ult.objeto_social,
                       any(l.partes.empresa.comercializa_veiculos for l in candidatos), subtipo)

    def _e_empresa(self, emp: Empresa, nome: str | None, doc: str | None) -> bool:
        if doc and emp.cnpj and so_digitos(doc) == so_digitos(emp.cnpj):
            return True
        if nome and emp.razao_social:
            return similaridade_nomes(nome.replace("LTDA", "").replace("S.A.", ""),
                                      emp.razao_social.replace("LTDA", "").replace("S.A.", "")) >= 85
        return False

    # ------------------------------------------------------------------------ regras + léxico
    def _regra(self, l: LeituraDocumento, r: sc.Regra, idx: int) -> RegraRep:
        f = self.fonte(l, r.evidencia, r.clausula)
        verifs: list[Verificacao] = []
        modo, escopo = r.modo, r.escopo
        # 1) forma de atuação: a expressão citada manda
        sinal = lx.modo_por_lexico(r.expressao_modo) if r.expressao_modo else lx.SinalModo(None)
        if sinal.modo is None:
            sinal = lx.modo_por_lexico(r.evidencia)
        if sinal.modo and modo in ("isolado", "conjunto", "nao_especificado") and sinal.modo != modo and sinal.certeza >= 0.85:
            verifs.append(Verificacao("modo", modo, sinal.modo, True, sinal.modo, sinal.expressoes))
            modo = sinal.modo
        elif sinal.modo:
            verifs.append(Verificacao("modo", modo, sinal.modo, False, None, sinal.expressoes))
        # 2) escopo do bem
        esc = lx.escopo_por_lexico(r.evidencia)
        novo = escopo
        if escopo in ("alienacao_bens", "alienacao_bens_moveis", "geral", "alienacao_ativo_imobilizado", "outro") and esc.so_imoveis \
                and (esc.alienacao or esc.oneracao):
            novo = "alienacao_bens_imoveis"
        elif escopo == "alienacao_bens_imoveis" and (esc.menciona_veiculo or esc.menciona_imobilizado) and not esc.so_imoveis:
            novo = "alienacao_veiculos" if esc.menciona_veiculo else "alienacao_ativo_imobilizado"
        elif escopo == "onerar_bens" and esc.alienacao:
            novo = "alienacao_veiculos" if esc.menciona_veiculo else ("alienacao_bens_imoveis" if esc.so_imoveis else "alienacao_bens")
        elif escopo in ("outro", "geral", "alienacao_bens") and esc.menciona_veiculo and esc.alienacao and (r.valor_acima_de or r.veiculo is None):
            novo = "alienacao_veiculos" if escopo != "geral" or r.valor_acima_de else escopo
        if novo != escopo:
            contradiz = {escopo, novo} & {"alienacao_bens_imoveis"} != set() or escopo in ("onerar_bens", "outro")
            verifs.append(Verificacao("escopo", escopo, novo, contradiz, novo, []))
            escopo = novo
        # 3) pessoas → chaves (casando com quem já existe); cargos nomeados ("Presidente") viram "@cargo:..."
        def ref(n: str) -> str | None:
            return f"@cargo:{n.strip()}" if lx.e_cargo(n) else self.k(n)

        pessoas = [ref(n) for n in r.pessoas if n and len(n) > 3 and not lx.norm(n).startswith(("socios", "administrador"))]
        pessoas = [p for p in pessoas if p]
        cargo, qtd_lida = r.cargo, r.quantidade_minima
        if not pessoas and cargo in (None, "administradores", "diretores") and modo != "misto":
            # "Compete ao Presidente representar..." lido como "administradores" (o schema só tem cargos genéricos):
            # vale só o cargo nomeado — restringe, nunca amplia
            nomeados = lx.cargos_signatarios(r.evidencia)
            # um cargo só: apenas se a leitura já é de atuação isolada ("pelo Diretor-Presidente em conjunto com outro
            # Diretor" continua exigindo dois); dois cargos nomeados juntos: assinatura conjunta dos dois
            if len(nomeados) >= 2 or (nomeados and modo in ("isolado", "nao_especificado")):
                verifs.append(Verificacao("pessoas", cargo or "—", " + ".join(nomeados), True, " + ".join(nomeados), []))
                pessoas, cargo, qtd_lida = [f"@cargo:{n}" for n in nomeados], None, None
                if len(nomeados) > 1:
                    modo = "conjunto"
        anuencia = [ref(n) for n in r.exige_anuencia_de if n]
        combs = [[Grupo(g.cargo, [ref(g.pessoa)] if g.pessoa else [], max(1, g.quantidade)) for g in c.grupos]
                 for c in r.combinacoes] if modo == "misto" else []
        quorum = r.quorum_percentual
        if r.exige_aprovacao_socios and quorum is None:
            t = lx.norm(r.evidencia)
            quorum = 75.0 if "tres quartos" in t or "3/4" in t else (50.01 if "metade" in t or "maioria" in t else None)
        valor_acima = r.valor_acima_de
        if valor_acima is None and r.valor_ate is None:
            valor_acima = lx.valor_limite_do_ato(r.evidencia)  # só o limite do próprio ato, nunca o de outro inciso
            if valor_acima:
                verifs.append(Verificacao("valor_acima_de", None, valor_acima, True, valor_acima, []))
        qtd = qtd_lida
        # a quantidade explícita só COMPLETA a leitura (conjunto sem número / quantidade ausente), nunca sobrescreve
        if (modo == "conjunto" or (modo == "quantidade_minima" and not qtd)) and (cargo or len(pessoas) > 2):
            q_lex = lx.quantidade_por_lexico(r.expressao_modo) or lx.quantidade_por_lexico(r.evidencia)
            if q_lex and q_lex > 1 and (qtd != q_lex or modo != "quantidade_minima"):
                verifs.append(Verificacao("quantidade_minima", f"{modo}/{qtd}", f"quantidade_minima/{q_lex}",
                                          modo == "conjunto" and qtd is None, f"quantidade_minima/{q_lex}", []))
                modo, qtd = "quantidade_minima", q_lex
        efeito = r.efeito
        if efeito == "veda" and modo == "conjunto":  # "vedada a prática isolada" = exige assinatura conjunta
            verifs.append(Verificacao("efeito", "veda", "restringe", False, "restringe", []))
            efeito = "restringe"
        atos, nivel_aq = lx.atos_da_regra(escopo, r.evidencia)
        if escopo.startswith("alienacao") and "alienar" not in atos:  # regra de COMPRA rotulada como alienação
            verifs.append(Verificacao("ato", "alienar", "adquirir", True, "adquirir", []))
        elif (efeito == "autoriza" and "adquirir" not in atos and escopo != "alienacao_bens_imoveis"
              and lx.clausula_geral_de_administracao(r.evidencia)):
            # a IA rotulou como "alienação" a cláusula geral de administração ("..., inclusive vender bens"): ela também
            # rege a compra (sem mudar o rótulo, para não mexer na especialidade do lado da venda)
            verifs.append(Verificacao("ato", "alienar", "alienar+adquirir", False, "alienar+adquirir", []))
            atos, nivel_aq = {"alienar", "adquirir"}, 0
        div = sum(1 for v in verifs if v.divergiu)
        substitutos = lx.cargos_substitutos(r.evidencia)
        return RegraRep(f"{l.doc.id}#R{idx + 1}", escopo, efeito, modo, pessoas, cargo, qtd, combs,
                        _veic(r.veiculo), valor_acima, r.valor_ate, r.exige_aprovacao_socios, quorum,
                        [a for a in anuencia if a], f, verifs, self._conf(l, f, div, "regras"), atos, nivel_aq, substitutos)

    # --------------------------------------------------------------------------- atos
    def _ato(self, l: LeituraDocumento) -> AtoSocietario:
        p = l.partes
        dt_ass, dt_reg = _d(p.documento.data_assinatura) or _d(l.classificacao.data_documento), _d(p.documento.data_registro)
        admins = []
        for a in p.administradores:
            if not self.k(a.nome, a.cpf):  # sem nome de pessoa ("null", "administradores"): não vira administrador
                continue
            f = self.fonte(l, a.evidencia)
            termino = _d(a.prazo.termino) if a.prazo.tipo == "determinado" else None
            admins.append(Administrador(self.k(a.nome, a.cpf), a.cargo, a.socio, dt_ass, termino,
                                        a.prazo.descricao if a.prazo.tipo == "determinado" else None, f))
        socios = {}
        for s in p.socios:
            kk = self.k(s.nome, s.cpf)
            if kk:
                socios[kk] = float(s.percentual) if s.percentual is not None else 0.0
        if socios and all(v == 0 for v in socios.values()):
            socios = {k: round(100 / len(socios), 2) for k in socios}
        regras = [self._regra(l, r, i) for i, r in enumerate(l.regras.regras)] if l.regras else []
        rp = None
        if l.regras and l.regras.regras_procuracao and (l.regras.regras_procuracao.prazo_maximo_meses or
                                                        l.regras.regras_procuracao.vedada_para_alienacao or
                                                        l.regras.regras_procuracao.exige_poderes_especificados):
            x = l.regras.regras_procuracao
            rp = RegrasProcuracaoEmpresa(x.prazo_maximo_meses, x.exige_poderes_especificados, x.vedada_para_alienacao,
                                         self.fonte(l, x.evidencia))
        bens = [BemIntegralizado(self.k(b.socio_nome), b.descricao, _veic(b.veiculo), self.fonte(l, b.evidencia))
                for b in p.bens_integralizados]
        tipo = p.documento.tipo_detalhado
        if l.classificacao.tipo == "requerimento_empresario":
            tipo = "requerimento_empresario"
        consolida = tipo in ("alteracao_e_consolidacao", "estatuto") or l.classificacao.tipo == "contrato_consolidado"
        restricoes = [(self.fonte(l, t), atos) for t, atos in lx.clausulas_de_aprovacao(l.doc.texto)]
        return AtoSocietario(l.doc.id, l.classificacao.titulo, tipo, dt_ass, dt_reg, p.documento.numero_alteracao, consolida,
                             p.alteracao.altera_administracao or tipo == "constituicao", admins, socios, regras, rp, bens,
                             restricoes_texto=restricoes)

    def _ata(self, l: LeituraDocumento, socios_ref: dict[str, float]) -> tuple[AtoSocietario | None, list[DeliberacaoSocios]]:
        a = l.ata
        data = _d(a.data) or _d(l.classificacao.data_documento)
        eleitos, delibs = [], []
        # capital dos presentes: pelo quadro societário vigente (a leitura da ata pode somar errado); nunca > 100
        presentes_pct = 0.0
        for p in a.presentes:
            k = self.k(p.nome, p.cpf)
            presentes_pct += socios_ref.get(k, p.percentual or 0) if socios_ref else (p.percentual or 0)
        presentes_pct = min(100.0, presentes_pct)
        for i, dl in enumerate(a.deliberacoes):
            f = self.fonte(l, dl.evidencia)
            if dl.tipo == "eleicao_administradores":
                for e in dl.eleitos:
                    if lx.cargo_sem_representacao(e.cargo):  # Conselho Fiscal/suplentes fiscalizam, não representam
                        continue
                    termino = _d(e.mandato_termino)
                    if not termino and e.mandato_descricao and data:
                        termino = lx.somar_prazo(data, e.mandato_descricao)
                    if self.k(e.nome, e.cpf):
                        eleitos.append(Administrador(self.k(e.nome, e.cpf), e.cargo, False, data, termino,
                                                     e.mandato_descricao, f))
            elif dl.tipo == "aprova_alienacao_veiculo":
                pct = dl.percentual_favoravel if dl.percentual_favoravel is not None else presentes_pct
                t_ev = lx.norm(dl.evidencia + " " + l.doc.texto)
                if a.presentes and (pct > presentes_pct + 0.5 or "unanimidade dos presentes" in t_ev or "maioria dos presentes" in t_ev):
                    pct = presentes_pct  # "unanimidade dos presentes" não é 100% do capital
                pct = min(100.0, pct)
                delibs.append(DeliberacaoSocios(f"{l.doc.id}#D{i + 1}", data, dl.tipo, dl.aprovada, pct,
                                                [v for v in (_veic(x) for x in dl.veiculos) if v], dl.valor_minimo, f,
                                                self._conf(l, f)))
        ato = None
        if eleitos:
            reg = None
            if l.partes and l.partes.documento.data_registro:
                reg = _d(l.partes.documento.data_registro)
            ato = AtoSocietario(l.doc.id, l.classificacao.titulo, "ata", data, reg, None, False, True, eleitos, {}, [], None, [],
                                eleicao=True)
        return ato, delibs

    def _procuracao(self, l: LeituraDocumento, emp: Empresa) -> Procuracao:
        x = l.procuracao
        F = {"outorgante": self.fonte(l, x.outorgante.evidencia), "poderes": self.fonte(l, x.poderes.evidencia),
             "validade": self.fonte(l, x.validade.evidencia), "substabelecimento": self.fonte(l, x.substabelecimento.evidencia)}
        verifs = []
        texto = l.doc.texto
        # poderes: conferência pelo texto inteiro (o trecho citado pode vir cortado)
        lp = lx.poderes_por_lexico(x.poderes.evidencia)
        lt = lx.poderes_por_lexico(texto)
        alienar = x.poderes.alienar_veiculos
        if alienar and not (lp.alienar or lt.alienar):
            verifs.append(Verificacao("alienar_veiculos", True, False, True, False, []))
            alienar = False
        elif not alienar and lp.alienar and not lp.alienacao_negada and not x.poderes.apenas_administracao_geral:
            verifs.append(Verificacao("alienar_veiculos", False, True, True, None, []))  # sinaliza, não corrige
        apenas_gerais = x.poderes.apenas_administracao_geral
        if not apenas_gerais and not alienar and lt.gerais:
            apenas_gerais = True
        # substabelecimento: vedação explícita no texto prevalece
        sub = x.substabelecimento.regra
        sl = lx.substabelecimento_por_lexico(x.substabelecimento.evidencia) or lx.substabelecimento_por_lexico(texto)
        if sl == "vedado" and sub != "vedado":
            verifs.append(Verificacao("substabelecimento", sub, "vedado", True, "vedado", []))
            sub = "vedado"
        elif sub == "vedado" and sl and sl != "vedado":
            verifs.append(Verificacao("substabelecimento", sub, sl, True, sl, []))
            sub = sl
        elif sub == "omisso" and sl and sl.startswith("permitido"):
            verifs.append(Verificacao("substabelecimento", sub, sl, True, sl, []))
            sub = sl
        # validade
        data = _d(x.data_outorga) or _d(l.classificacao.data_documento)
        fim = _d(x.validade.data_fim)
        if not fim and x.validade.tipo == "prazo" and data:
            fim = lx.somar_prazo(data, x.validade.prazo_texto or x.validade.evidencia)
        if fim and data and x.validade.tipo == "prazo":
            calc = lx.somar_prazo(data, x.validade.prazo_texto or x.validade.evidencia)
            if calc and abs((calc - fim).days) > 3:
                verifs.append(Verificacao("validade_fim", fim.isoformat(), calc.isoformat(), True, calc.isoformat(), []))
                fim = calc
        # outorgante
        o = x.outorgante
        e_emp = o.tipo == "PJ" and self._e_empresa(emp, o.nome, o.documento)
        reps = [k for r in o.representantes if (k := self.k(r.nome, r.cpf))]
        if o.tipo == "PF":
            reps = [k for k in [self.k(o.nome, o.documento)] if k]
        outorgados = [k for p in x.outorgados if (k := self.k(p.nome, p.cpf))]
        atuacao = x.atuacao_outorgados
        if len(outorgados) > 1:
            sm = lx.modo_por_lexico(x.poderes.evidencia)
            t = lx.norm(texto)
            if atuacao != "conjunta" and ("sempre em conjunto" in t or "agindo sempre em conjunto" in t or "conjuntamente" in t) \
                    and x.poderes.exige_conjunto_com == "nenhum":
                verifs.append(Verificacao("atuacao_outorgados", atuacao, "conjunta", True, "conjunta", sm.expressoes))
                atuacao = "conjunta"
        exige = x.poderes.exige_conjunto_com
        if exige in ("diretor", "administrador") and not lx.CONJUNTO_COM.search(lx.norm(x.poderes.evidencia)) \
                and not lx.CONJUNTO_COM.search(lx.norm(texto)):  # só relaxa se a exigência não aparece em lugar nenhum
            # "representada conjuntamente por seus administradores" descreve quem OUTORGA, não limita o procurador
            verifs.append(Verificacao("exige_conjunto_com", exige, "nenhum", True, "nenhum", []))
            exige = "nenhum"
        veics = [v for v in (_veic(v) for v in x.poderes.veiculos) if v]
        abr = x.poderes.abrangencia
        if abr == "todos_veiculos_da_outorgante" and veics and "exclusivamente" in lx.norm(x.poderes.evidencia):
            verifs.append(Verificacao("abrangencia", abr, "veiculos_especificos", True, "veiculos_especificos", []))
            abr = "veiculos_especificos"
        adquirir = bool(lx.ADQUIRIR_PODER.search(lx.norm(x.poderes.evidencia)) or lx.ADQUIRIR_PODER.search(lx.norm(texto)))
        div = sum(1 for v in verifs if v.divergiu)
        confs = [self._conf(l, F["poderes"], div, "poderes"), self._conf(l, F["outorgante"], 0, "outorgante")]
        return Procuracao(l.doc.id, l.classificacao.titulo, x.forma, x.cartorio, x.livro, x.folhas, data, x.firma_reconhecida,
                          o.tipo, o.nome, o.documento, e_emp, [r for r in reps if r], o.age_em_nome_da_empresa,
                          [p for p in outorgados if p], atuacao, alienar, x.poderes.assinar_atpv, x.poderes.poderes_especiais_expressos,
                          apenas_gerais, abr, veics, x.poderes.bens_do_proprio_outorgante, exige,
                          x.validade.tipo, fim, x.validade.prazo_texto, sub, x.irrevogavel, x.em_causa_propria, F, verifs,
                          round(min(confs), 3), sorted(lx.alteracoes_citadas(texto)), adquirir)

    def _procuracoes_alcancadas(self, texto: str, outorgado_nome: str | None, data_rev: date | None, procs: list[Procuracao],
                                exceto: str | None, todas: bool | None = None) -> list[str]:
        """Revogação genérica: procurações anteriores alcançadas (por outorgado citado, por data citada ou 'todas')."""
        anteriores = [p for p in procs if p.id != exceto and (data_rev is None or p.data is None or p.data < data_rev)]
        t = lx.norm(texto)
        alvo = set()
        nomes = [outorgado_nome] if outorgado_nome else []
        for p in anteriores:
            for k in p.outorgados:
                pessoa = self.ids.pessoas.get(self.ids.chave(k))
                if pessoa and (lx.norm(pessoa.nome) in t or any(similaridade_nomes(n, pessoa.nome) >= 90 for n in nomes)):
                    alvo.add(p.id)
        datas = {lx.parse_data(m.group(0)) for m in re.finditer(r"\d{1,2}/\d{1,2}/\d{4}|\d{1,2}o? de [a-z]+ de \d{4}", t)}
        for p in anteriores:
            if p.data and p.data in datas:
                alvo.add(p.id)
        if not alvo and (todas if todas is not None else bool(lx._REVOGA_TODAS.search(t))):
            alvo = {p.id for p in anteriores}
        return sorted(alvo)

    def _casar_procuracao(self, ref: sc.RefProcuracao, procs: list[Procuracao], substabelecente: str | None = None) -> str | None:
        melhor, pontos = None, 0
        for p in procs:
            s = 0
            if ref.data and p.data and _d(ref.data) == p.data:
                s += 3
            if ref.livro and p.livro and so_digitos(ref.livro) and so_digitos(ref.livro) == so_digitos(p.livro):
                s += 2
            if ref.folhas and p.folhas and so_digitos(ref.folhas)[:3] == so_digitos(p.folhas)[:3]:
                s += 1
            if substabelecente and substabelecente in p.outorgados:
                s += 2
            if ref.outorgado_nome and any(similaridade_nomes(ref.outorgado_nome, self.ids.pessoas[k].nome) >= 90
                                          for k in p.outorgados if k in self.ids.pessoas):
                s += 2
            if s > pontos:
                melhor, pontos = p.id, s
        return melhor if pontos >= 3 else None

    # --------------------------------------------------------------------------- tudo
    def consolidar_pf(self, nome: str | None, cpf: str | None, origem: str) -> BaseConhecimento:
        """Lado pessoa física: só o próprio titular assina, ou quem tiver procuração DELE (CC, arts. 653 e 661).
        Vira um "titular único" com regra geral isolada, e o motor reaproveita toda a verificação de procurações."""
        dono = self.k(nome or "(titular não identificado)", cpf)  # antes dos documentos: o CPF vira a chave do titular
        kb = self.consolidar()
        dono = self.ids.chave(dono)
        bonito = kb.pessoas[dono].nome if dono in kb.pessoas else (nome or "(titular não identificado)")
        kb.empresa = Empresa(bonito, None, "PF", "", False, "PF")
        fonte = Fonte("TITULAR", origem, f"{nome or '—'} — CPF {cpf or '—'}", "titularidade", 100.0)
        inicio = date(1900, 1, 1)
        adm = Administrador(dono, "titular (pessoa física)", True, inicio, None, None, fonte)
        regra = RegraRep("TITULAR#R1", "geral", "autoriza", "isolado", [dono], None, None, [], None, None, None, False, None,
                         [], fonte, [], 1.0, {"alienar", "adquirir"}, 0)
        kb.atos = [AtoSocietario("TITULAR", "Titularidade (pessoa física)", "titularidade_pf", inicio, None, None, True, True,
                                 [adm], {dono: 100.0}, [regra], None, [])]
        kb.deliberacoes = []
        return kb

    def consolidar(self) -> BaseConhecimento:
        self._registrar_pessoas()
        emp = self._empresa()
        atos = []
        for l in self.leituras:
            if l.partes and l.classificacao.tipo in SOCIETARIOS | {"outro"}:
                atos.append(self._ato(l))
        socios_ref = {}
        for a in sorted(atos, key=lambda a: a.data_efeito or date.min):
            socios_ref = a.socios or socios_ref
        deliberacoes = []
        for l in self.leituras:
            if l.ata:
                ato, dls = self._ata(l, socios_ref)
                if ato:
                    atos.append(ato)
                deliberacoes += dls
        procs = [self._procuracao(l, emp) for l in self.leituras if l.procuracao]
        subs = []
        for l in self.leituras:
            if not l.substabelecimento:
                continue
            x = l.substabelecimento
            f = self.fonte(l, x.evidencia)
            ss = self.k(x.substabelecente.nome, x.substabelecente.cpf)
            reserva = x.reserva
            rl = lx.reserva_por_lexico(x.evidencia) or lx.reserva_por_lexico(l.doc.texto)
            verifs = []
            if rl and rl != reserva:
                verifs.append(Verificacao("reserva", reserva, rl, True, rl, []))
                reserva = rl
            data_s = _d(x.data) or _d(l.classificacao.data_documento)
            pid = self._casar_procuracao(x.procuracao_origem, procs, ss)
            origem_sub = None
            if pid is None:  # substabelecimento de substabelecimento: o substabelecente recebeu poderes de outro sub
                ant = [t for t in subs if ss in t.substabelecidos and (t.data is None or data_s is None or t.data <= data_s)]
                origem_sub = ant[-1].id if ant else None
            subs.append(Substabelecimento(l.doc.id, l.classificacao.titulo, x.forma, data_s,
                                          x.firma_reconhecida, x.procuracao_origem.model_dump(), pid, origem_sub, ss,
                                          [k for p in x.substabelecidos if (k := self.k(p.nome, p.cpf))], reserva,
                                          x.todos_os_poderes,
                                          x.alienar_veiculos, f, verifs, self._conf(l, f, len(verifs))))
        revs = []
        for l in self.leituras:
            if not l.revogacao:
                continue
            x = l.revogacao
            f = self.fonte(l, x.evidencia)
            data_r = _d(x.data) or _d(l.classificacao.data_documento)
            pid = self._casar_procuracao(x.procuracao_revogada, procs)
            generica = False
            if pid:
                ids = [pid]
            else:
                generica = True
                ids = self._procuracoes_alcancadas(x.evidencia + " " + l.doc.texto, x.procuracao_revogada.outorgado_nome,
                                                   data_r, procs, exceto=None)
            revs.append(Revogacao(l.doc.id, l.classificacao.titulo, x.forma, data_r, x.revogante.nome,
                                  [k for r in x.revogante.representantes if (k := self.k(r.nome, r.cpf))],
                                  x.procuracao_revogada.model_dump(), ids, f, generica, self._conf(l, f)))
        # revogações dentro de outros documentos ("revogando a procuração anterior", "ficam revogadas as procurações")
        for l in self.leituras:
            if l.revogacao or l.crlv or l.atpv:
                continue
            data_doc = _d(l.classificacao.data_documento)
            for sinal in lx.revogacoes_no_texto(l.doc.texto):
                ids = self._procuracoes_alcancadas(sinal.trecho, None, data_doc, procs, exceto=l.doc.id, todas=sinal.todas)
                f = self.fonte(l, sinal.trecho)
                revs.append(Revogacao(f"{l.doc.id}#rev", f"Revogação em {l.classificacao.titulo}", "embutida", data_doc,
                                      emp.razao_social, [], {"trecho": sinal.trecho}, ids, f, True, self._conf(l, f)))
        crlv = None
        for l in self.leituras:
            if l.crlv:
                c = l.crlv
                crlv = CRLV(c.placa, c.renavam, c.chassi, c.marca_modelo, c.proprietario_nome, c.proprietario_documento,
                            self.fonte(l, c.placa))
        docs = {l.doc.id: DocumentoInfo(l.doc.id, l.classificacao.titulo, l.classificacao.tipo, l.doc.arquivo,
                                        len(l.doc.paginas), l.doc.metodo in ("ocr", "misto"), l.doc.ocr_confianca,
                                        _d(l.classificacao.data_documento)) for l in self.leituras}
        pessoas = {k: p for k, p in self.ids.pessoas.items()}
        # remapeia chaves promovidas (nome → CPF) nos fatos já criados
        def rk(x):
            return self.ids.chave(x)
        for a in atos:
            for adm in a.administradores:
                adm.pessoa = rk(adm.pessoa)
            a.socios = {rk(k): v for k, v in a.socios.items()}
            for r in a.regras:
                r.pessoas = [rk(p) for p in r.pessoas]
                r.exige_anuencia_de = [rk(p) for p in r.exige_anuencia_de]
            for b in a.bens:
                b.socio = rk(b.socio)
        for p in procs:
            p.representantes = [rk(x) for x in p.representantes]
            p.outorgados = [rk(x) for x in p.outorgados]
        for s in subs:
            s.substabelecente = rk(s.substabelecente)
            s.substabelecidos = [rk(x) for x in s.substabelecidos]
        return BaseConhecimento(emp, pessoas, atos, procs, subs, revs, deliberacoes, crlv, docs, self.ids.avisos + self.avisos)
