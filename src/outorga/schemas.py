"""Schemas de extração (saída estruturada do LLM).

Regras de desenho, aprendidas testando o Qwen local:
- a evidência literal vem ANTES da classificação em cada item (o modelo cita, depois decide);
- enums fechados para tudo que o motor de regras usa; texto livre só para exibição;
- datas como texto "AAAA-MM-DD" (o parser do motor é tolerante);
- o JSON Schema gerado é "achatado" (sem $ref) para a gramática do llama.cpp.
"""

from __future__ import annotations

import copy
from typing import Any, Literal

from pydantic import BaseModel, Field

TipoDocumento = Literal[
    "contrato_social", "alteracao_contratual", "contrato_consolidado", "estatuto_social", "ato_constitutivo_slu",
    "requerimento_empresario", "ata_reuniao_socios", "ata_assembleia", "ata_conselho", "termo_posse",
    "procuracao", "substabelecimento", "revogacao_procuracao", "crlv", "atpv", "certidao_junta", "outro",
]
TipoSocietario = Literal["LTDA", "SLU", "SA", "EI", "EIRELI", "SS", "COOPERATIVA", "OUTRO"]
Escopo = Literal[
    "geral", "alienacao_bens", "alienacao_bens_moveis", "alienacao_veiculos", "alienacao_ativo_imobilizado",
    "alienacao_bens_imoveis", "onerar_bens", "veiculo_especifico", "outorgar_procuracoes", "obrigacoes_garantias",
    "outro",
]
Modo = Literal["isolado", "conjunto", "quantidade_minima", "misto", "nao_especificado"]
Cargo = Literal["administradores", "diretores", "socios", "procuradores"]


class VeiculoRef(BaseModel):
    descricao: str | None = Field(None, description="marca/modelo como escrito")
    placa: str | None = None
    renavam: str | None = None
    chassi: str | None = None


class PessoaRef(BaseModel):
    nome: str
    cpf: str | None = None


# ------------------------------------------------------------------------------ classificação
class Classificacao(BaseModel):
    tipo: TipoDocumento
    titulo: str
    data_documento: str | None = Field(None, description="AAAA-MM-DD da assinatura/lavratura")
    confianca: float = Field(description="0 a 1")


# ------------------------------------------------------------------ atos societários: partes
class Prazo(BaseModel):
    tipo: Literal["indeterminado", "determinado", "nao_informado"]
    termino: str | None = Field(None, description="AAAA-MM-DD se for possível calcular")
    descricao: str | None = Field(None, description="texto literal do prazo")


class Administrador(BaseModel):
    evidencia: str = Field(description="trecho literal que designa a pessoa")
    nome: str
    cpf: str | None = None
    cargo: str = Field(description="ex.: sócio administrador, administrador não sócio, Diretor-Presidente")
    socio: bool
    prazo: Prazo


class Socio(BaseModel):
    nome: str
    cpf: str | None = None
    percentual: float | None = Field(None, description="participação no capital, 0-100")


class BemIntegralizado(BaseModel):
    evidencia: str
    socio_nome: str
    descricao: str
    veiculo: VeiculoRef | None = None


class DadosDocumento(BaseModel):
    tipo_detalhado: Literal["constituicao", "alteracao", "alteracao_e_consolidacao", "estatuto", "ato_constitutivo_slu",
                            "requerimento_empresario", "ata", "outro"]
    numero_alteracao: int | None = None
    data_assinatura: str | None = Field(None, description="AAAA-MM-DD")
    data_registro: str | None = Field(None, description="AAAA-MM-DD do registro na Junta, se houver")
    numero_registro: str | None = None


class DadosEmpresa(BaseModel):
    razao_social: str
    cnpj: str | None = None
    tipo_societario: TipoSocietario
    objeto_social: str
    comercializa_veiculos: bool = Field(description="o objeto inclui compra e venda/revenda de veículos?")


class AlteracaoAdministracao(BaseModel):
    altera_administracao: bool = Field(description="este documento muda quem administra ou como se assina?")
    resumo: str | None = None


