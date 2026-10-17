"""Modelo de domínio normalizado — o que o motor de regras enxerga depois da leitura dos documentos.

Tudo aqui já está "resolvido": pessoas viraram chaves canônicas (CPF ou nome normalizado), datas
viraram `date`, e cada fato carrega a `Fonte` (documento, cláusula, trecho literal e ancoragem).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date
from enum import Enum
from typing import Any


class Severidade(str, Enum):
    BLOQUEIO = "bloqueio"  # invalida um caminho de assinatura (ou o caso todo, se global)
    ALERTA = "alerta"      # exige revisão humana se afetar a decisão (força a faixa intermediária)
    ATENCAO = "atencao"    # reduz a confiança, não força revisão
    INFO = "info"          # explicação
    OK = "ok"              # verificação que passou


ORDEM_SEV = {Severidade.OK: 0, Severidade.INFO: 0, Severidade.ATENCAO: 1, Severidade.ALERTA: 2, Severidade.BLOQUEIO: 3}


class Veredito(str, Enum):
    PODE = "PODE"
    NAO_PODE = "NAO_PODE"
    INDETERMINADO = "INDETERMINADO"


class Faixa(str, Enum):
    VERDE = "VERDE"        # aceito
    AMARELO = "AMARELO"    # faixa intermediária — revisão humana
    VERMELHO = "VERMELHO"  # recusado


@dataclass
class Fonte:
    doc_id: str
    doc_titulo: str
    trecho: str | None = None
    clausula: str | None = None
    ancoragem: float | None = None  # 0-100: quanto o trecho citado bate com o texto original
    pagina: int | None = None
    inicio: int | None = None
    fim: int | None = None


@dataclass
class Pessoa:
    chave: str
    nome: str
    cpf: str | None = None
    aliases: set[str] = field(default_factory=set)


@dataclass
class VeiculoId:
    descricao: str | None = None
    placa: str | None = None
    renavam: str | None = None
    chassi: str | None = None


@dataclass
class Administrador:
    pessoa: str
    cargo: str
    socio: bool
    inicio: date | None
    termino: date | None
    prazo_descricao: str | None
    fonte: Fonte


@dataclass
class Grupo:
    cargo: str | None = None          # administradores | diretores | socios | procuradores
    pessoas: list[str] = field(default_factory=list)
    quantidade: int = 1


@dataclass
class Verificacao:
    """Resultado da conferência léxica de um fato extraído pelo LLM."""
    campo: str
    valor_llm: Any
    valor_lexico: Any
    divergiu: bool
    corrigido_para: Any = None
    expressoes: list[str] = field(default_factory=list)


@dataclass
class RegraRep:
    id: str
    escopo: str
    efeito: str
    modo: str
    pessoas: list[str]
    cargo: str | None
    quantidade_minima: int | None
    combinacoes: list[list[Grupo]]
    veiculo: VeiculoId | None
    valor_acima_de: float | None
    valor_ate: float | None
    exige_aprovacao_socios: bool
    quorum_percentual: float | None
    exige_anuencia_de: list[str]
    fonte: Fonte
    verificacoes: list[Verificacao] = field(default_factory=list)
    confianca: float = 1.0
    atos: set[str] = field(default_factory=lambda: {"alienar"})   # "alienar" (vendedor) e/ou "adquirir" (comprador)
    nivel_aquisicao: int | None = None                          # especialidade da regra no ato de adquirir
    substitutos: list[str] = field(default_factory=list)        # cargos que só assinam na ausência/impedimento do titular

    @property
    def define_assinantes(self) -> bool:
        return self.modo != "nao_especificado" or bool(self.pessoas) or bool(self.combinacoes)


@dataclass
class RegrasProcuracaoEmpresa:
    prazo_maximo_meses: int | None = None
    exige_poderes_especificados: bool = False
    vedada_para_alienacao: bool = False
    fonte: Fonte | None = None


@dataclass
class BemIntegralizado:
    socio: str
    descricao: str
    veiculo: VeiculoId | None
    fonte: Fonte


@dataclass
class AtoSocietario:
    doc_id: str
    titulo: str
    tipo: str                  # constituicao | alteracao | alteracao_e_consolidacao | estatuto | ...
    data_assinatura: date | None
    data_registro: date | None
    numero_alteracao: int | None
    consolida: bool
    altera_administracao: bool
    administradores: list[Administrador]
    socios: dict[str, float]
    regras: list[RegraRep]
    regras_procuracao: RegrasProcuracaoEmpresa | None
    bens: list[BemIntegralizado]
    eleicao: bool = False      # ata que elege diretoria (S.A.)
    # cláusulas do texto que exigem aprovação prévia para vender/comprar bens que alcançam veículos (sentinela de leitura)
    restricoes_texto: list = field(default_factory=list)

    @property
    def data_efeito(self) -> date | None:
        """Lei 8.934/94, art. 36: arquivado em até 30 dias, retroage à data da assinatura."""
        if self.data_assinatura and (self.data_registro is None or (self.data_registro - self.data_assinatura).days <= 30):
            return self.data_assinatura
        return self.data_registro or self.data_assinatura


@dataclass
class Procuracao:
    id: str
    titulo: str
    forma: str
    cartorio: str | None
    livro: str | None
    folhas: str | None
    data: date | None
    firma_reconhecida: bool | None
    outorgante_tipo: str
    outorgante_nome: str
    outorgante_doc: str | None
    outorgante_e_empresa: bool
    representantes: list[str]
    age_em_nome_da_empresa: bool
    outorgados: list[str]
    atuacao: str
    alienar_veiculos: bool
    assinar_atpv: bool
    especiais: bool
    apenas_gerais: bool
    abrangencia: str
    veiculos: list[VeiculoId]
    bens_do_proprio_outorgante: bool
    exige_conjunto_com: str
    validade_tipo: str
    validade_fim: date | None
    prazo_texto: str | None
    substabelecimento: str
    irrevogavel: bool
    em_causa_propria: bool
    fontes: dict[str, Fonte]
    verificacoes: list[Verificacao] = field(default_factory=list)
    confianca: float = 1.0
    alteracoes_citadas: list[int] = field(default_factory=list)  # "nos termos da Terceira Alteração..."
    adquirir_veiculos: bool = False                             # poder expresso de comprar/adquirir veículos


@dataclass
class Substabelecimento:
    id: str
    titulo: str
    forma: str
    data: date | None
    firma_reconhecida: bool | None
    origem: dict[str, Any]
    procuracao_id: str | None
    origem_sub_id: str | None
    substabelecente: str
    substabelecidos: list[str]
    reserva: str
    todos_os_poderes: bool
    alienar_veiculos: bool
    fonte: Fonte
    verificacoes: list[Verificacao] = field(default_factory=list)
    confianca: float = 1.0


@dataclass
class Revogacao:
    id: str
    titulo: str
    forma: str
    data: date | None
    revogante_nome: str
    representantes: list[str]
    origem: dict[str, Any]
    procuracao_ids: list[str]
    fonte: Fonte
    generica: bool = False
    confianca: float = 1.0


@dataclass
class DeliberacaoSocios:
    id: str
    data: date | None
    tipo: str
    aprovada: bool
    percentual: float | None
    veiculos: list[VeiculoId]
    valor_minimo: float | None
    fonte: Fonte
    confianca: float = 1.0


@dataclass
class Empresa:
    razao_social: str
    cnpj: str | None
    tipo: str
    objeto: str
    comercializa_veiculos: bool
    subtipo: str | None = None   # "MEI", "EIRELI", "COOPERATIVA", "ASSOCIACAO", "FUNDACAO", "SS"


@dataclass
class CRLV:
    placa: str | None
    renavam: str | None
    chassi: str | None
    marca_modelo: str | None
    proprietario_nome: str | None
    proprietario_doc: str | None
    fonte: Fonte


@dataclass
class DocumentoInfo:
    id: str
    titulo: str
    tipo: str
    arquivo: str
    paginas: int
    ocr: bool
    ocr_confianca: float | None
    data: date | None


@dataclass
class BaseConhecimento:
    empresa: Empresa
    pessoas: dict[str, Pessoa]
    atos: list[AtoSocietario]
    procuracoes: list[Procuracao]
    substabelecimentos: list[Substabelecimento]
    revogacoes: list[Revogacao]
    deliberacoes: list[DeliberacaoSocios]
    crlv: CRLV | None
    documentos: dict[str, DocumentoInfo]
    avisos: list[str] = field(default_factory=list)
    titular_fonte: str | None = None   # proprietário conferido na base veicular (dispensa o CRLV)

    def nome(self, chave: str) -> str:
        p = self.pessoas.get(chave)
        return p.nome if p else chave


@dataclass
class Assinante:
    nome: str
    cpf: str | None = None


@dataclass
class Parte:
    """Um lado da ATPV-e (antigo ou novo proprietário)."""
    tipo: str                    # "PJ" | "PF"
    nome: str | None = None
    documento: str | None = None  # CNPJ ou CPF
    assinantes: list[Assinante] = field(default_factory=list)


@dataclass
class Pedido:
    """Pedido visto por UM lado: `lado` diz quem está sendo verificado (vendedor aliena; comprador adquire)."""
    veiculo: VeiculoId
    data_venda: date
    valor: float | None
    assinantes: list[Assinante]
    forma_assinatura: str = "ATPV-e"
    comprador: str | None = None
    vendedor_cnpj: str | None = None   # CNPJ da empresa verificada (nome mantido por compatibilidade)
    lado: str = "vendedor"             # "vendedor" | "comprador"
    consulta: bool = False             # consulta por CPF antes da ATPV-e: sem procuração, pergunta por ela antes de recusar


@dataclass
class PedidoATPV:
    """Os dois lados da ATPV-e. A verificação de poderes roda para cada lado que for pessoa jurídica."""
    veiculo: VeiculoId
    data_venda: date
    valor: float | None
    vendedor: Parte
    comprador: Parte
    forma_assinatura: str = "ATPV-e"
    origem: str = "informado"          # "informado" | "ATPV-e" (dados lidos da própria ATPV-e)
    alvo: str | None = None            # consulta por CPF (antes da ATPV-e): só o lado de quem vai assinar
    titular_fonte: str | None = None   # de onde veio o proprietário: "base veicular" | "CRLV" | "ATPV-e" | "informado"

    def lado(self, qual: str) -> Pedido:
        p = self.vendedor if qual == "vendedor" else self.comprador
        return Pedido(self.veiculo, self.data_venda, self.valor, list(p.assinantes), self.forma_assinatura,
                      self.comprador.nome, p.documento, qual, self.alvo is not None)


def fator_ancoragem(score: float | None) -> float:
    """Converte a ancoragem (0-100) de uma citação em fator de confiança (0.3-1.0)."""
    if score is None:
        return 0.7
    if score >= 95:
        return 1.0
    if score >= 80:
        return 0.85 + (score - 80) / 15 * 0.15
    if score >= 60:
        return 0.55 + (score - 60) / 20 * 0.30
    return 0.3


def para_json(obj: Any) -> Any:
    """Serializa dataclasses/enums/datas/sets para JSON."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: para_json(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): para_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [para_json(v) for v in obj]
    return obj
