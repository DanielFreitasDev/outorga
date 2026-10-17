// Contrato da API do Outorga (ver src/outorga/api.py e pipeline.serializar). Campos podem ganhar adições.

export type Faixa = "VERDE" | "AMARELO" | "VERMELHO";
export type Veredito = "PODE" | "NAO_PODE" | "INDETERMINADO";
export type Sev = "bloqueio" | "alerta" | "atencao" | "info" | "ok";
/** Lado da ATPV-e: vendedor (antigo proprietário) ou comprador (novo proprietário). */
export type Lado = "vendedor" | "comprador";
export const LADOS: Lado[] = ["vendedor", "comprador"];

export interface Fonte {
  doc_id: string;
  doc_titulo: string;
  trecho: string | null;
  clausula: string | null;
  ancoragem: number | null;
  pagina: number | null;
  inicio: number | null;
  fim: number | null;
}

export interface Achado {
  codigo: string;
  severidade: Sev;
  titulo: string;
  detalhe: string;
  fundamento: string[];
  fontes: (Fonte | null)[];
  caminho: string | null;
}

export interface Precondicao {
  codigo: string;
  descricao: string;
  quorum: number | null;
  satisfeita: boolean | null;
  detalhe: string;
  fontes: Fonte[];
}

export interface PessoaRef { chave: string; nome: string }

export interface Alternativa {
  id: string;
  pessoas: PessoaRef[];
  via: "contrato" | "procuracao" | "substabelecimento";
  descricao: string;
  cadeia: string[];
  severidade: Sev;
  confianca: number;
  achados: Achado[];
  precondicoes: Precondicao[];
}

export interface Verificacao {
  campo: string;
  valor_llm: unknown;
  valor_lexico: unknown;
  divergiu: boolean;
  corrigido_para: unknown;
  expressoes: string[];
}

export interface RegraAvaliada {
  regra: string;
  escopo: string;
  aplicavel: boolean | null;
  motivo: string;
  so_condicao: boolean;
  fonte: Fonte | null;
  modo: string | null;
  pessoas: string[];
  cargo: string | null;
  valor_acima_de: number | null;
  confianca: number | null;
  verificacoes: Verificacao[];
  decisiva: boolean;
}

export interface NoGrafo {
  id: string;
  tipo: "empresa" | "veiculo" | "pessoa";
  rotulo: string;
  sub?: string;
  papeis?: string[];
  assinante?: boolean;
}

export interface ArestaGrafo {
  de: string;
  para: string;
  tipo: "propriedade" | "socio" | "administracao" | "procuracao" | "substabelecimento" | "clausula" | string;
  rotulo?: string;
  status: "valido" | "invalido" | "alerta" | "neutro";
  doc?: string;
  motivo?: string | null;
}

export interface EventoTempo {
  data: string;
  tipo: "ato" | "venda" | "procuracao" | "vencimento" | "fim_mandato" | "substabelecimento" | "deliberacao" | "revogacao" | string;
  titulo: string;
  doc: string | null;
  detalhe: string;
}

export interface DocumentoRes {
  id: string;
  nome: string;
  tipo: string;
  titulo: string;
  data: string | null;
  paginas: string[];
  metodo: string;
  ocr_confianca: number | null;
  sha256: string;
  leitura: Record<string, unknown>;
}

export interface Comprovacao {
  norma: string;
  status: "comprovada" | "pendente" | "não comprovada" | string;
  /** Outorgante (PJ) ou titular pessoa física (tipo "PF": `cpf` e `titularidade` — onde o dono foi conferido). */
  outorgante: {
    nome: string; cnpj: string | null; tipo: string; atos_vigentes: { titulo: string; doc: string; efeito: string | null }[];
    cpf?: string | null; documento?: string | null; titularidade?: string | null;
  };
  outorgado: { nome: string; cpf: string | null; identificacao: string; qualidade: string }[];
  poderes_conferidos: string[];
  prazo_validade: string[];
  revogacao: string[];
  fontes: Fonte[];
  documentos_verificaveis: { id: string; titulo: string; arquivo: string }[];
}

export interface ParteATPV {
  tipo: "PJ" | "PF";
  nome: string | null;
  documento: string | null;
  assinantes: { nome: string; cpf: string | null }[];
}

/** Pedido completo da ATPV-e (o informado, completado com a leitura da própria ATPV-e). */
export interface PedidoATPV {
  veiculo: { descricao: string | null; placa: string | null; renavam: string | null; chassi: string | null };
  data_venda: string | null;
  valor: number | null;
  vendedor: ParteATPV;
  comprador: ParteATPV;
  forma_assinatura: string;
  /** "informado" | "ATPV-e" | "consulta por CPF" */
  origem: string;
  /** Consulta por CPF (antes da ATPV-e): o lado de quem vai assinar — só ele é verificado. */
  alvo?: Lado | null;
  /** De onde veio o proprietário: "base veicular" | "CRLV" | "informado". */
  titular_fonte?: string | null;
}