class ExtracaoPartes(BaseModel):
    documento: DadosDocumento
    empresa: DadosEmpresa
    socios: list[Socio]
    administradores: list[Administrador]
    bens_integralizados: list[BemIntegralizado]
    alteracao: AlteracaoAdministracao


# ----------------------------------------------------------------- atos societários: regras
class Grupo(BaseModel):
    cargo: Cargo | None = None
    pessoa: str | None = None
    quantidade: int = 1


class Combinacao(BaseModel):
    descricao: str
    grupos: list[Grupo]


class Regra(BaseModel):
    evidencia: str = Field(description="trecho literal da cláusula")
    clausula: str | None = Field(None, description="ex.: Cláusula Sétima, Parágrafo único")
    expressao_modo: str | None = Field(None, description="expressão literal que define a forma de assinar")
    escopo: Escopo
    veiculo: VeiculoRef | None = Field(None, description="só para escopo veiculo_especifico")
    efeito: Literal["autoriza", "restringe", "veda"]
    modo: Modo
    pessoas: list[str] = Field(description="nomes citados na regra")
    cargo: Cargo | None = None
    quantidade_minima: int | None = None
    combinacoes: list[Combinacao] = Field(description="só quando modo = misto")
    valor_acima_de: float | None = None
    valor_ate: float | None = None
    exige_aprovacao_socios: bool
    quorum_percentual: float | None = Field(None, description="ex.: 75 para três quartos; 50.01 para mais da metade")
    exige_anuencia_de: list[str]


class RegrasProcuracao(BaseModel):
    evidencia: str | None = None
    prazo_maximo_meses: int | None = None
    exige_poderes_especificados: bool
    vedada_para_alienacao: bool


class ExtracaoRegras(BaseModel):
    regras: list[Regra]
    regras_procuracao: RegrasProcuracao


# ------------------------------------------------------------------------------------- atas
class Eleito(BaseModel):
    nome: str
    cpf: str | None = None
    cargo: str
    mandato_descricao: str | None = None
    mandato_termino: str | None = Field(None, description="AAAA-MM-DD se calculável")


class Deliberacao(BaseModel):
    evidencia: str
    assunto: str
    tipo: Literal["aprova_alienacao_veiculo", "eleicao_administradores", "outro"]
    aprovada: bool
    percentual_favoravel: float | None = Field(None, description="% do capital que votou a favor")
    veiculos: list[VeiculoRef]
    valor_minimo: float | None = None
    eleitos: list[Eleito]


class ExtracaoAta(BaseModel):
    data: str | None = Field(None, description="AAAA-MM-DD")
    orgao: Literal["reuniao_socios", "assembleia_socios", "assembleia_acionistas", "conselho_administracao", "outro"]
    presentes: list[Socio]
    deliberacoes: list[Deliberacao]


# -------------------------------------------------------------------------------- procuração
class Outorgante(BaseModel):
    evidencia: str
    tipo: Literal["PJ", "PF"]
    nome: str
    documento: str | None = Field(None, description="CNPJ ou CPF")
    representantes: list[PessoaRef] = Field(description="quem assinou pela PJ")
    age_em_nome_da_empresa: bool = Field(description="pessoa física que declara agir como administrador EM NOME da empresa")


class Poderes(BaseModel):
    evidencia: str = Field(description="trecho literal com os poderes")
    alienar_veiculos: bool = Field(description="pode vender/alienar/transferir veículos?")
    assinar_atpv: bool
    poderes_especiais_expressos: bool
    apenas_administracao_geral: bool = Field(description="só poderes gerais de administração, sem poder de alienar")
    abrangencia: Literal["todos_veiculos_da_outorgante", "veiculos_especificos", "nao_aplicavel"]
    veiculos: list[VeiculoRef]
    bens_do_proprio_outorgante: bool = Field(description="fala de bens 'de propriedade do outorgante' pessoa física")
    exige_conjunto_com: Literal["nenhum", "diretor", "administrador", "outro_procurador", "outro"]


