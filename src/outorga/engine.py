"""Motor de regras: quem pode assinar o ATPV deste veículo, nesta data?

Entrada: a base de conhecimento (fatos já extraídos e conferidos) e o pedido de venda.
Saída: as combinações mínimas de assinantes que obrigam a empresa, o veredito sobre os assinantes
informados, e uma trilha de verificações com fundamento legal e fonte de cada fato.

Princípios codificados (ver docs/REGRAS.md):
- regime vigente na data da venda (alterações posteriores substituem as anteriores; Lei 8.934/94, art. 36);
- especialidade: cláusula do veículo específico > veículos > bens móveis/ativo > regra geral;
- restrição sobre IMÓVEIS não alcança veículo (bem móvel);
- alçada por valor só vale se o valor do veículo cruzar o limite (sem valor => indeterminado);
- procuração precisa de poderes expressos para alienar (CC 661, §1º), ser outorgada pela PJ por
  quem tinha poder para o ato (ninguém delega mais do que tem), estar no prazo e não revogada;
- substabelecimento: vedado => não obriga (CC 667, §3º); sem reserva => o substabelecente perde poderes;
- mandato outorgado pela PJ não se extingue com a troca do administrador (CC 682).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from . import lexicon as lx
from .domain import (
    ORDEM_SEV, AtoSocietario, BaseConhecimento, Faixa, Fonte, Grupo, Pedido, Procuracao,
    RegraRep, RegrasProcuracaoEmpresa, Severidade, Substabelecimento, VeiculoId, Veredito, fator_ancoragem,
)
from .ids import normalizar_chassi, placas_equivalentes, similaridade_nomes, so_digitos


# ------------------------------------------------------------------------------------ política
@dataclass
class Politica:
    """Parâmetros de risco configuráveis por órgão/UF (ver docs/REGRAS.md).

    Padrão = perfil DETRAN-CE: o DETRAN-CE aceita procurador "por instrumento de procuração pública e específica para
    o ato (com validade de até 01 ano da data de expedição)" (página do serviço no gov.br). O perfil "generica" aplica
    só o Código Civil (procuração particular é válida; idade só gera alerta).
    """
    nome: str = "DETRAN-CE"
    uf: str | None = "CE"
    idade_max_procuracao_dias: int = 365
    idade_max_severidade: Severidade = Severidade.BLOQUEIO
    procuracao_particular_com_firma: Severidade = Severidade.BLOQUEIO
    procuracao_particular_sem_firma: Severidade = Severidade.BLOQUEIO
    substabelecimento_particular: Severidade = Severidade.ALERTA
    procuracao_sem_veiculo_identificado: Severidade = Severidade.ATENCAO
    crlv_ausente: Severidade = Severidade.ATENCAO
    compra_com_poderes_gerais: Severidade = Severidade.BLOQUEIO  # DETRAN-CE: procuração "específica para o ato"
    cnd_inss: Severidade = Severidade.INFO          # Lei 8.212/91, art. 47, I, "c" (exigida por MG/RJ/PR)
    limite_cnd_inss: float = 87493.73               # valor de 2026 citado pelo DETRAN-MG
    quorum_padrao_deliberacao: float = 50.01
    limiar_aceite: float = 85.0   # índice >= limiar_aceite => VERDE
    limiar_recusa: float = 15.0   # índice <= limiar_recusa => VERMELHO

    @classmethod
    def detran_ce(cls) -> "Politica":
        return cls()

    @classmethod
    def generica(cls) -> "Politica":
        return cls(nome="Código Civil (genérica)", uf=None, idade_max_severidade=Severidade.ALERTA,
                   procuracao_particular_com_firma=Severidade.ATENCAO, procuracao_particular_sem_firma=Severidade.ALERTA,
                   substabelecimento_particular=Severidade.ATENCAO, procuracao_sem_veiculo_identificado=Severidade.INFO,
                   compra_com_poderes_gerais=Severidade.ALERTA)

    @classmethod
    def por_nome(cls, nome: str | None) -> "Politica":
        n = (nome or "ce").lower()
        if n in ("ce", "detran-ce", "detran_ce"):
            return cls.detran_ce()
        if n in ("generica", "genérica", "cc", "civil"):
            return cls.generica()
        raise ValueError(f"política desconhecida: {nome}")


SO_ALERTA = {"ESTOQUE_OU_IMOBILIZADO", "REGRA_COM_ADMINISTRADOR_QUE_SAIU", "COMBINACAO_POR_CLASSES",
             "REPRESENTACAO_POR_SUBSTITUTO"}
INCERTEZA_CAMINHO = {"PODERES_DO_OUTORGANTE_INCERTOS", "PODERES_DO_OUTORGANTE_NAO_VERIFICADOS"}  # pendências que pedem revisão, mas não tornam o caso indeterminado
NIVEL = {"geral": 0, "alienacao_bens": 1, "alienacao_bens_moveis": 2, "alienacao_ativo_imobilizado": 2,
         "alienacao_veiculos": 3, "veiculo_especifico": 4}
# atos que trazem o texto inteiro do contrato/estatuto (os anteriores deixam de valer)
ATOS_COMPLETOS = ("constituicao", "alteracao_e_consolidacao", "estatuto", "ato_constitutivo_slu", "requerimento_empresario")
NAO_APLICAVEL = {
    "alienacao_bens_imoveis": "trata de bens imóveis; veículo é bem móvel",
    "onerar_bens": "trata de oneração/gravame, não de venda",
    "outorgar_procuracoes": "regula a outorga de procurações (usada para validar procurações)",
    "obrigacoes_garantias": "trata de avais, fianças e garantias",
    "outro": "não trata de alienação de veículo",
}
ROTULO_ESCOPO = {
    "geral": "regra geral de representação", "alienacao_bens": "alienação de bens",
    "alienacao_bens_moveis": "alienação de bens móveis", "alienacao_ativo_imobilizado": "alienação de ativo imobilizado/não circulante",
    "alienacao_veiculos": "alienação de veículos", "veiculo_especifico": "cláusula do veículo específico",
    "alienacao_bens_imoveis": "bens imóveis", "onerar_bens": "oneração de bens", "outorgar_procuracoes": "outorga de procurações",
    "obrigacoes_garantias": "avais e garantias", "outro": "outro",
}


# ------------------------------------------------------------------------------- estruturas
@dataclass
class Achado:
    codigo: str
    severidade: Severidade
    titulo: str
    detalhe: str
    fundamento: list[str] = field(default_factory=list)
    fontes: list[Fonte] = field(default_factory=list)
    caminho: str | None = None  # None = global


@dataclass
class Precondicao:
    codigo: str
    descricao: str
    quorum: float | None = None
    satisfeita: bool | None = None
    detalhe: str = ""
    fontes: list[Fonte] = field(default_factory=list)
    pessoas: frozenset[str] = frozenset()  # só se aplica a caminhos com estas pessoas (ex.: substitutos)


@dataclass
class Alternativa:
    id: str
    pessoas: frozenset[str]
    via: str                    # contrato | procuracao | substabelecimento
    descricao: str
    cadeia: list[str]           # ids dos documentos que sustentam o caminho
    regras: list[str] = field(default_factory=list)
    achados: list[Achado] = field(default_factory=list)
    precondicoes: list[Precondicao] = field(default_factory=list)
    confianca: float = 1.0

    @property
    def severidade(self) -> Severidade:
        sevs = [a.severidade for a in self.achados if a.severidade != Severidade.BLOQUEIO]
        return max(sevs, key=lambda s: ORDEM_SEV[s]) if sevs else Severidade.OK


@dataclass
class Regime:
    data: date
    atos: list[AtoSocietario]
    administradores: list[Any]
    encerrados: list[tuple[Any, str]]
    socios: dict[str, float]
    regras: list[RegraRep]
    regras_procuracao: RegrasProcuracaoEmpresa | None
    bens: list[Any]
    prorrogados: list[tuple[Any, str]] = field(default_factory=list)


@dataclass
class Formula:
    alternativas: list[frozenset[str]]
    regras: list[RegraRep]
    precondicoes: list[Precondicao]
    avaliacao: list[dict]           # cada regra: aplicável? por quê?
    omissa: bool = False
    valor_indeterminado: bool = False
    nivel: int | None = None
    anuencias: set[str] = field(default_factory=set)


@dataclass
class Resultado:
    veredito: Veredito
    resumo: str
    alternativas: list[Alternativa]
    bloqueadas: list[Alternativa]
    satisfeitas: list[Alternativa]
    escolhida: Alternativa | None
    assinantes: list[dict]
    faltantes: list[dict]
    achados: list[Achado]
    formula: Formula
    regime: Regime
    fatos_decisivos: list[dict]
    grafo: dict
    linha_do_tempo: list[dict]
    indeterminacoes: list[str]


# ----------------------------------------------------------------------------------- utilidades
def minimizar(conjuntos: list[frozenset[str]]) -> list[frozenset[str]]:
    unicos = sorted(set(c for c in conjuntos if c), key=lambda c: (len(c), sorted(c)))
    out: list[frozenset[str]] = []
    for c in unicos:
        if not any(o <= c for o in out):
            out.append(c)
    return out


def veiculo_confere(ref: VeiculoId | None, alvo: VeiculoId) -> bool | None:
    """True se algum identificador forte bate; False se diverge; None se não há como comparar."""
    if ref is None:
        return None
    comparou = False
    if ref.placa and alvo.placa:
        comparou = True
        if placas_equivalentes(ref.placa, alvo.placa):
            return True
    if ref.renavam and alvo.renavam:
        comparou = True
        if so_digitos(ref.renavam).lstrip("0") == so_digitos(alvo.renavam).lstrip("0"):
            return True
    if ref.chassi and alvo.chassi:
        comparou = True
        if normalizar_chassi(ref.chassi) == normalizar_chassi(alvo.chassi):
            return True
    return False if comparou else None


def _fmt_data(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if d else "data não identificada"


def _fmt_valor(v: float | None) -> str:
    if v is None:
        return "valor não informado"
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------------------- motor
class Motor:
    def __init__(self, kb: BaseConhecimento, politica: Politica | None = None):
        self.kb = kb
        self.pol = politica or Politica()
        self._designados = {a.pessoa for ato in kb.atos for a in ato.administradores}
        self._lado = "vendedor"

    def nome(self, chave: str) -> str:
        if not chave:
            return "(sem nome)"
        if chave.startswith("?"):  # assinante que não aparece nos documentos: o nome (ou CPF) como informado
            n = chave[1:]
            return f"o {n}" if n.startswith("CPF ") else n
        return self.kb.nome(chave)

    def nomes(self, chaves) -> str:
        lst = [self.nome(c) for c in sorted(chaves, key=self.nome)]
        return lst[0] if len(lst) == 1 else ", ".join(lst[:-1]) + " e " + lst[-1] if lst else "ninguém"

    # ------------------------------------------------------------------------------- regime
    def regime_em(self, data: date) -> Regime:
        atos = sorted([a for a in self.kb.atos if a.data_efeito and a.data_efeito <= data],
                      key=lambda a: (a.data_efeito, a.data_registro or a.data_efeito))
        admins: list = []
        socios: dict[str, float] = {}
        regras: list[RegraRep] = []
        rp: RegrasProcuracaoEmpresa | None = None
        bens: list = []
        for a in atos:
            completo = a.consolida or a.tipo in ATOS_COMPLETOS
            if a.eleicao:
                if a.administradores:
                    admins = list(a.administradores)
                continue
            if completo:
                if a.administradores or a.tipo != "estatuto":
                    admins = list(a.administradores)
                regras = list(a.regras)
                rp = a.regras_procuracao or rp
            else:
                if a.altera_administracao:
                    antigos = {x.pessoa for x in admins}
                    if a.administradores:
                        admins = list(a.administradores)
                    if a.regras:
                        novos_esc = {r.escopo for r in a.regras}
                        novas_cl = {lx.norm(r.fonte.clausula) for r in a.regras if r.fonte.clausula}

                        def substituida(r: RegraRep) -> bool:
                            return (r.fonte.clausula and lx.norm(r.fonte.clausula) in novas_cl) or r.escopo in novos_esc \
                                or r.escopo == "geral"

                        saiu = antigos - {x.pessoa for x in admins}
                        regras = [r for r in regras if not substituida(r) and not (
                            saiu & set(r.pessoas) and r.escopo != "veiculo_especifico")] + list(a.regras)
                    elif a.administradores:
                        # nova administração sem regra nova: regra geral antiga passa a valer para os novos administradores
                        saiu = antigos - {x.pessoa for x in admins}
                        regras = [self._retarget(r, saiu) for r in regras]
                elif a.regras:
                    novos_esc = {r.escopo for r in a.regras}
                    regras = [r for r in regras if r.escopo not in novos_esc] + list(a.regras)
                if a.regras_procuracao:
                    rp = a.regras_procuracao
            if a.socios:
                socios = dict(a.socios)
            bens += a.bens
        ativos, encerrados, prorrogados = [], [], []
        for adm in admins:
            fim = adm.termino or self._termino_mandato(adm, atos)
            if fim and fim < data:
                if self.kb.empresa.tipo == "SA":  # LSA, art. 150, §4º: gestão se estende até a posse dos sucessores
                    ativos.append(adm)
                    prorrogados.append((adm, f"prazo de gestão terminou em {_fmt_data(fim)}"))
                else:
                    encerrados.append((adm, f"mandato encerrado em {_fmt_data(fim)}"))
            else:
                ativos.append(adm)
        return Regime(data, atos, ativos, encerrados, socios, regras, rp, bens, prorrogados)

    def lacuna_em(self, data: date) -> tuple[int, int] | None:
        """Faltam alterações (pela numeração) entre o último ato conhecido até `data` e o primeiro ato posterior?
        Devolve (último número conhecido, próximo número conhecido) quando há buraco que pode cair antes de `data`."""
        numerados = []
        for a in self.kb.atos:
            n = 0 if a.tipo == "constituicao" and a.numero_alteracao is None else a.numero_alteracao
            if n is not None and a.data_efeito:
                numerados.append((a.data_efeito, n))
        if not numerados:
            return None
        antes = [n for d, n in numerados if d <= data]
        depois = [n for d, n in numerados if d > data]
        if not antes or not depois:
            return None
        p, q = max(antes), min(depois)
        return (p, q) if q - p > 1 else None

    @staticmethod
    def _retarget(r: RegraRep, saiu: set[str]) -> RegraRep:
        if r.escopo != "veiculo_especifico" and saiu & set(r.pessoas):
            from dataclasses import replace
            return replace(r, pessoas=[], cargo="administradores")
        return r

    @staticmethod
    def _termino_mandato(adm, atos: list[AtoSocietario]) -> date | None:
        desc = adm.prazo_descricao
        if not desc or "indetermin" in lx.norm(desc):
            return None
        ato = next((a for a in atos if adm in a.administradores), None)
        base = adm.inicio
        if ato:
            base = ato.data_registro if "registro" in lx.norm(desc) and ato.data_registro else (ato.data_assinatura or base)
        return lx.somar_prazo(base, desc) if base else None

    # ----------------------------------------------------------------------------- fórmula
    def membros(self, cargo: str | None, regime: Regime) -> list[str]:
        if cargo == "socios":
            return list(regime.socios)
        if cargo == "diretores":
            dirs = [a.pessoa for a in regime.administradores if "diretor" in lx.norm(a.cargo)]
            return dirs or [a.pessoa for a in regime.administradores]
        if cargo == "procuradores":
            return []  # procuradores entram pelas próprias procurações
        return [a.pessoa for a in regime.administradores]

    def _resolver(self, pessoas: list[str], regime: Regime) -> list[str]:
        """Troca cargos nomeados ("@cargo:Presidente") por quem ocupa o cargo na data; mantém as demais chaves."""
        out = []
        for p in pessoas:
            if p.startswith("@cargo:"):
                cargo = p.split(":", 1)[1]
                out += [a.pessoa for a in regime.administradores if lx.cargo_casa(cargo, a.cargo)]
            else:
                out.append(p)
        return list(dict.fromkeys(out))

    def _grupo_regra(self, r: RegraRep, regime: Regime) -> list[str]:
        if r.pessoas:
            ativos = {a.pessoa for a in regime.administradores}
            pessoas = self._resolver(r.pessoas, regime)
            if r.escopo == "veiculo_especifico":
                return pessoas
            # quem foi designado administrador e saiu (prazo vencido, renúncia) não conta mais
            return [p for p in pessoas if p in ativos or p not in self._designados]
        return self.membros(r.cargo, regime)

    def alternativas_regra(self, r: RegraRep, regime: Regime) -> list[frozenset[str]]:
        grupo = self._grupo_regra(r, regime)
        if r.modo == "misto" and r.combinacoes:
            alts: list[frozenset[str]] = []
            for comb in r.combinacoes:
                partes = []
                for g in comb:
                    if g.cargo == "procuradores":
                        partes = None
                        break
                    membros = self._resolver(g.pessoas, regime) if g.pessoas else self.membros(g.cargo, regime)
                    partes.append([frozenset(c) for c in itertools.combinations(sorted(set(membros)), max(1, g.quantidade))])
                if not partes:
                    continue
                for prod in itertools.product(*partes):
                    s = frozenset().union(*prod)
                    if len(s) == sum(len(x) for x in prod):
                        alts.append(s)
            base = alts
        elif r.modo == "conjunto" and r.quantidade_minima and len(set(grupo)) > r.quantidade_minima:
            base = [frozenset(c) for c in itertools.combinations(sorted(set(grupo)), r.quantidade_minima)]
        elif r.modo == "conjunto":
            base = [frozenset(grupo)] if grupo else []
        elif r.modo == "quantidade_minima":
            k = r.quantidade_minima or 2
            base = [frozenset(c) for c in itertools.combinations(sorted(set(grupo)), k)] if len(grupo) >= k else []
        else:  # isolado ou não especificado (supletivo: cada um separadamente — CC 1.013)
            base = [frozenset([p]) for p in grupo]
        if r.exige_anuencia_de:
            base = [b | frozenset(r.exige_anuencia_de) for b in base] or [frozenset(r.exige_anuencia_de)]
        return minimizar(base)

    ESCOPOS_ALIENACAO = {"alienacao_bens", "alienacao_bens_moveis", "alienacao_veiculos", "alienacao_ativo_imobilizado",
                         "veiculo_especifico"}

    @staticmethod
    def _exclusao(r: RegraRep) -> bool:
        """'Veda' que TIRA poderes de pessoas (ex.: "sócios quotistas, não lhes cabendo poderes de administração").
        Diferente de "vedada a prática isolada" (restrição de modo: exige assinatura conjunta)."""
        return (r.efeito == "veda" and bool(r.pessoas) and r.modo == "nao_especificado"
                and bool(lx.NEGA_PODERES.search(lx.norm(r.fonte.trecho))))

    def _proibe_ato(self, r: RegraRep) -> bool:
        """Proibição do próprio ato de alienar (rara): exige deliberação unânime/alteração contratual."""
        return r.efeito == "veda" and not r.pessoas and r.escopo in self.ESCOPOS_ALIENACAO and lx.escopo_por_lexico(
            r.fonte.trecho).alienacao

    @staticmethod
    def _so_condicao(r: RegraRep) -> bool:
        """Regra que só impõe condição (aprovação de sócios/anuência), sem dizer quem assina."""
        if r.efeito == "veda":
            # "vedada a prática isolada" com pessoas/cargo e modo definido = regra de assinatura (conjunta)
            return not ((r.pessoas or r.cargo) and r.modo in ("conjunto", "quantidade_minima", "misto"))
        if r.exige_aprovacao_socios and (r.cargo == "socios" or not r.pessoas) and r.modo in ("conjunto", "nao_especificado", "quantidade_minima"):
            return True
        return not r.define_assinantes

    def _rotulo_regra(self, r: RegraRep, veic: VeiculoId | None = None) -> str:
        """Nome da cláusula para o parecer; no lado comprador, pelo ato de adquirir ('aquisição de veículos')."""
        if self.kb.empresa.tipo == "PF":
            return "assinatura do próprio " + ("proprietário" if self._lado == "vendedor" else "comprador") + " (pessoa física)"
        if self._lado == "comprador" and r.escopo != "geral" and "adquirir" in r.atos:
            base = {1: "bens e obrigações", 2: "bens móveis ou do ativo", 3: "veículos"}.get(r.nivel_aquisicao or 0)
            if base:
                return ("compra e venda de " if "alienar" in r.atos else "aquisição de ") + base
            return "regra geral de representação"
        especifico = r.veiculo and (veiculo_confere(r.veiculo, veic) if veic else (r.veiculo.placa or r.veiculo.renavam))
        return ROTULO_ESCOPO.get("veiculo_especifico" if especifico else r.escopo, r.escopo)

    def aplicabilidade(self, r: RegraRep, veic: VeiculoId, valor: float | None, ato: str = "alienar") -> tuple[bool | None, str]:
        if ato == "adquirir":
            if r.valor_acima_de is not None or r.valor_ate is not None:
                if valor is None:
                    return None, "a regra depende do valor da compra, que não foi informado"
                ok = (r.valor_acima_de is None or valor > r.valor_acima_de) and (r.valor_ate is None or valor <= r.valor_ate)
                lim = r.valor_acima_de if r.valor_acima_de is not None else r.valor_ate
                return ok, f"valor {_fmt_valor(valor)} {'cruza' if ok else 'não cruza'} o limite de {_fmt_valor(lim)}"
            return True, {0: "regra geral de representação", 1: "aquisição de bens / assunção de obrigações",
                          2: "aquisição de bens móveis ou do ativo", 3: "aquisição de veículos"}.get(r.nivel_aquisicao or 0, "aquisição")
        esc = r.escopo
        if r.veiculo and (r.veiculo.placa or r.veiculo.renavam or r.veiculo.chassi):
            ok = veiculo_confere(r.veiculo, veic)
            if ok is False:
                return False, "cláusula de outro veículo específico"
            if ok:
                esc = "veiculo_especifico"
        elif esc == "veiculo_especifico":
            return False, "cláusula de veículo específico sem identificação conferível"
        if esc in NAO_APLICAVEL:
            return False, NAO_APLICAVEL[esc]
        if esc == "alienacao_ativo_imobilizado" and self.kb.empresa.comercializa_veiculos:
            return None, "a empresa revende veículos: se o carro for estoque (mercadoria), a restrição ao imobilizado não se aplica"
        if r.valor_acima_de is not None or r.valor_ate is not None:
            if valor is None:
                return None, "a regra depende do valor do veículo, que não foi informado"
            ok = True
            if r.valor_acima_de is not None:
                ok &= valor > r.valor_acima_de
            if r.valor_ate is not None:
                ok &= valor <= r.valor_ate
            lim = r.valor_acima_de if r.valor_acima_de is not None else r.valor_ate
            return ok, f"valor {_fmt_valor(valor)} {'cruza' if ok else 'não cruza'} o limite de {_fmt_valor(lim)}"
        return True, ROTULO_ESCOPO.get(esc, esc)

    def formula(self, regime: Regime, veic: VeiculoId, valor: float | None, forcar_valor: str | None = None,
                ato: str = "alienar") -> Formula:
        """Combinações mínimas para alienar (vendedor) ou adquirir (comprador) `veic` sob `regime`.
        `forcar_valor` = 'acima'|'abaixo' explora os ramos quando a alçada depende de valor não informado."""
        avaliacao, assinantes_rules, precs = [], [], []
        excluidos: set[str] = set()
        anuencias: set[str] = set()
        indeterminado = False
        for r in regime.regras:
            if self._exclusao(r):  # "não lhes cabendo poderes" vale para comprar e para vender
                excluidos.update(self._resolver(r.pessoas, regime))
                continue
            if ato not in r.atos:
                avaliacao.append({"regra": r.id, "escopo": r.escopo, "aplicavel": False,
                                  "motivo": "regra de compra (não se aplica à venda)" if ato == "alienar" else
                                  "regra de venda/alienação (não se aplica à compra)",
                                  "so_condicao": self._so_condicao(r), "fonte": r.fonte})
                continue
            apl, motivo = self.aplicabilidade(r, veic, valor, ato)
            if apl is None and forcar_valor and (r.valor_acima_de is not None or r.valor_ate is not None):
                apl = forcar_valor == "acima" if r.valor_acima_de is not None else forcar_valor == "abaixo"
                motivo += f" (hipótese: valor {forcar_valor} do limite)"
            esc_ef = "veiculo_especifico" if (r.veiculo and veiculo_confere(r.veiculo, veic)) else r.escopo
            avaliacao.append({"regra": r.id, "escopo": esc_ef, "aplicavel": apl, "motivo": motivo,
                              "so_condicao": self._so_condicao(r), "fonte": r.fonte})
            if apl is None:
                if r.valor_acima_de is not None or r.valor_ate is not None:
                    indeterminado = True
                elif esc_ef == "alienacao_ativo_imobilizado":
                    precs.append(Precondicao("ESTOQUE_OU_IMOBILIZADO",
                                             "Confirmar se o veículo é estoque (mercadoria) ou ativo imobilizado", None, None,
                                             motivo, [r.fonte]))
                continue
            if not apl:
                continue
            anuencias.update(self._resolver(r.exige_anuencia_de, regime))
            if r.efeito == "veda" and not self._proibe_ato(r):
                continue
            if r.exige_aprovacao_socios or r.efeito == "veda":
                q = r.quorum_percentual or (100.0 if r.efeito == "veda" else self.pol.quorum_padrao_deliberacao)
                precs.append(Precondicao("DELIBERACAO_SOCIOS",
                                         f"Aprovação prévia de sócios com {('mais da metade' if abs(q - 50.01) < 0.01 else f'{q:g}%')} do capital",
                                         q, None, "", [r.fonte]))
            if not self._so_condicao(r):
                assinantes_rules.append(r)
        if assinantes_rules:
            def nivel_de(r):
                if ato == "adquirir":
                    return r.nivel_aquisicao or 0
                return NIVEL.get("veiculo_especifico" if (r.veiculo and veiculo_confere(r.veiculo, veic)) else r.escopo, 0)

            niveis = sorted({nivel_de(r) for r in assinantes_rules}, reverse=True)
            alts: list[frozenset[str]] | None = None
            topo: list[RegraRep] = []
            for nivel in niveis:
                topo = [r for r in assinantes_rules if nivel_de(r) == nivel]
                alts = None
                for r in topo:
                    ar = self.alternativas_regra(r, regime)
                    alts = ar if alts is None else minimizar([a | b for a in alts for b in ar])
                vazia_por_saida = not alts and all(r.pessoas and set(r.pessoas) <= self._designados for r in topo)
                if alts or not vazia_por_saida:
                    break
                precs.append(Precondicao("REGRA_COM_ADMINISTRADOR_QUE_SAIU", "Cláusula cita administrador que não está mais "
                                         "no cargo", None, None, "A regra mais específica só cita quem deixou a administração; "
                                         "aplicada a regra seguinte.", [r.fonte for r in topo]))
            omissa = all(r.modo == "nao_especificado" for r in topo) and len(self._grupo_regra(topo[0], regime)) > 1
            classes = [r for r in topo if lx.menciona_classes(r.fonte.trecho) and not (
                r.modo == "misto" and r.combinacoes and all(g.pessoas for comb in r.combinacoes for g in comb))]
            substitutos = frozenset(p for r in topo for c in r.substitutos for p in self._resolver([f"@cargo:{c}"], regime))
            if substitutos:
                precs.append(Precondicao("REPRESENTACAO_POR_SUBSTITUTO", "Assinatura por substituto (ausência ou impedimento "
                                         "do titular)", None, None, "A cláusula só deixa o substituto representar na ausência "
                                         "ou no impedimento do titular, o que os documentos não comprovam: confira.",
                                         [r.fonte for r in topo if r.substitutos], substitutos))
            if classes:
                precs.append(Precondicao("COMBINACAO_POR_CLASSES", "Assinatura exige combinação entre classes/grupos",
                                         None, None, "A cláusula combina administradores de classes ou grupos diferentes "
                                         "(ex.: 'um Administrador A e um Administrador B'); confira se os assinantes "
                                         "pertencem às classes exigidas.", [r.fonte for r in classes]))
            # anuência exigida por qualquer regra aplicável (de assinatura ou só de condição) vale para todos os caminhos
            if anuencias:
                alts = minimizar([a | frozenset(anuencias) for a in (alts or [])])
            if excluidos:
                alts = [a for a in (alts or []) if not (a & excluidos)]
            return Formula(alts or [], topo, precs, avaliacao, omissa, indeterminado, nivel, anuencias)
        # contrato não diz quem assina para este ato: regra supletiva (CC 1.013 / 1.060)
        if self.kb.empresa.tipo == "EI":
            titular = list(regime.socios) or [a.pessoa for a in regime.administradores]
            alts = minimizar([frozenset([t]) | frozenset(anuencias) for t in titular])
            return Formula(alts, [], precs, avaliacao, False, indeterminado, None, anuencias)
        admins = [a.pessoa for a in regime.administradores]
        grupo = [p for p in (admins or (list(regime.socios) if not self._designados else [])) if p not in excluidos]
        alts = minimizar([frozenset([p]) | frozenset(anuencias) for p in grupo])
        return Formula(alts, [], precs, avaliacao, len(grupo) > 1, indeterminado, None, anuencias)

    # ------------------------------------------------------------------------- procurações
    def _outorgados_todos(self) -> set[str]:
        """Quem recebeu poderes em alguma procuração ou substabelecimento apresentado."""
        return ({k for p in self.kb.procuracoes for k in p.outorgados}
                | {k for s in self.kb.substabelecimentos for k in s.substabelecidos})

    def _revogacao_de(self, p: Procuracao):
        return [r for r in self.kb.revogacoes if p.id in r.procuracao_ids]

    def _fim_procuracao(self, p: Procuracao) -> date | None:
        if p.validade_fim:
            return p.validade_fim
        if p.validade_tipo == "prazo" and p.data and p.prazo_texto:
            return lx.somar_prazo(p.data, p.prazo_texto)
        return None

    def avaliar_procuracao(self, p: Procuracao, pedido: Pedido, regime_venda: Regime,
                           removidos: dict[str, tuple[date, str]]) -> tuple[list[Alternativa], list[Alternativa], list[Achado]]:
        D, veic = pedido.data_venda, pedido.veiculo
        cam = p.id
        ach: list[Achado] = []
        F = p.fontes

        def add(cod, sev, tit, det, fund=(), fontes=()):
            ach.append(Achado(cod, sev, tit, det, list(fund), [f for f in fontes if f], cam))

        if p.data and p.data > D:
            return [], [], []
        representantes = list(p.representantes)
        # (a) quem outorgou
        if self.kb.empresa.tipo == "PF":
            titular = self.kb.atos[0].administradores[0].pessoa if self.kb.atos else None
            papel = "o proprietário do veículo" if self._lado == "vendedor" else "o comprador"
            if p.outorgante_tipo == "PF" and titular and (titular in representantes or (
                    p.outorgante_doc and so_digitos(p.outorgante_doc) == so_digitos(self.kb.pessoas[titular].cpf or "x"))):
                add("OUTORGANTE_TITULAR", Severidade.OK, f"Outorgada por {papel}",
                    f"A outorgante é {self.nome(titular)}, {papel} (pessoa física).", ["CC art. 653"], [F.get("outorgante")])
            else:
                add("OUTORGANTE_NAO_E_O_TITULAR", Severidade.BLOQUEIO, f"Procuração de quem não é {papel}",
                    f"A procuração foi outorgada por {p.outorgante_nome}, não por {self.nome(titular) if titular else papel}. "
                    "Só o próprio titular pode constituir procurador para esse ato.", ["CC art. 653"], [F.get("outorgante")])
        elif p.outorgante_tipo == "PJ":
            if not p.outorgante_e_empresa:
                add("OUTORGANTE_OUTRA_EMPRESA", Severidade.BLOQUEIO, "Procuração de outra empresa",
                    f"A outorgante é {p.outorgante_nome}, não a proprietária do veículo.", [], [F.get("outorgante")])
            else:
                add("OUTORGANTE_PJ", Severidade.OK, "Outorgada pela própria empresa",
                    f"A outorgante é a empresa, representada por {self.nomes(representantes) if representantes else 'representante não identificado'}.",
                    ["CC art. 1.018"], [F.get("outorgante")])
        else:
            titular_ei = self.kb.empresa.tipo == "EI" and representantes == [] and p.outorgados
            pf_chave = representantes[0] if representantes else None
            if self.kb.empresa.tipo == "EI" and (pf_chave in regime_venda.socios or titular_ei):
                add("OUTORGANTE_TITULAR_EI", Severidade.OK, "Outorgada pelo titular do empresário individual",
                    "No empresário individual, o titular e a empresa são o mesmo sujeito.", ["CC art. 966"], [F.get("outorgante")])
            elif p.age_em_nome_da_empresa:
                add("OUTORGANTE_PF_EM_NOME_DA_EMPRESA", Severidade.ALERTA, "Pessoa física dizendo agir pela empresa",
                    f"{p.outorgante_nome} outorgou em nome próprio, mas declara agir pela empresa. O correto é a procuração "
                    "ser outorgada pela sociedade, representada por seu administrador.", ["CC art. 1.018"], [F.get("outorgante")])
            else:
                add("OUTORGANTE_PF", Severidade.BLOQUEIO, "Procuração da pessoa física, não da empresa",
                    f"{p.outorgante_nome} outorgou como pessoa física"
                    + (", para bens 'de propriedade do outorgante'" if p.bens_do_proprio_outorgante else "")
                    + ". O veículo é da empresa: só a sociedade, representada por quem tem poder, pode constituir "
                      "procurador para vendê-lo.", ["CC art. 1.018", "CC art. 47"], [F.get("outorgante"), F.get("poderes")])
        # (b) poder de quem outorgou, na data da outorga
        if p.data is None:
            add("DATA_OUTORGA_DESCONHECIDA", Severidade.ALERTA, "Data da outorga não identificada",
                "Sem a data não é possível conferir se quem outorgou tinha poder naquele momento.", [], [F.get("outorgante")])
        elif p.outorgante_tipo == "PJ" and p.outorgante_e_empresa or p.age_em_nome_da_empresa:
            reg_g = self.regime_em(p.data)
            f_g = self.formula(reg_g, veic, pedido.valor, ato=("adquirir" if pedido.lado == "comprador" else "alienar"))
            grantors = frozenset(representantes)
            lacuna = self.lacuna_em(p.data)
            citadas = set(p.alteracoes_citadas) | lx.alteracoes_citadas(F["outorgante"].trecho if F.get("outorgante") else "")
            conhecidas = {a.numero_alteracao for a in self.kb.atos if a.numero_alteracao}
            ausentes_citadas = {n for n in citadas if n not in conhecidas and not any(
                a.consolida and (a.numero_alteracao or 0) >= n for a in reg_g.atos)}
            incerto = bool(lacuna or ausentes_citadas)
            if f_g.alternativas and not any(a <= grantors for a in f_g.alternativas) and incerto:
                faltam = (f"alterações nº {lacuna[0] + 1} a {lacuna[1] - 1}" if lacuna else
                          "alteração nº " + ", ".join(map(str, sorted(ausentes_citadas))))
                add("PODERES_DO_OUTORGANTE_INCERTOS", Severidade.ALERTA, "Poder de quem outorgou depende de documento ausente",
                    f"Pelos atos apresentados, {self.nomes(grantors) if grantors else 'quem assinou'} não tinha poder em "
                    f"{_fmt_data(p.data)}, mas faltam {faltam}, que podem ter mudado a administração antes da outorga. "
                    "Apresente as alterações ou a certidão de inteiro teor da Junta.", ["CC art. 1.018"],
                    [F.get("outorgante")])
            elif f_g.alternativas and not any(a <= grantors for a in f_g.alternativas):
                exig = " ou ".join(self.nomes(a) for a in f_g.alternativas[:4])
                add("OUTORGA_SEM_PODERES", Severidade.BLOQUEIO, "Quem outorgou não tinha poder sozinho",
                    f"Na data da outorga ({_fmt_data(p.data)}), alienar este veículo exigia {exig}; a procuração foi "
                    f"assinada por {self.nomes(grantors) if grantors else 'representante não identificado'}. "
                    "Ninguém delega mais poder do que tem.", ["CC art. 47", "CC art. 1.014"],
                    [F.get("outorgante")] + [r.fonte for r in f_g.regras])
            elif not f_g.alternativas:
                add("PODERES_DO_OUTORGANTE_NAO_VERIFICADOS", Severidade.ALERTA, "Poder de quem outorgou não verificado",
                    "Não há ato societário vigente na data da outorga entre os documentos (ou ele não indica administradores): "
                    "não é possível confirmar que quem assinou pela empresa tinha poder. Apresente o contrato social/estatuto "
                    "e as alterações.", ["CC art. 1.018", "CC art. 47"], [F.get("outorgante")])
            elif f_g.alternativas:
                add("OUTORGA_COM_PODERES", Severidade.OK, "Quem outorgou tinha poder",
                    f"Em {_fmt_data(p.data)}, {self.nomes(grantors)} podia representar a empresa nesse ato.",
                    ["CC art. 1.018"], [F.get("outorgante")] + [r.fonte for r in f_g.regras])
            regras_poa = [r for r in reg_g.regras if r.escopo == "outorgar_procuracoes" and r.define_assinantes]
            if regras_poa:
                alts_poa = None
                for r in regras_poa:
                    ar = self.alternativas_regra(r, reg_g)
                    alts_poa = ar if alts_poa is None else minimizar([a | b for a in alts_poa for b in ar])
                if alts_poa and not any(a <= grantors for a in alts_poa):
                    add("OUTORGA_EM_DESACORDO", Severidade.ALERTA if incerto else Severidade.BLOQUEIO,
                        "Outorga em desacordo com o estatuto/contrato" + (" (pelos atos apresentados)" if incerto else ""),
                        f"Procurações exigem {' ou '.join(self.nomes(a) for a in alts_poa[:4])}"
                        + ("; faltam alterações que podem ter mudado essa regra." if incerto else "."), [],
                        [r.fonte for r in regras_poa] + [F.get("outorgante")])
            rp = reg_g.regras_procuracao
            if rp:
                if rp.vedada_para_alienacao:
                    add("PROCURACAO_VEDADA", Severidade.BLOQUEIO, "Contrato veda procuração para alienar",
                        "O contrato social proíbe outorgar procuração com poderes de alienação.", [], [rp.fonte])
                fim = self._fim_procuracao(p)
                if rp.prazo_maximo_meses:
                    dur = (fim - p.data).days if fim else None
                    if dur is None or dur > rp.prazo_maximo_meses * 31:
                        add("PRAZO_ACIMA_DO_CONTRATO", Severidade.ALERTA, "Prazo acima do permitido pelo contrato",
                            f"O contrato limita procurações a {rp.prazo_maximo_meses} meses; esta tem "
                            f"{'prazo indeterminado' if dur is None else f'{dur} dias'}.", [], [rp.fonte, F.get("validade")])
        # (c) poderes (comprador: poder de COMPRAR; vendedor: poder de ALIENAR)
        if pedido.lado == "comprador":
            if p.adquirir_veiculos:
                add("PODERES_COMPRA", Severidade.OK, "Poder expresso para comprar veículos",
                    "A procuração confere poder para comprar/adquirir veículos em nome da outorgante.", ["CC art. 661"],
                    [F.get("poderes")])
            elif p.alienar_veiculos:
                add("PODERES_SO_DE_VENDA", Severidade.BLOQUEIO, "Procuração é para vender, não para comprar",
                    "Os poderes são de alienação (vender/transferir); não há poder para adquirir veículo em nome da empresa.",
                    ["CC art. 661"], [F.get("poderes")])
            elif p.apenas_gerais:
                add("PODERES_GERAIS_PARA_COMPRA", self.pol.compra_com_poderes_gerais, "Só poderes gerais para a compra",
                    "Há apenas poderes gerais de administração. "
                    + ("O DETRAN-CE exige procuração específica para o ato." if self.pol.uf == "CE" else
                       "Comprar pode ser ato de administração, mas convém poder expresso."), ["CC art. 661"], [F.get("poderes")])
            else:
                add("SEM_PODER_DE_COMPRA", Severidade.BLOQUEIO, "Sem poder para comprar",
                    "A procuração não confere poder para adquirir veículos em nome da outorgante.", ["CC art. 661"],
                    [F.get("poderes")])
        elif p.apenas_gerais or not p.alienar_veiculos:
            add("PODERES_INSUFICIENTES", Severidade.BLOQUEIO, "Sem poder expresso para vender",
                "A procuração não confere poder expresso para alienar veículos"
                + (" — só poderes gerais de administração" if p.apenas_gerais else "")
                + ". Mandato em termos gerais só confere poderes de administração; alienar exige poderes especiais e expressos.",
                ["CC art. 661, caput e §1º"], [F.get("poderes")])
        else:
            add("PODERES_ESPECIAIS", Severidade.OK, "Poder expresso para alienar veículos",
                "Confere poder expresso para vender/transferir veículos" + (" e assinar a ATPV/ATPV-e." if p.assinar_atpv else "."),
                ["CC art. 661, §1º"], [F.get("poderes")])
            if not p.assinar_atpv:
                add("ATPV_NAO_CITADO", Severidade.ATENCAO, "ATPV não mencionado",
                    "Os poderes cobrem a venda, mas não citam o ATPV/ATPV-e; alguns cartórios exigem menção expressa.",
                    [], [F.get("poderes")])
        # (d) objeto
        if p.abrangencia == "veiculos_especificos":
            confs = [veiculo_confere(v, veic) for v in p.veiculos]
            if not any(c is True for c in confs):
                add("VEICULO_NAO_ABRANGIDO", Severidade.BLOQUEIO, "Procuração é para outro veículo",
                    "A procuração só abrange " + "; ".join(filter(None, (v.descricao or v.placa for v in p.veiculos)))
                    + f", não o veículo da venda ({veic.placa or veic.descricao}).", ["CC art. 661, §1º"], [F.get("poderes")])
            else:
                add("VEICULO_ABRANGIDO", Severidade.OK, "Veículo identificado na procuração",
                    "A procuração identifica exatamente este veículo.", [], [F.get("poderes")])
        # (e) prazo
        fim = self._fim_procuracao(p)
        if fim and fim < D:
            add("PROCURACAO_VENCIDA", Severidade.BLOQUEIO, "Procuração vencida",
                f"Válida até {_fmt_data(fim)}; a venda é em {_fmt_data(D)}.", ["CC art. 682, IV"], [F.get("validade")])
        elif fim:
            add("PROCURACAO_NO_PRAZO", Severidade.OK, "Dentro do prazo", f"Válida até {_fmt_data(fim)}.", [], [F.get("validade")])
        if p.data and (D - p.data).days > self.pol.idade_max_procuracao_dias and not (fim and fim < D):
            meses = (D - p.data).days // 30
            if self.pol.uf == "CE":
                add("PROCURACAO_ANTIGA", self.pol.idade_max_severidade, "Procuração com mais de 1 ano",
                    f"Expedida há {meses} meses. O DETRAN-CE aceita procuração pública e específica com validade de até "
                    "1 ano da data de expedição.", ["DETRAN-CE (serviço de transferência)"], [F.get("validade")])
            else:
                add("PROCURACAO_ANTIGA", self.pol.idade_max_severidade, "Procuração antiga",
                    f"Outorgada há {meses} meses. Peça certidão/traslado atualizado do cartório confirmando que não foi "
                    "revogada (a revogação fica anotada na serventia de origem).", ["CC art. 682"], [F.get("validade")])
        # (f) revogação
        for rev in self._revogacao_de(p):
            if rev.data and rev.data <= D:
                add("PROCURACAO_REVOGADA", Severidade.BLOQUEIO, "Procuração revogada",
                    f"Revogada em {_fmt_data(rev.data)} ({rev.titulo})"
                    + (" — revogação genérica que alcança esta procuração." if rev.generica else "."),
                    ["CC art. 682, I", "CC art. 686"], [rev.fonte])
            else:
                add("REVOGACAO_POSTERIOR", Severidade.INFO, "Revogação posterior à venda",
                    f"A revogação ({_fmt_data(rev.data)}) é posterior à venda.", [], [rev.fonte])
        # (g) forma
        if p.forma == "particular":
            sev = self.pol.procuracao_particular_com_firma if p.firma_reconhecida else self.pol.procuracao_particular_sem_firma
            tit = "Procuração particular" + (" com firma reconhecida" if p.firma_reconhecida else " sem firma reconhecida")
            if self.pol.uf == "CE":
                det = ("O DETRAN-CE só aceita procurador por instrumento de procuração PÚBLICA e específica para o ato. "
                       "(Civilmente o instrumento particular é válido; a exigência é do órgão.)")
                fund = ["DETRAN-CE (serviço de transferência)", "CC art. 654, §2º"]
            else:
                det = "Instrumento particular" + (" com reconhecimento de firma." if p.firma_reconhecida else
                                                  " sem reconhecimento de firma: o terceiro (DETRAN/cartório) pode exigir firma "
                                                  "reconhecida ou instrumento público.")
                fund = ["CC art. 654, §2º"]
            add("FORMA_PARTICULAR", sev, tit, det, fund, [F.get("outorgante")])
        if p.alienar_veiculos and p.abrangencia == "todos_veiculos_da_outorgante" and \
                self.pol.procuracao_sem_veiculo_identificado not in (Severidade.INFO, Severidade.OK):
            add("PROCURACAO_SEM_VEICULO", self.pol.procuracao_sem_veiculo_identificado, "Procuração não identifica o veículo",
                "Os poderes valem para os veículos da outorgante em geral, sem placa/RENAVAM/chassi deste veículo. "
                + ("O DETRAN-CE pede procuração 'específica para o ato': confirme se o entendimento do órgão exige "
                   "identificar o veículo." if self.pol.uf == "CE" else ""), ["CJF, Enunciado 183"], [F.get("poderes")])
        # (h) troca de administração depois da outorga
        if p.outorgante_tipo == "PJ" and p.outorgante_e_empresa and representantes:
            ativos = {a.pessoa for a in regime_venda.administradores}
            sairam = [r for r in representantes if r not in ativos]
            if sairam:
                add("MANDATO_SUBSISTE", Severidade.INFO, "Quem outorgou não é mais administrador",
                    f"{self.nomes(sairam)} deixou a administração depois da outorga, mas o mandato foi dado pela empresa e "
                    "não se extingue com a troca do administrador (as causas de extinção estão no art. 682).",
                    ["CC art. 682"], [F.get("outorgante")])
        bloqueado = any(a.severidade == Severidade.BLOQUEIO for a in ach)
        # (i) outorgados -> alternativas
        ativos_out = [o for o in p.outorgados if not (o in removidos and removidos[o][0] <= D)]
        for o in p.outorgados:
            if o in removidos and removidos[o][0] <= D:
                ach.append(Achado("SUBSTABELECEU_SEM_RESERVA", Severidade.BLOQUEIO, "Substabeleceu sem reserva",
                                  f"{self.nome(o)} substabeleceu sem reserva em {_fmt_data(removidos[o][0])} e deixou de ter os poderes.",
                                  ["CC art. 667"], [], f"{cam}:{o}"))
        if p.atuacao == "conjunta":
            sets = [frozenset(ativos_out)] if ativos_out and len(ativos_out) == len(p.outorgados) else []
        else:
            sets = [frozenset([o]) for o in ativos_out]
            if p.atuacao == "nao_especificada" and len(p.outorgados) > 1:
                add("ATUACAO_OUTORGADOS_OMISSA", Severidade.INFO, "Atuação dos procuradores não especificada",
                    "Com vários procuradores no mesmo instrumento, qualquer um pode agir se não forem declarados conjuntos.",
                    ["CC art. 672"], [F.get("poderes")])
        if p.exige_conjunto_com in ("diretor", "administrador"):
            parceiros = self.membros("diretores" if p.exige_conjunto_com == "diretor" else "administradores", regime_venda)
            sets = [s | {d} for s in sets for d in parceiros if d not in s]
        descricao = (f"{'Procuração pública' if p.forma == 'publica' else 'Procuração particular'} de "
                     f"{_fmt_data(p.data)}" + (f" ({p.cartorio})" if p.cartorio else ""))
        alts = [Alternativa(f"{cam}:{'+'.join(sorted(s))}", frozenset(s), "procuracao", descricao, [p.id],
                            achados=[a for a in ach if a.caminho in (cam, None)], confianca=p.confianca) for s in sets]
        bloqueadas = []
        todos_removidos = p.outorgados and all(o in removidos and removidos[o][0] <= D for o in p.outorgados)
        if (bloqueado or not alts) and not (todos_removidos and not bloqueado):
            pessoas = frozenset(p.outorgados)
            bloqueadas = [Alternativa(f"{cam}:bloqueada", pessoas, "procuracao", descricao, [p.id], achados=list(ach),
                                      confianca=p.confianca)]
            alts = []
        # outorgado removido por substabelecimento sem reserva: caminho bloqueado específico
        for o in p.outorgados:
            if o in removidos and removidos[o][0] <= D:
                bloqueadas.append(Alternativa(f"{cam}:{o}:sem_reserva", frozenset([o]), "procuracao", descricao, [p.id],
                                              achados=[a for a in ach if a.caminho in (cam, f'{cam}:{o}')], confianca=p.confianca))
        return alts, bloqueadas, ach

    def avaliar_substabelecimento(self, s: Substabelecimento, pedido: Pedido, regime_venda: Regime,
                                  status_origem: dict[str, tuple[list[Alternativa], list[Alternativa], list[Achado]]],
                                  status_subs: dict[str, tuple[list[Alternativa], list[Alternativa]]] | None = None
                                  ) -> tuple[list[Alternativa], list[Alternativa]]:
        status_subs = status_subs or {}
        D = pedido.data_venda
        cam = s.id
        ach: list[Achado] = []

        def add(cod, sev, tit, det, fund=(), fontes=()):
            ach.append(Achado(cod, sev, tit, det, list(fund), [f for f in fontes if f], cam))

        if s.data and s.data > D:
            return [], []
        origem = next((p for p in self.kb.procuracoes if p.id == s.procuracao_id), None)
        cadeia = [s.id]
        exige_conjunto = "nenhum"
        pai = None
        if origem is None and s.origem_sub_id:
            # substabelecimento de substabelecimento: sobe a cadeia até a procuração original
            pai = next((t for t in self.kb.substabelecimentos if t.id == s.origem_sub_id), None)
            elos, raiz, vistos = [s.id], pai, set()
            while raiz is not None and raiz.id not in vistos:
                vistos.add(raiz.id)
                elos.insert(0, raiz.id)
                if raiz.procuracao_id:
                    origem = next((p for p in self.kb.procuracoes if p.id == raiz.procuracao_id), None)
                    break
                raiz = next((t for t in self.kb.substabelecimentos if t.id == raiz.origem_sub_id), None)
            cadeia = ([origem.id] if origem else []) + elos
            add("SUBSTABELECIMENTO_EM_CADEIA", Severidade.ALERTA, "Substabelecimento em cadeia",
                f"{self.nome(s.substabelecente)} recebeu os poderes por outro substabelecimento ({len(elos)} níveis). "
                "O Código Civil não proíbe, mas há órgãos que aceitam um só nível: confirme a aceitação.",
                ["CC art. 667"], [s.fonte])
            st_pai = status_subs.get(pai.id) if pai else None
            if st_pai is not None and not st_pai[0] and st_pai[1]:
                add("CADEIA_INVALIDA", Severidade.BLOQUEIO, "Elo anterior da cadeia não vale",
                    "O substabelecimento de onde vieram os poderes não é válido.", ["CC art. 667"], [s.fonte])
        if origem is None:
            add("ORIGEM_NAO_APRESENTADA", Severidade.ALERTA, "Procuração de origem não apresentada",
                "Sem a procuração original não é possível conferir os poderes substabelecidos.", ["CC art. 667"], [s.fonte])
        else:
            if not pai:
                cadeia = [origem.id, s.id]
            exige_conjunto = origem.exige_conjunto_com
            _, _, ach_o = status_origem.get(origem.id, ([], [], []))
            motivos = [a for a in ach_o if a.severidade == Severidade.BLOQUEIO and a.caminho == origem.id]
            if motivos:
                add("ORIGEM_INVALIDA", Severidade.BLOQUEIO, "A procuração de origem não vale",
                    "O substabelecimento herda os vícios da procuração original: " + "; ".join(m.titulo.lower() for m in motivos) + ".",
                    ["CC art. 667"], [s.fonte] + [f for m in motivos for f in m.fontes])
            else:
                add("ORIGEM_VALIDA", Severidade.OK, "Procuração de origem válida",
                    f"Origem: procuração de {_fmt_data(origem.data)}.", [], [s.fonte])
                for a in ach_o:
                    if a.caminho == origem.id and a.severidade in (Severidade.ALERTA, Severidade.ATENCAO):
                        ach.append(Achado(a.codigo, a.severidade, a.titulo + " (procuração de origem)", a.detalhe,
                                          a.fundamento, a.fontes, cam))
            if not pai and s.substabelecente not in origem.outorgados:
                add("SUBSTABELECENTE_NAO_E_PROCURADOR", Severidade.BLOQUEIO, "Quem substabeleceu não é o procurador",
                    f"{self.nome(s.substabelecente)} não consta como outorgado da procuração de origem.", [], [s.fonte])
            if origem.substabelecimento == "vedado":
                add("SUBSTABELECIMENTO_VEDADO", Severidade.BLOQUEIO, "Substabelecimento proibido",
                    "A procuração original proíbe substabelecer: os atos do substabelecido não obrigam a empresa, salvo "
                    "ratificação expressa.", ["CC art. 667, §3º"], [origem.fontes.get("substabelecimento"), s.fonte])
            else:
                add("SUBSTABELECIMENTO_PERMITIDO", Severidade.OK, "Substabelecimento permitido",
                    "A procuração permite substabelecer" + (" (omissa: permitido, com responsabilidade do procurador)."
                                                           if origem.substabelecimento == "omisso" else "."),
                    ["CC art. 667"], [origem.fontes.get("substabelecimento")])
            fim = self._fim_procuracao(origem)
            if fim and s.data and s.data > fim:
                add("SUBSTABELECIDO_APOS_VENCER", Severidade.BLOQUEIO, "Substabelecido depois do vencimento",
                    f"A procuração venceu em {_fmt_data(fim)}.", [], [s.fonte])
            if fim and fim < D:
                add("PROCURACAO_VENCIDA", Severidade.BLOQUEIO, "Poderes vencidos",
                    f"Os poderes substabelecidos venceram em {_fmt_data(fim)}.", ["CC art. 682, IV"], [origem.fontes.get("validade")])
        if not (s.todos_os_poderes or s.alienar_veiculos):
            add("PODERES_NAO_SUBSTABELECIDOS", Severidade.BLOQUEIO, "Não substabeleceu o poder de vender",
                "O substabelecimento não transfere o poder de alienar veículos.", [], [s.fonte])
        if s.forma == "particular":
            sev = self.pol.substabelecimento_particular if s.firma_reconhecida else max(
                self.pol.procuracao_particular_sem_firma, self.pol.substabelecimento_particular, key=lambda x: ORDEM_SEV[x])
            add("SUBSTABELECIMENTO_PARTICULAR", sev, "Substabelecimento por instrumento particular",
                "O Código Civil admite substabelecer por instrumento particular mesmo procuração pública (art. 655), mas "
                "DETRAN e cartórios podem exigir a mesma forma do original.", ["CC art. 655"], [s.fonte])
        bloqueado = any(a.severidade == Severidade.BLOQUEIO for a in ach)
        sets = [frozenset([x]) for x in s.substabelecidos]
        if exige_conjunto in ("diretor", "administrador"):
            parceiros = self.membros("diretores" if exige_conjunto == "diretor" else "administradores", regime_venda)
            sets = [st | {d} for st in sets for d in parceiros if d not in st]
        desc = f"Substabelecimento {'com' if s.reserva == 'com_reserva' else 'sem' if s.reserva == 'sem_reserva' else ''} reserva de {_fmt_data(s.data)}".replace("  ", " ")
        if bloqueado:
            return [], [Alternativa(f"{cam}:bloqueada", frozenset(s.substabelecidos), "substabelecimento", desc, cadeia,
                                    achados=ach, confianca=s.confianca)]
        return [Alternativa(f"{cam}:{'+'.join(sorted(st))}", st, "substabelecimento", desc, cadeia, achados=list(ach),
                            confianca=min(s.confianca, origem.confianca if origem else 0.6)) for st in sets], []

    # ------------------------------------------------------------------------------ análise
    def resolver_assinantes(self, pedido: Pedido) -> tuple[frozenset[str], list[dict], list[Achado]]:
        chaves, info, ach = set(), [], []
        for a in pedido.assinantes:
            cpf = so_digitos(a.cpf)
            achou, criterio = None, None
            if len(cpf) == 11:
                achou = next((p.chave for p in self.kb.pessoas.values() if so_digitos(p.cpf) == cpf), None)
                criterio = "CPF" if achou else None
            if not achou:
                melhor = max(self.kb.pessoas.values(), key=lambda p: similaridade_nomes(a.nome, p.nome), default=None)
                if melhor and similaridade_nomes(a.nome, melhor.nome) >= 90:
                    if len(cpf) == 11 and melhor.cpf and so_digitos(melhor.cpf) != cpf:
                        ach.append(Achado("CPF_DIVERGENTE", Severidade.ALERTA, "CPF do assinante diverge",
                                          f"{a.nome}: o CPF informado não confere com o CPF de {melhor.nome} nos documentos."))
                    else:
                        achou, criterio = melhor.chave, f"nome ({similaridade_nomes(a.nome, melhor.nome):.0f}%)"
                        if len(cpf) != 11 or not melhor.cpf:
                            ach.append(Achado("IDENTIDADE_POR_NOME", Severidade.ATENCAO, "Assinante identificado só pelo nome",
                                              f"{a.nome} foi casado com {melhor.nome} pelo nome; confira o CPF."))
            chave = achou or f"?{a.nome}"
            chaves.add(chave)
            info.append({"informado": a.nome, "cpf": a.cpf, "chave": chave,
                         "nome": self.nome(achou) if achou else a.nome, "criterio": criterio or "não encontrado nos documentos"})
            if not achou:
                ach.append(Achado("ASSINANTE_DESCONHECIDO", Severidade.INFO, "Assinante não aparece nos documentos",
                                  f"{a.nome} não é sócio, administrador nem procurador em nenhum documento apresentado."))
        return frozenset(chaves), info, ach

    def _restricao_nao_lida(self, regime: Regime, veic: VeiculoId, ato: str) -> list[Achado]:
        """Sentinela de leitura: o texto vigente tem cláusula de aprovação prévia (sócios, conselho, quórum) que alcança
        veículos, mas nenhuma regra lida pela IA exige aprovação para este ato. Uma omissão da leitura não pode virar
        aceite automático: o caso vai para revisão, com o trecho da cláusula."""
        lidas = [r for r in regime.regras if (r.exige_aprovacao_socios or r.efeito == "veda")
                 and self.aplicabilidade(r, veic, None, ato)[0] is not False]
        if lidas or not regime.atos:
            return []
        completos = [i for i, a in enumerate(regime.atos) if a.consolida or a.tipo in ATOS_COMPLETOS]
        vigentes = regime.atos[completos[-1]:] if completos else regime.atos  # último texto completo e alterações posteriores
        fontes = [f for a in vigentes for f, atos in a.restricoes_texto if ato in atos]
        if not fontes:
            return []
        return [Achado("RESTRICAO_NAO_LIDA", Severidade.ALERTA, "Cláusula de aprovação prévia não lida pela IA",
                       "O texto do contrato tem uma cláusula que exige aprovação prévia (de sócios, do conselho ou por quórum) "
                       f"para {'vender' if ato == 'alienar' else 'comprar'} bens que podem incluir o veículo, mas a leitura da IA "
                       "não a trouxe como regra aplicável. Confira a cláusula e, se ela valer, a ata de aprovação.",
                       ["CC art. 1.010", "CC art. 1.015, parágrafo único"], fontes[:2])]

    def _checar_titularidade(self, pedido: Pedido, regime: Regime) -> list[Achado]:
        ach = []
        c = self.kb.crlv
        if c is None and self.kb.titular_fonte == "base veicular":
            ach.append(Achado("TITULARIDADE_BASE", Severidade.OK, "Proprietário conferido na base veicular",
                              f"Pela placa/RENAVAM, o veículo está em nome de {self.kb.empresa.razao_social}.", ["CTB art. 123"]))
            return ach
        if c is None:
            sev = self.pol.crlv_ausente
            ach.append(Achado("CRLV_NAO_APRESENTADO", sev, "CRLV não apresentado",
                              "Não foi possível conferir se o veículo está registrado no CNPJ da empresa."))
            return ach
        ok_veic = veiculo_confere(VeiculoId(c.marca_modelo, c.placa, c.renavam, c.chassi), pedido.veiculo)
        if ok_veic is False:
            ach.append(Achado("DIVERGENCIA_VEICULO", Severidade.BLOQUEIO, "CRLV de outro veículo",
                              f"O CRLV é do veículo {c.placa}, diferente do informado na venda.", [], [c.fonte]))
        doc = so_digitos(c.proprietario_doc)
        cnpj = so_digitos(self.kb.empresa.cnpj)
        if self.kb.empresa.tipo == "PF":
            titular = self.kb.atos[0].administradores[0].pessoa if self.kb.atos else None
            cpf_t = so_digitos(self.kb.pessoas[titular].cpf) if titular and self.kb.pessoas.get(titular) else ""
            if (doc and cpf_t and doc == cpf_t) or (not doc and c.proprietario_nome and titular
                                                     and similaridade_nomes(c.proprietario_nome, self.nome(titular)) >= 92):
                ach.append(Achado("TITULARIDADE_OK", Severidade.OK, "Veículo registrado no CPF do proprietário",
                                  f"Proprietário no CRLV: {c.proprietario_nome}.", ["CTB art. 123"], [c.fonte]))
            else:
                ach.append(Achado("VEICULO_DE_TERCEIRO", Severidade.BLOQUEIO, "Veículo não pertence a quem outorga",
                                  f"O CRLV está em nome de {c.proprietario_nome or 'terceiro'}.", ["CTB art. 123"], [c.fonte]))
            return ach
        if doc and cnpj and doc == cnpj:
            ach.append(Achado("TITULARIDADE_OK", Severidade.OK, "Veículo registrado no CNPJ da empresa",
                              f"Proprietário no CRLV: {c.proprietario_nome}.", ["CTB art. 123"], [c.fonte]))
            return ach
        pessoa = None
        if len(doc) == 11:
            pessoa = next((p.chave for p in self.kb.pessoas.values() if so_digitos(p.cpf) == doc), None)
        elif not doc and c.proprietario_nome:
            pessoa = next((p.chave for p in self.kb.pessoas.values() if similaridade_nomes(p.nome, c.proprietario_nome) >= 92), None)
        if self.kb.empresa.tipo == "EI" and pessoa and pessoa in regime.socios:
            ach.append(Achado("TITULARIDADE_EI", Severidade.INFO, "Veículo no CPF do titular do empresário individual",
                              "No empresário individual, CPF e CNPJ são o mesmo patrimônio.", ["CC art. 966"], [c.fonte]))
            return ach
        integralizado = any(b.socio == pessoa for b in regime.bens) if pessoa else False
        if pessoa and (pessoa in regime.socios or integralizado):
            ach.append(Achado("TITULARIDADE_REGISTRAL_DIVERGENTE", Severidade.ALERTA, "CRLV ainda no CPF do sócio",
                              f"O veículo consta no DETRAN em nome de {self.nome(pessoa)} (pessoa física)"
                              + (", embora tenha sido conferido ao capital da empresa" if integralizado else "")
                              + ". O ATPV é emitido em nome do proprietário registral: regularize a transferência para o CNPJ "
                                "ou a venda terá de ser assinada pelo sócio como pessoa física.", ["CTB art. 123"], [c.fonte]))
        else:
            ach.append(Achado("VEICULO_DE_TERCEIRO", Severidade.BLOQUEIO, "Veículo não pertence à empresa",
                              f"O CRLV está em nome de {c.proprietario_nome or 'terceiro'}.", ["CTB art. 123"], [c.fonte]))
        return ach

    def _avaliar_precondicoes(self, alt: Alternativa, precs: list[Precondicao], S: frozenset[str], pedido: Pedido,
                              regime: Regime) -> list[Precondicao]:
        out = []
        for pc in precs:
            pc = Precondicao(pc.codigo, pc.descricao, pc.quorum, None, pc.detalhe, list(pc.fontes), pc.pessoas)
            if pc.pessoas and not (alt.pessoas & pc.pessoas):
                pc.satisfeita = True  # o caminho não usa quem a condição alcança
                out.append(pc)
                continue
            if pc.codigo == "DELIBERACAO_SOCIOS":
                q = pc.quorum or self.pol.quorum_padrao_deliberacao
                falhou = False
                for d in sorted(self.kb.deliberacoes, key=lambda d: d.data or date.min):
                    if not (d.aprovada and d.tipo == "aprova_alienacao_veiculo" and (d.data is None or d.data <= pedido.data_venda)):
                        continue
                    if d.veiculos and not any(veiculo_confere(v, pedido.veiculo) for v in d.veiculos):
                        continue
                    pct = d.percentual or 0
                    if pct + 1e-9 < q:
                        pc.detalhe = (f"A deliberação apresentada teve {pct:g}% do capital, abaixo dos "
                                      f"{q:g}% exigidos pelo contrato.")
                        pc.fontes.append(d.fonte)
                        falhou = True
                        continue
                    if d.valor_minimo and pedido.valor is not None and pedido.valor < d.valor_minimo:
                        pc.satisfeita = False
                        pc.detalhe = (f"A ata aprovou a venda por no mínimo {_fmt_valor(d.valor_minimo)}; "
                                      f"a venda é por {_fmt_valor(pedido.valor)}.")
                        pc.fontes.append(d.fonte)
                        break
                    pc.satisfeita = True
                    pc.detalhe = f"Aprovada em {_fmt_data(d.data)} por sócios com {pct:g}% do capital."
                    pc.fontes.append(d.fonte)
                    break
                if pc.satisfeita is None:
                    pct_ass = sum(regime.socios.get(k, 0) for k in S)
                    if pct_ass + 1e-9 >= q:
                        pc.satisfeita = True
                        pc.detalhe = (f"Os assinantes somam {pct_ass:g}% do capital: a assinatura conjunta supre a "
                                      "aprovação prévia.")
                    elif falhou:
                        pc.satisfeita = False  # a aprovação foi tentada e não alcançou o quórum: não pode
                    else:
                        pc.satisfeita = None
                        pc.detalhe = (pc.detalhe + " " if pc.detalhe else "") + "Nenhuma ata de aprovação foi apresentada."
            out.append(pc)
        return out

    def analisar(self, pedido: Pedido) -> Resultado:
        self._lado = pedido.lado
        D, veic = pedido.data_venda, pedido.veiculo
        ato = "adquirir" if pedido.lado == "comprador" else "alienar"
        regime = self.regime_em(D)
        achados: list[Achado] = []
        indet: list[str] = []
        # 1) fórmula do contrato
        f = self.formula(regime, veic, pedido.valor, ato=ato)
        base_alts = []
        for s in f.alternativas:
            r_ids = [r.id for r in f.regras]
            desc = ("Regra supletiva (contrato não define a forma de assinar)" if not f.regras else
                    self._rotulo_regra(f.regras[0]).capitalize() if self.kb.empresa.tipo == "PF" else
                    "; ".join(dict.fromkeys(f"{self._rotulo_regra(r, veic)} — {r.fonte.clausula or r.fonte.doc_titulo}"
                                            for r in f.regras)))
            ach_alt = []
            if f.omissa and not f.regras and self.kb.empresa.tipo == "SA":
                ach_alt.append(Achado("LSA_144", Severidade.INFO, "Estatuto omisso: qualquer diretor representa",
                                      "No silêncio do estatuto e sem deliberação do Conselho, qualquer diretor representa a companhia.",
                                      ["Lei 6.404/76, art. 144"], [], "contrato"))
            elif f.omissa and not f.regras and self.kb.empresa.tipo in ("COOPERATIVA", "ASSOCIACAO"):
                ach_alt.append(Achado("ESTATUTO_SEM_REPRESENTACAO", Severidade.ALERTA, "Estatuto sem regra de representação lida",
                                      "Não foi encontrada a regra de quem representa a entidade; para cooperativas e associações "
                                      "não há regra supletiva — confira o estatuto.", ["CC art. 46, III", "Lei 5.764/71, art. 21, V"],
                                      [], "contrato"))
            elif f.omissa:
                ach_alt.append(Achado("FORMA_ATUACAO_OMISSA", Severidade.ALERTA, "Contrato omisso sobre a forma de atuação",
                                      "Há mais de um administrador e o contrato não diz se atuam isolada ou conjuntamente. "
                                      "A regra supletiva (art. 1.013) indica atuação separada, mas há risco de questionamento: "
                                      "recomenda-se assinatura conjunta ou declaração dos sócios.",
                                      ["CC art. 1.013", "CC art. 1.014"], [r.fonte for r in f.regras], "contrato"))
            if not f.regras and self.kb.empresa.tipo != "EI":
                ach_alt.append(Achado("SEM_REGRA_ESPECIFICA", Severidade.ATENCAO, "Sem cláusula sobre quem assina",
                                      "Nenhuma cláusula define quem representa a empresa neste ato; aplicada a regra supletiva.",
                                      ["CC art. 1.013", "CC art. 1.060"], [], "contrato"))
            for r in f.regras:
                for v in r.verificacoes:
                    if v.divergiu:
                        ach_alt.append(Achado("CONFERENCIA_LEXICA", Severidade.ATENCAO, "Leitura da IA corrigida pela conferência léxica",
                                              f"Campo '{v.campo}': a IA leu '{v.valor_llm}', mas as expressões "
                                              f"{', '.join(repr(e) for e in v.expressoes[:3])} indicam '{v.valor_lexico}'.",
                                              [], [r.fonte], "contrato"))
            conf = min([r.confianca for r in f.regras] or [0.85])
            base_alts.append(Alternativa(f"contrato:{'+'.join(sorted(s))}", s, "contrato", desc,
                                         sorted({r.fonte.doc_id for r in f.regras}) or [a.doc_id for a in regime.atos[-1:]],
                                         r_ids, ach_alt, confianca=conf))
        if f.valor_indeterminado:
            indet.append("valor do veículo não informado — a regra de alçada não pode ser aplicada")
            achados.append(Achado("VALOR_NAO_INFORMADO", Severidade.ALERTA, "Valor do veículo não informado",
                                  "O contrato tem alçada por valor; informe o valor de venda (ou FIPE) para decidir.",
                                  [], [a["fonte"] for a in f.avaliacao if a["aplicavel"] is None]))
        for rv in self.kb.revogacoes:
            if not rv.procuracao_ids and (rv.data is None or rv.data <= D):
                achados.append(Achado("REVOGACAO_NAO_VINCULADA", Severidade.ALERTA, "Revogação que não se liga a uma procuração",
                                      f"Há um ato de revogação ({rv.titulo}) que não foi possível ligar a nenhuma procuração "
                                      "apresentada. Confira se ele alcança a procuração usada na venda.", ["CC art. 682, I"],
                                      [rv.fonte]))
        achados += self._restricao_nao_lida(regime, veic, ato)
        if not self.kb.atos:
            achados.append(Achado("SEM_ATO_CONSTITUTIVO", Severidade.ALERTA, "Contrato social/estatuto não apresentado",
                                  "Sem o ato constitutivo vigente não há como saber quem representa a empresa.",
                                  ["CC art. 997", "CC art. 1.060"]))
        if pedido.vendedor_cnpj and self.kb.empresa.cnpj and so_digitos(pedido.vendedor_cnpj) != so_digitos(self.kb.empresa.cnpj):
            achados.append(Achado("CNPJ_DIVERGENTE", Severidade.BLOQUEIO, "Documentos de outra empresa",
                                  f"O vendedor informado tem CNPJ {pedido.vendedor_cnpj}, mas os documentos são de "
                                  f"{self.kb.empresa.razao_social} (CNPJ {self.kb.empresa.cnpj})."))
        if regime.encerrados:
            for adm, motivo in regime.encerrados:
                achados.append(Achado("MANDATO_ENCERRADO", Severidade.ALERTA, "Administrador sem mandato em vigor",
                                      f"{self.nome(adm.pessoa)}: {motivo}, sem recondução nos documentos apresentados.",
                                      ["CC art. 1.063"], [adm.fonte]))
        if self.kb.empresa.subtipo == "EIRELI":
            achados.append(Achado("EIRELI_SLU", Severidade.INFO, "EIRELI transformada em sociedade limitada unipessoal",
                                  "As EIRELI existentes foram transformadas em SLU por força de lei, sem alterar o ato constitutivo; "
                                  "o titular segue como sócio único.", ["Lei 14.195/2021, art. 41"]))
        if self.kb.empresa.subtipo == "MEI":
            achados.append(Achado("MEI_EI", Severidade.INFO, "Microempreendedor individual",
                                  "O MEI é empresário individual: o próprio titular assina pelo CNPJ.", ["CC art. 966", "LC 123/2006, art. 18-A"]))
        lac_venda = self.lacuna_em(D)
        if lac_venda:
            achados.append(Achado("LACUNA_DE_ALTERACOES", Severidade.ALERTA, "Alterações contratuais faltando",
                                  f"Os documentos vão da alteração nº {lac_venda[0]} à nº {lac_venda[1]}: faltam as "
                                  "intermediárias, que podem ter mudado a administração. Apresente-as ou a certidão de "
                                  "inteiro teor da Junta.", ["Lei 8.934/94, art. 36"]))
        for adm, motivo in regime.prorrogados:
            achados.append(Achado("MANDATO_PRORROGADO", Severidade.ATENCAO, "Prazo de gestão vencido (S.A.)",
                                  f"{self.nome(adm.pessoa)}: {motivo}; na S.A. o prazo se estende até a investidura dos "
                                  "sucessores. Confirme se houve nova eleição.", ["Lei 6.404/76, art. 150, §4º"], [adm.fonte]))
        emp = self.kb.empresa
        escopos_bens = {"alienacao_ativo_imobilizado", "alienacao_bens", "alienacao_bens_moveis", "alienacao_veiculos",
                        "veiculo_especifico"}
        if ato == "alienar" and emp.tipo == "SA" and not emp.comercializa_veiculos and not any(r.escopo in escopos_bens for r in regime.regras):
            achados.append(Achado("AUTORIZACAO_CONSELHO", Severidade.ALERTA, "Autorização do Conselho de Administração",
                                  "Na S.A., alienar bem do ativo não circulante depende de autorização do Conselho, se o estatuto "
                                  "não dispuser em contrário. O estatuto apresentado não trata do tema: apresente a ata do Conselho.",
                                  ["Lei 6.404/76, art. 142, VIII"]))
        if ato == "alienar" and emp.tipo != "PF" and not emp.comercializa_veiculos and pedido.valor \
                and pedido.valor > self.pol.limite_cnd_inss and self.pol.cnd_inss != Severidade.OK:
            achados.append(Achado("CND_INSS", self.pol.cnd_inss, "CND previdenciária",
                                  f"Valor acima de {_fmt_valor(self.pol.limite_cnd_inss)}: a lei exige CND na alienação de bem "
                                  "incorporado ao ativo permanente; verifique a exigência do órgão.", ["Lei 8.212/91, art. 47, I, \"c\""]))
        if not f.alternativas and not f.valor_indeterminado:
            achados.append(Achado("SEM_REPRESENTANTE", Severidade.ALERTA, "Ninguém com poder de administração em vigor",
                                  "Nenhum administrador com mandato vigente foi encontrado. É preciso regularizar a "
                                  "administração (recondução/eleição) antes da venda.", ["CC art. 1.063", "CC art. 1.060"]))
        # 2) procurações e substabelecimentos
        removidos: dict[str, tuple[date, str]] = {}
        for s in self.kb.substabelecimentos:
            if s.reserva == "sem_reserva" and s.data and s.data <= D:
                removidos[s.substabelecente] = (s.data, s.id)
        status_poa = {}
        deleg_alts, bloqueadas = [], []
        for p in sorted(self.kb.procuracoes, key=lambda p: p.data or date.min):
            alts, bl, ach_p = self.avaliar_procuracao(p, pedido, regime, removidos)
            status_poa[p.id] = (alts, bl, ach_p)
            deleg_alts += alts
            bloqueadas += bl
        status_subs: dict[str, tuple[list[Alternativa], list[Alternativa]]] = {}
        for s in sorted(self.kb.substabelecimentos, key=lambda s: s.data or date.min):
            alts, bl = self.avaliar_substabelecimento(s, pedido, regime, status_poa, status_subs)
            status_subs[s.id] = (alts, bl)
            deleg_alts += alts
            bloqueadas += bl
        # preconditions do contrato valem para qualquer caminho; anuência exigida idem
        anuencia = set(f.anuencias)
        for a in deleg_alts:
            if anuencia:
                outorgantes = set().union(*[set(p.representantes) for p in self.kb.procuracoes if p.id in a.cadeia])
                if not anuencia <= outorgantes:
                    a.pessoas = a.pessoas | frozenset(anuencia - outorgantes)
                else:
                    a.achados.append(Achado("ANUENCIA_VIA_PROCURACAO", Severidade.ALERTA, "Anuência dada por meio de procuração",
                                            f"O contrato exige a assinatura de {self.nomes(anuencia)}, que outorgou a procuração. "
                                            "Confirme se a procuração cobre essa exigência específica.", [], [], a.id))
        todas = base_alts + deleg_alts
        # 3) assinantes e titularidade
        S, info_ass, ach_ass = self.resolver_assinantes(pedido)
        achados += ach_ass
        if ato == "alienar":
            achados += self._checar_titularidade(pedido, regime)
        for a in todas:  # validade hipotética de cada combinação: conta só o capital de quem está nela
            a.precondicoes = self._avaliar_precondicoes(a, f.precondicoes, a.pessoas, pedido, regime)
        reprovadas = [a for a in todas if any(pc.satisfeita is False for pc in a.precondicoes)]
        for a in reprovadas:
            pc = next(pc for pc in a.precondicoes if pc.satisfeita is False)
            a.achados.append(Achado(pc.codigo, Severidade.BLOQUEIO, pc.descricao + " — não atendida", pc.detalhe,
                                    ["CC art. 1.015", "CC art. 1.072"], pc.fontes, a.id))
        todas = [a for a in todas if a not in reprovadas]
        bloqueadas += reprovadas
        satisf = [a for a in todas if a.pessoas <= S] if S else []
        global_bloqueio = [a for a in achados if a.severidade == Severidade.BLOQUEIO]
        if not S:
            indet.append("assinantes não informados — consulta de quem pode assinar")
        escolhida = None
        faltantes = []
        if satisf:
            escolhida = min(satisf, key=lambda a: (ORDEM_SEV[a.severidade], len(a.cadeia), len(a.pessoas), -a.confianca))
            # no caminho escolhido valem os assinantes reais (ex.: todos os sócios assinando suprem a aprovação prévia)
            escolhida.precondicoes = self._avaliar_precondicoes(escolhida, f.precondicoes, S, pedido, regime)
            if any(x.codigo in INCERTEZA_CAMINHO for x in escolhida.achados):
                indet.append("o poder de quem outorgou a procuração depende de documento não apresentado")
            pend = [pc for pc in escolhida.precondicoes if pc.satisfeita is not True]
            for pc in pend:
                if pc.codigo in SO_ALERTA:
                    achados.append(Achado(pc.codigo, Severidade.ALERTA, pc.descricao, pc.detalhe, ["CC art. 1.015"], pc.fontes))
                    continue
                if pc.satisfeita is False:
                    global_bloqueio.append(Achado(pc.codigo, Severidade.BLOQUEIO, pc.descricao, pc.detalhe, [], pc.fontes))
                else:
                    indet.append(pc.descricao)
                    achados.append(Achado(pc.codigo, Severidade.ALERTA, pc.descricao + " — pendente", pc.detalhe,
                                          ["CC art. 1.015", "CC art. 1.072"], pc.fontes))
            if global_bloqueio:
                veredito = Veredito.NAO_PODE
            elif indet or any(a.codigo == "TITULARIDADE_REGISTRAL_DIVERGENTE" for a in achados):
                veredito = Veredito.INDETERMINADO
            else:
                veredito = Veredito.PODE
        elif not S:
            veredito = Veredito.INDETERMINADO
        elif (self.kb.empresa.tipo == "PF" or pedido.consulta) and not global_bloqueio and not (S & self._outorgados_todos()):
            # ninguém que vai assinar aparece em procuração apresentada: antes de recusar, pergunta pela procuração
            veredito = Veredito.INDETERMINADO
            pf = self.kb.empresa.tipo == "PF"
            papel = ("proprietário" if self._lado == "vendedor" else "comprador") if pf else "administrador"
            acao = "vender" if self._lado == "vendedor" else "comprar"
            indet.append("falta a procuração de quem vai assinar")
            quem = self.nomes(regime.socios) if pf else " ou ".join(self.nomes(a.pessoas) for a in todas[:4]) or "ninguém"
            achados.append(Achado("PROCURACAO_NECESSARIA", Severidade.ALERTA, "Precisa de procuração",
                                  (f"Quem vai assinar não é o próprio {papel} ({quem})." if pf else
                                   f"Pelos atos apresentados, quem vai assinar não tem poder para {acao} (quem pode: {quem}).")
                                  + f" Se for procurador, anexe a procuração com poderes para {acao} o veículo"
                                  + (" — pública, específica e com até 1 ano (DETRAN-CE)" if self.pol.uf == "CE" else "")
                                  + " e os substabelecimentos, se houver.", ["CC arts. 653 e 661"]))
        else:
            if f.valor_indeterminado:
                ramos = [self.formula(regime, veic, pedido.valor, forcar_valor=h, ato=ato) for h in ("acima", "abaixo")]
                pode_em_algum = any(any(s <= S for s in r.alternativas) for r in ramos)
                veredito = Veredito.INDETERMINADO if pode_em_algum else Veredito.NAO_PODE
            else:
                veredito = Veredito.NAO_PODE
            for a in sorted(todas, key=lambda a: (len(a.pessoas - S), ORDEM_SEV[a.severidade]))[:4]:
                faltantes.append({"alternativa": a.id, "via": a.via, "descricao": a.descricao,
                                  "pessoas": sorted(a.pessoas), "faltam": sorted(a.pessoas - S)})
        resumo = self._resumo(veredito, escolhida, S, todas, bloqueadas, f, indet, global_bloqueio)
        fatos = self._fatos_decisivos(veredito, escolhida, f, bloqueadas, S)
        grafo = self._grafo(regime, f, todas, bloqueadas, S, pedido)
        tl = self._linha_do_tempo(pedido)
        return Resultado(veredito, resumo, todas, bloqueadas, satisf, escolhida, info_ass, faltantes,
                         achados + [a for a in global_bloqueio if a not in achados], f, regime, fatos, grafo, tl, indet)

    # ----------------------------------------------------------------------------- relatório
    def _resumo(self, v, esc, S, todas, bloqueadas, f, indet, bloq) -> str:
        quem = " ou ".join(self.nomes(a.pessoas) + (" (procurador)" if a.via != "contrato" else "") for a in todas[:5]) or "ninguém"
        if not S:
            return f"Consulta (sem assinantes informados): quem pode assinar a ATPV-e deste veículo — {quem}."
        pf = self.kb.empresa.tipo == "PF"
        papel_pf = "proprietário" if self._lado == "vendedor" else "comprador"
        if v == Veredito.PODE and pf and esc.via == "contrato":
            return f"{self.nomes(esc.pessoas)} é o próprio {papel_pf} (pessoa física): assina em nome próprio."
        if v == Veredito.PODE and pf:
            return (f"{self.nomes((esc.pessoas - set(regime_titular(self))) or esc.pessoas)} pode assinar a ATPV-e como procurador(a) de "
                    f"{self.kb.empresa.razao_social} — {esc.descricao[0].lower() + esc.descricao[1:]}.")
        if v == Veredito.PODE:
            verbo = "pode" if len(esc.pessoas) == 1 else "podem, em conjunto,"
            papel = " como comprador(a)" if self._lado == "comprador" else ""
            return f"{self.nomes(esc.pessoas)} {verbo} assinar a ATPV-e{papel} — {esc.descricao[0].lower() + esc.descricao[1:]}."
        if v == Veredito.INDETERMINADO and any(i.startswith("falta a procuração") for i in indet):
            acao = "vender" if self._lado == "vendedor" else "comprar"
            outros = self._outorgados_todos()
            obs = (f" A procuração apresentada é para {self.nomes(outros)}, não para quem vai assinar." if outros else "")
            if pf:
                return (f"O CPF informado não é o do {papel_pf} ({self.kb.empresa.razao_social}).{obs} Se quem vai assinar é "
                        "procurador, anexe a procuração dele para conferir se ela dá poder para este ato.")
            return (f"Pelos atos apresentados, {self.nomes(S)} não tem poder para {acao} pela empresa (quem pode: {quem}).{obs} "
                    "Se for procurador, anexe a procuração para conferir.")
        if v == Veredito.INDETERMINADO:
            return "Não é possível decidir com segurança: " + "; ".join(indet or ["há pendência de titularidade no CRLV"]) + "."
        motivo = ""
        envolvidos = [b for b in bloqueadas if b.pessoas & S]
        if envolvidos:
            b = envolvidos[0]
            tits = [a.titulo.lower() for a in b.achados if a.severidade == Severidade.BLOQUEIO]
            motivo = f" O caminho por {b.descricao.lower()} não vale: {', '.join(dict.fromkeys(tits))}."
        elif bloq:
            motivo = " " + bloq[0].titulo + "."
        elif f.regras:
            r = f.regras[0]
            motivo = f" Regra aplicável: {self._rotulo_regra(r)} ({r.fonte.clausula or r.fonte.doc_titulo})."
        return f"Os assinantes informados não bastam. Quem pode assinar: {quem}.{motivo}"

    def _fatos_decisivos(self, v, esc, f: Formula, bloqueadas, S) -> list[dict]:
        fatos = []
        for r in f.regras:
            fatos.append({"tipo": "regra", "id": r.id, "confianca": r.confianca, "fonte": r.fonte})
        if esc and esc.via == "contrato" or (v == Veredito.PODE and not f.regras):
            designacoes = {}
            for ato in self.kb.atos:
                for adm in ato.administradores:
                    if esc is None or adm.pessoa in esc.pessoas:
                        designacoes[adm.pessoa] = adm
            for adm in designacoes.values():
                fatos.append({"tipo": "administrador", "id": adm.pessoa, "confianca": fator_ancoragem(adm.fonte.ancoragem),
                              "fonte": adm.fonte})
        if esc and esc.via != "contrato":
            for doc_id in esc.cadeia:
                obj = next((p for p in self.kb.procuracoes if p.id == doc_id), None) or \
                      next((s for s in self.kb.substabelecimentos if s.id == doc_id), None)
                if obj:
                    fatos.append({"tipo": esc.via, "id": doc_id, "confianca": obj.confianca, "fonte": None})
        if v == Veredito.NAO_PODE:
            for b in bloqueadas:
                if b.pessoas & S:
                    for doc_id in b.cadeia:
                        obj = next((p for p in self.kb.procuracoes if p.id == doc_id), None) or \
                              next((s for s in self.kb.substabelecimentos if s.id == doc_id), None)
                        if obj:
                            fatos.append({"tipo": "bloqueio", "id": doc_id, "confianca": obj.confianca, "fonte": None})
        return fatos

    def _grafo(self, regime: Regime, f: Formula, todas, bloqueadas, S, pedido) -> dict:
        nos, arestas = {}, []
        emp = self.kb.empresa
        nos["EMPRESA"] = {"id": "EMPRESA", "tipo": "empresa", "rotulo": emp.razao_social, "sub": emp.cnpj or ""}
        nos["VEICULO"] = {"id": "VEICULO", "tipo": "veiculo", "rotulo": pedido.veiculo.descricao or pedido.veiculo.placa or "veículo",
                          "sub": pedido.veiculo.placa or ""}
        arestas.append({"de": "EMPRESA", "para": "VEICULO", "tipo": "propriedade", "rotulo": "proprietária",
                        "status": "valido" if self.kb.crlv else "alerta"})

        def pessoa(ch, papel):
            if ch not in nos:
                nos[ch] = {"id": ch, "tipo": "pessoa", "rotulo": self.nome(ch), "papeis": [], "assinante": ch in S}
            if papel not in nos[ch]["papeis"]:
                nos[ch]["papeis"].append(papel)

        for k, pct in regime.socios.items():
            pessoa(k, f"sócio {pct:g}%")
            arestas.append({"de": k, "para": "EMPRESA", "tipo": "socio", "rotulo": f"{pct:g}%", "status": "neutro"})
        modo = {a: ("isolado" if len(a) == 1 else "em conjunto") for a in f.alternativas}
        for adm in regime.administradores:
            pessoa(adm.pessoa, adm.cargo)
            alts = [a for a in f.alternativas if adm.pessoa in a]
            rot = "administra · " + (", ".join(sorted({modo[a] for a in alts})) if alts else "sem poder para este ato")
            arestas.append({"de": "EMPRESA", "para": adm.pessoa, "tipo": "administracao", "rotulo": rot,
                            "status": "valido" if alts else "invalido", "doc": adm.fonte.doc_id})
        for adm, motivo in regime.encerrados:
            pessoa(adm.pessoa, f"ex-{adm.cargo}")
            arestas.append({"de": "EMPRESA", "para": adm.pessoa, "tipo": "administracao", "rotulo": motivo,
                            "status": "invalido", "doc": adm.fonte.doc_id})
        for a in f.alternativas:
            for p in a:
                if p not in nos:
                    pessoa(p, "assinatura exigida pelo contrato")
                    arestas.append({"de": "EMPRESA", "para": p, "tipo": "clausula", "rotulo": "cláusula específica",
                                    "status": "valido"})
        vistos = set()
        for alt in todas + bloqueadas:
            if alt.via == "contrato":
                continue
            st = "invalido" if alt in bloqueadas else ("alerta" if ORDEM_SEV[alt.severidade] >= 2 else "valido")
            doc_id = alt.cadeia[-1]
            motivo = next((a.titulo for a in alt.achados if a.severidade == Severidade.BLOQUEIO), None)
            if alt.via == "procuracao":
                p = next(p for p in self.kb.procuracoes if p.id == doc_id)
                origem = "EMPRESA" if p.outorgante_tipo == "PJ" else (p.representantes[0] if p.representantes else "EMPRESA")
                if origem != "EMPRESA":
                    pessoa(origem, "outorgante (pessoa física)")
                for o in p.outorgados:
                    if (doc_id, o) in vistos:
                        continue
                    vistos.add((doc_id, o))
                    pessoa(o, "procurador")
                    st_o = "invalido" if any(b.id.startswith(f"{doc_id}:{o}:") for b in bloqueadas) else st
                    arestas.append({"de": origem, "para": o, "tipo": "procuracao", "status": st_o, "doc": doc_id,
                                    "rotulo": f"procuração {_fmt_data(p.data)}" + (f" · {motivo}" if motivo and st_o == 'invalido' else ""),
                                    "motivo": motivo})
            else:
                s = next(s for s in self.kb.substabelecimentos if s.id == doc_id)
                for x in s.substabelecidos:
                    if (doc_id, x) in vistos:
                        continue
                    vistos.add((doc_id, x))
                    pessoa(s.substabelecente, "procurador")
                    pessoa(x, "substabelecido")
                    arestas.append({"de": s.substabelecente, "para": x, "tipo": "substabelecimento", "status": st, "doc": doc_id,
                                    "rotulo": f"substabelece {s.reserva.replace('_', ' ')}" + (f" · {motivo}" if motivo and st == 'invalido' else ""),
                                    "motivo": motivo})
        for ch in S:
            if ch not in nos:
                nos[ch] = {"id": ch, "tipo": "pessoa", "rotulo": ch.lstrip("?"), "papeis": ["sem vínculo nos documentos"],
                           "assinante": True}
        return {"nos": list(nos.values()), "arestas": arestas}

    def _linha_do_tempo(self, pedido: Pedido) -> list[dict]:
        ev = []
        for a in self.kb.atos:
            ev.append({"data": a.data_efeito, "tipo": "ato", "titulo": a.titulo, "doc": a.doc_id,
                       "detalhe": "altera a administração" if a.altera_administracao else ""})
            for adm in a.administradores:
                fim = adm.termino or self._termino_mandato(adm, self.kb.atos)
                if fim:
                    ev.append({"data": fim, "tipo": "fim_mandato", "titulo": f"Fim do mandato de {self.nome(adm.pessoa)}",
                               "doc": a.doc_id, "detalhe": adm.prazo_descricao or ""})
        for p in self.kb.procuracoes:
            ev.append({"data": p.data, "tipo": "procuracao", "titulo": f"Procuração para {self.nomes(p.outorgados)}",
                       "doc": p.id, "detalhe": p.forma})
            fim = self._fim_procuracao(p)
            if fim:
                ev.append({"data": fim, "tipo": "vencimento", "titulo": f"Vence a procuração de {self.nomes(p.outorgados)}",
                           "doc": p.id, "detalhe": ""})
        for s in self.kb.substabelecimentos:
            ev.append({"data": s.data, "tipo": "substabelecimento",
                       "titulo": f"{self.nome(s.substabelecente)} substabelece a {self.nomes(s.substabelecidos)}",
                       "doc": s.id, "detalhe": s.reserva})
        for r in self.kb.revogacoes:
            ev.append({"data": r.data, "tipo": "revogacao", "titulo": "Revogação de procuração", "doc": r.id, "detalhe": ""})
        for d in self.kb.deliberacoes:
            ev.append({"data": d.data, "tipo": "deliberacao", "titulo": "Deliberação de sócios", "doc": d.id,
                       "detalhe": f"{d.percentual or 0:g}% do capital"})
        ev.append({"data": pedido.data_venda, "tipo": "venda", "titulo": "Data da venda (ATPV)", "doc": None,
                   "detalhe": _fmt_valor(pedido.valor)})
        return sorted([e for e in ev if e["data"]], key=lambda e: e["data"])


def regime_titular(motor: "Motor") -> list[str]:
    """Lado pessoa física: a chave do titular (a 'administração' sintética da titularidade)."""
    return [a.pessoa for ato in motor.kb.atos for a in ato.administradores]


def faixa_por_indice(indice: float, pol: Politica, forcar_amarelo: bool) -> Faixa:
    if forcar_amarelo:
        return Faixa.AMARELO
    if indice >= pol.limiar_aceite:
        return Faixa.VERDE
    if indice <= pol.limiar_recusa:
        return Faixa.VERMELHO
    return Faixa.AMARELO