/** O que falta pedir a quem está no balcão (a tela usa isto para "perguntar"). */
export type TipoPendencia = "procuracao" | "ato_constitutivo" | "alteracoes" | "valor" | "ata_aprovacao" | "crlv";
export interface Pendencia { tipo: TipoPendencia | string; mensagem: string; lado?: Lado }

/** Proprietário de um veículo na base veicular (no protótipo, simulada) — GET /api/veiculo. */
export interface VeiculoBase {
  placa: string;
  renavam: string | null;
  chassi: string | null;
  marca_modelo: string | null;
  ano_modelo?: number | null;
  proprietario: { tipo: "PJ" | "PF"; nome: string; documento: string };
  fonte?: string;
}

/** Resultado combinado quando há PJ dos dois lados: o lado mais fraco decide. */
export interface Geral {
  veredito: Veredito;
  faixa: Faixa;
  indice: number;
  resumo: string;
  motivos_faixa: string[];
  lados: Lado[];
}

export interface Resultado {
  versao: string;
  gerado_em: string;
  pedido: {
    veiculo: { descricao: string | null; placa: string | null; renavam: string | null; chassi: string | null };
    data_venda: string;
    valor: number | null;
    assinantes: { nome: string; cpf: string | null }[];
    forma_assinatura?: string;
    comprador?: string | null;
    vendedor_cnpj?: string | null;
    lado?: Lado;
  };
  /** Parte verificada: empresa ou, com tipo "PF", a pessoa física titular (nome em `razao_social`, CPF em `cpf`). */
  empresa: { razao_social: string; cnpj: string | null; tipo: string; objeto: string; comercializa_veiculos: boolean;
    subtipo?: string | null; cpf?: string | null };
  veredito: Veredito;
  faixa: Faixa;
  indice: number;
  confianca: number;
  componentes: Record<string, number>;
  motivos_faixa: string[];
  resumo: string;
  assinantes: { informado: string; cpf: string | null; chave: string; nome: string; criterio: string }[];
  quem_pode: Alternativa[];
  caminhos_invalidos: Alternativa[];
  caminho_escolhido: Alternativa | null;
  faltantes: { alternativa: string; via: string; descricao: string; pessoas: string[]; faltam: string[]; faltam_nomes: string[]; pessoas_nomes: string[] }[];
  achados: Achado[];
  regras: RegraAvaliada[];
  precondicoes: Precondicao[];
  regime: {
    data: string;
    atos: { doc: string; titulo: string; efeito: string | null }[];
    administradores: { chave: string; nome: string; cargo: string; doc: string }[];
    encerrados: { nome: string; motivo: string }[];
    socios: { chave: string; nome: string; percentual: number }[];
  };
  grafo: { nos: NoGrafo[]; arestas: ArestaGrafo[] };
  linha_do_tempo: EventoTempo[];
  pessoas: Record<string, { nome: string; cpf: string | null }>;
  comprovacao_poderes?: Comprovacao;
  documentos: DocumentoRes[];
  avisos: string[];
  meta: Record<string, unknown>;
  hash_entrada?: string;
  auditoria?: { hash: string };
  /** Lado verificado neste resultado (o resultado de topo é o lado principal: vendedor PJ, senão comprador). */
  lado?: Lado;
  /** Resultado completo de cada lado PJ verificado. */
  lados?: Partial<Record<Lado, Resultado>>;
  geral?: Geral;
  pedido_atpv?: PedidoATPV;
  /** O que falta (procuração, contrato social, valor…) — por lado e, no topo, de todos os lados. */
  pendencias?: Pendencia[];
}

export interface Politica {
  nome: string;
  uf: string | null;
  perfil: "ce" | "generica" | string;
  idade_max_procuracao_dias: number;
  idade_max_severidade: Sev;
  procuracao_particular_com_firma: Sev;
  procuracao_particular_sem_firma: Sev;
  substabelecimento_particular: Sev;
  procuracao_sem_veiculo_identificado: Sev;
  crlv_ausente: Sev;
  quorum_padrao_deliberacao: number;
  limiar_aceite: number;
  limiar_recusa: number;
}

export interface Saude {
  versao: string;
  provedor: string;
  modelo: string;
  llm_disponivel: boolean;
  /** "IA local · qwen3.8-27b", "OpenAI · <modelo>", "Anthropic (Claude) · <modelo>", "sem IA (demonstração)" */
  rotulo_ia?: string;
  /** demonstração pública: envio de documentos e mudanças de política desativados */
  demonstracao?: boolean;
  fila: number;
  politica: Politica;
}

export interface Esperado {
  veredito: Veredito;
  faixas_aceitaveis: Faixa[];
  conjuntos_minimos: string[][] | null;
  conjuntos_minimos_nomes?: string[][] | null;
  fundamentos: string[];
}