class Validade(BaseModel):
    evidencia: str | None = None
    tipo: Literal["indeterminado", "ate_data", "prazo", "nao_informado"]
    data_fim: str | None = Field(None, description="AAAA-MM-DD")
    prazo_texto: str | None = None


class Substab(BaseModel):
    evidencia: str | None = None
    regra: Literal["permitido_com_reserva", "permitido_sem_reserva", "permitido", "vedado", "omisso"]


class ExtracaoProcuracao(BaseModel):
    forma: Literal["publica", "particular"]
    cartorio: str | None = None
    livro: str | None = None
    folhas: str | None = None
    data_outorga: str | None = Field(None, description="AAAA-MM-DD")
    firma_reconhecida: bool | None = None
    outorgante: Outorgante
    outorgados: list[PessoaRef]
    atuacao_outorgados: Literal["isolada", "conjunta", "nao_especificada"]
    poderes: Poderes
    validade: Validade
    substabelecimento: Substab
    irrevogavel: bool
    em_causa_propria: bool


class RefProcuracao(BaseModel):
    data: str | None = Field(None, description="AAAA-MM-DD da procuração de origem")
    cartorio: str | None = None
    livro: str | None = None
    folhas: str | None = None
    outorgante_nome: str | None = None
    outorgado_nome: str | None = None


class ExtracaoSubstabelecimento(BaseModel):
    evidencia: str
    forma: Literal["publica", "particular"]
    data: str | None = Field(None, description="AAAA-MM-DD")
    firma_reconhecida: bool | None = None
    procuracao_origem: RefProcuracao
    substabelecente: PessoaRef
    substabelecidos: list[PessoaRef]
    reserva: Literal["com_reserva", "sem_reserva", "nao_informado"]
    todos_os_poderes: bool
    alienar_veiculos: bool


class ExtracaoRevogacao(BaseModel):
    evidencia: str
    forma: Literal["publica", "particular"]
    data: str | None = Field(None, description="AAAA-MM-DD")
    revogante: Outorgante
    procuracao_revogada: RefProcuracao


class ExtracaoCRLV(BaseModel):
    placa: str
    renavam: str | None = None
    chassi: str | None = None
    marca_modelo: str | None = None
    ano_fabricacao: int | None = None
    ano_modelo: int | None = None
    proprietario_nome: str
    proprietario_documento: str | None = Field(None, description="CPF ou CNPJ")


class ParteATPV(BaseModel):
    tipo: Literal["PJ", "PF"]
    nome: str
    documento: str | None = Field(None, description="CNPJ ou CPF")


class AssinaturaATPV(BaseModel):
    nome: str
    cpf: str | None = None
    lado: Literal["vendedor", "comprador"]


class ExtracaoATPV(BaseModel):
    numero: str | None = None
    placa: str | None = None
    renavam: str | None = None
    chassi: str | None = None
    marca_modelo: str | None = None
    valor: float | None = Field(None, description="valor declarado da venda")
    data: str | None = Field(None, description="AAAA-MM-DD da venda/emissão")
    vendedor: ParteATPV
    comprador: ParteATPV
    assinaturas: list[AssinaturaATPV] = Field(description="assinaturas eletrônicas já registradas, se houver")


# --------------------------------------------------------------------------- JSON Schema plano
def schema_plano(model: type[BaseModel]) -> dict[str, Any]:
    """JSON Schema sem $ref/$defs/títulos — formato aceito pela gramática do llama.cpp e por APIs."""
    bruto = model.model_json_schema()
    defs = bruto.pop("$defs", {})

    def resolver(no: Any) -> Any:
        if isinstance(no, dict):
            if "$ref" in no:
                return resolver(copy.deepcopy(defs[no["$ref"].split("/")[-1]]))
            out = {}
            for k, v in no.items():
                if k in ("title", "default"):
                    continue
                out[k] = resolver(v)
            if out.get("type") == "object" and "properties" in out:
                out["required"] = list(out["properties"])  # tudo obrigatório: menos ambiguidade
                out["additionalProperties"] = False
            return out
        if isinstance(no, list):
            return [resolver(x) for x in no]
        return no

    return resolver(bruto)