export interface CasoDemo {
  id: string;
  titulo: string;
  categoria: string;
  objetivo: string;
  empresa: string;
  documentos: string[];
  esperado: Esperado;
  esperado_ce: Esperado | null;
  /** Lote ATPV-e: o esperado de cada lado PJ. */
  esperado_lados?: Partial<Record<Lado, Esperado>>;
  precalculado: boolean;
}

export interface AnaliseResumo {
  id: string;
  criado_em: string;
  status: "processando" | "concluida" | "erro" | string;
  origem: string;
  caso_demo: string | null;
  empresa: string | null;
  placa: string | null;
  veredito: Veredito | null;
  faixa: Faixa | null;
  indice: number | null;
  provedor: string | null;
  politica: string | null;
  duracao_s: number | null;
  revisao: string | null;
}

export interface EventoAgente {
  seq: number;
  tipo: string;
  t: number;
  [k: string]: unknown;
}

export interface AnaliseCompleta extends Omit<AnaliseResumo, "revisao"> {
  atualizado_em: string;
  cnpj: string | null;
  erro: string | null;
  pedido: Record<string, unknown>;
  resultado: Resultado | null;
  revisoes: { id: number; criado_em: string; revisor: string; decisao: string; justificativa: string }[];
  eventos: EventoAgente[];
}

export interface PontoCurva { limiar: number; cobertura: number; decididos: number; erros: number; risco: number; risco_sup: number }

export interface ItemCalibracao {
  caso: string;
  titulo?: string;
  categoria?: string;
  indice: number;
  previsto: Veredito;
  esperado: Veredito;
  faixa?: Faixa;
  fonte: "corpus" | "revisao" | string;
}

export interface Sugestao {
  aceite: PontoCurva | null;
  recusa: PontoCurva | null;
  curva_aceite: PontoCurva[];
  curva_recusa: PontoCurva[];
}

export interface Calibracao {
  run: string | null;
  itens: ItemCalibracao[];
  alfa: number;
  sugestao: Sugestao | null;
  sugestao_conservadora: Sugestao | null;
  atual: { limiar_aceite: number; limiar_recusa: number };
}

export interface RegistroAuditoria {
  seq: number;
  criado_em: string;
  tipo: string;
  analise_id: string | null;
  payload_hash: string;
  hash_anterior: string;
  hash: string;
  resumo: string;
}

export interface Auditoria {
  cadeia: { registros: number; integra: boolean; quebra_em: number | null; ultimo_hash: string };
  registros: RegistroAuditoria[];
}

export interface ResumoAvaliacao {
  run: string;
  modo: "oraculo" | "llm" | string;
  casos: number;
  duracao_s: number;
  data: string;
  veredito_correto: number;
  faixa_aceitavel: number;
  quem_pode_correto: number;
  quem_pode_avaliados: number;
  erros_perigosos: number;
  erros_caros: number;
  cobertura_automatica: number;
  acerto_na_faixa_automatica: number | null;
  politica: { nome?: string; limiar_aceite: number; limiar_recusa: number };
}

export interface SimulacaoLado {
  veredito: Veredito;
  faixa: Faixa;
  indice: number;
  resumo: string;
  assinantes: Resultado["assinantes"];
  quem_pode: Alternativa[];
  faltantes: Resultado["faltantes"];
  caminho_escolhido: Alternativa | null;
  comprovacao_poderes?: Comprovacao;
  motivos_faixa: string[];
  achados?: Achado[];
  caminhos_invalidos?: Alternativa[];
  lado?: Lado;
}

export interface Simulacao extends SimulacaoLado {
  geral?: Geral | null;
  lados?: Partial<Record<Lado, SimulacaoLado>>;
}

/** Leitura de uma ATPV-e enviada para pré-preencher o pedido (POST /api/atpv/ler). */
export interface LeituraATPV {
  metodo: "regex" | "llm" | string;
  atpv: {
    numero: string | null;
    placa: string | null;
    renavam: string | null;
    chassi: string | null;
    marca_modelo: string | null;
    valor: number | null;
    data: string | null;
    vendedor: { tipo: "PJ" | "PF"; nome: string; documento: string | null };
    comprador: { tipo: "PJ" | "PF"; nome: string; documento: string | null };
    assinaturas: { nome: string; cpf: string | null; lado: Lado }[];
  };
}

/** Consulta de exemplo (corpus fictício) para preencher a tela de consulta por CPF. */
export interface ExemploConsulta {
  id: string;
  titulo: string;
  placa: string;
  papel: "vender" | "comprar";
  cpf: string;
  nome: string;
  comprador: { tipo: "PF" | "PJ"; nome: string; documento: string } | null;
  valor: number | null;
  documentos: string[];
  esperado: string;
}
