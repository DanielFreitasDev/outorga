import type { Faixa, Lado, Sev, Veredito } from "./types";

export function dataBR(iso: string | null | undefined): string {
  if (!iso) return "—";
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  if (!m) return iso;
  return `${m[3]}/${m[2]}/${m[1]}`;
}

export function dataHoraBR(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

export function moeda(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "valor não informado";
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export function cpfFmt(c: string | null | undefined): string {
  if (!c) return "";
  const d = c.replace(/\D/g, "");
  if (d.length === 11) return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9)}`;
  return c;
}

/** CPF (11 dígitos) ou CNPJ (14 dígitos) formatado; outro texto volta como veio. */
export function docFmt(c: string | null | undefined): string {
  if (!c) return "";
  const d = c.replace(/\D/g, "");
  if (d.length === 14) return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12)}`;
  return cpfFmt(c);
}

export function pct(v: number, casas = 0): string {
  return `${(v * 100).toFixed(casas).replace(".", ",")}%`;
}

export function hashCurto(h: string | null | undefined, n = 10): string {
  if (!h) return "—";
  return h.length > n * 2 ? `${h.slice(0, n)}…${h.slice(-4)}` : h;
}

export const FAIXA_TXT: Record<Faixa, string> = { VERDE: "Aceito", AMARELO: "Revisão humana", VERMELHO: "Recusado" };
export const FAIXA_LONGO: Record<Faixa, string> = {
  VERDE: "Aceito automaticamente",
  AMARELO: "Faixa intermediária — revisão humana",
  VERMELHO: "Recusado automaticamente",
};
export const VEREDITO_TXT: Record<Veredito, string> = { PODE: "Pode assinar", NAO_PODE: "Não pode assinar", INDETERMINADO: "Indeterminado" };

export const LADO_TXT: Record<Lado, string> = { vendedor: "Vendedor", comprador: "Comprador" };
export const LADO_LONGO: Record<Lado, string> = { vendedor: "Vendedor · antigo proprietário", comprador: "Comprador · novo proprietário" };
export const PF_FORA_ESCOPO = "pessoa física — assina em nome próprio (nada a comprovar)";

/** CPF mascarado para exibir dados do dono do veículo: ***.123.456-** */
export function cpfMascarado(c: string | null | undefined): string {
  const d = (c ?? "").replace(/\D/g, "");
  return d.length === 11 ? `***.${d.slice(3, 6)}.${d.slice(6, 9)}-**` : docFmt(c);
}

export const soDigitos = (s: string | null | undefined) => (s ?? "").replace(/\D/g, "");

/** Dígitos verificadores do CPF (mesma regra do backend). */
export function cpfValido(c: string | null | undefined): boolean {
  const d = soDigitos(c);
  if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false;
  for (const n of [9, 10]) {
    let soma = 0;
    for (let i = 0; i < n; i++) soma += Number(d[i]) * (n + 1 - i);
    const dv = ((soma * 10) % 11) % 10;
    if (dv !== Number(d[n])) return false;
  }
  return true;
}

/** Dígitos verificadores do CNPJ. */
export function cnpjValido(c: string | null | undefined): boolean {
  const d = soDigitos(c);
  if (d.length !== 14 || /^(\d)\1{13}$/.test(d)) return false;
  const calc = (n: number) => {
    const pesos = n === 12 ? [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2] : [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    const soma = pesos.reduce((acc, p, i) => acc + p * Number(d[i]), 0);
    const r = soma % 11;
    return r < 2 ? 0 : 11 - r;
  };
  return calc(12) === Number(d[12]) && calc(13) === Number(d[13]);
}

/** Nome de quem assina como veio no pedido; "CPF 000…" (sem nome informado) vira vazio. */
export function nomeInformado(n: string | null | undefined): string {
  return n && !/^CPF\s/.test(n) ? n : "";
}

export const PENDENCIA_TXT: Record<string, string> = {
  procuracao: "procuração",
  ato_constitutivo: "contrato social / estatuto",
  alteracoes: "alterações contratuais",
  valor: "valor da venda",
  ata_aprovacao: "ata de aprovação dos sócios",
  crlv: "CRLV",
};

export const SEV_TXT: Record<Sev, string> = { bloqueio: "Bloqueio", alerta: "Alerta", atencao: "Atenção", info: "Info", ok: "OK" };
export const SEV_ORDEM: Record<Sev, number> = { bloqueio: 0, alerta: 1, atencao: 2, info: 3, ok: 4 };

export const VIA_TXT: Record<string, string> = { contrato: "Contrato social", procuracao: "Procuração", substabelecimento: "Substabelecimento" };

export const ESCOPO_TXT: Record<string, string> = {
  geral: "Representação geral",
  alienacao_bens: "Alienação de bens",
  alienacao_bens_moveis: "Alienação de bens móveis",
  alienacao_veiculos: "Alienação de veículos",
  alienacao_ativo_imobilizado: "Ativo imobilizado / não circulante",
  alienacao_bens_imoveis: "Bens imóveis",
  onerar_bens: "Oneração de bens",
  veiculo_especifico: "Veículo específico",
  outorgar_procuracoes: "Outorga de procurações",
  obrigacoes_garantias: "Avais e garantias",
  outro: "Outro",
};

export const MODO_TXT: Record<string, string> = {
  isolado: "isoladamente",
  conjunto: "em conjunto",
  quantidade_minima: "número mínimo",
  misto: "combinações",
  nao_especificado: "não especificado",
};

export const TIPO_DOC_TXT: Record<string, string> = {
  contrato_social: "Contrato social",
  alteracao_contratual: "Alteração contratual",
  contrato_consolidado: "Contrato consolidado",
  estatuto_social: "Estatuto social",
  ato_constitutivo_slu: "Ato constitutivo (SLU)",
  requerimento_empresario: "Requerimento de empresário",
  ata_reuniao_socios: "Ata de reunião de sócios",
  ata_assembleia: "Ata de assembleia",
  ata_conselho: "Ata do Conselho",
  procuracao: "Procuração",
  substabelecimento: "Substabelecimento",
  revogacao_procuracao: "Revogação de procuração",
  crlv: "CRLV",
  atpv: "ATPV-e",
  outro: "Documento",
};

export const CATEGORIA_TXT: Record<string, string> = {
  administracao: "Administração e forma de assinar",
  alcada: "Alçada por valor",
  deliberacao: "Deliberação de sócios",
  bem_integralizado: "Carro integralizado ao capital (exemplo do áudio)",
  procuracao: "Procurações",
  substabelecimento: "Substabelecimento",
  forma: "Forma e idade da procuração",
  temporal: "Alterações e mandatos no tempo",
  estrutura: "Tipos societários",
  ocr: "Documentos escaneados (OCR)",
  comprador: "Comprador PJ — quem assina a compra",
  dois_lados: "PJ dos dois lados da ATPV-e",
  tipos: "Tipos de empresa — cooperativa, associação, MEI, EIRELI, sociedade simples",
  pf: "Consulta por CPF — pessoa física e procuração",
  pj: "Consulta por CPF — veículo de empresa",
  validacao_cega: "Validação cega — cenários novos, nunca usados no ajuste",
  validacao_independente: "Validação independente — casos escritos por outro autor, sem acesso ao código",
};

/** Rótulo curto para os filtros da Demonstração. */
export const CATEGORIA_CURTA: Record<string, string> = {
  bem_integralizado: "Carro integralizado ao capital",
  comprador: "Comprador PJ",
  dois_lados: "PJ dos dois lados",
  tipos: "Tipos de empresa",
  pf: "Consulta por CPF · pessoa física",
  pj: "Consulta por CPF · empresa",
  validacao_cega: "Validação cega",
  validacao_independente: "Validação independente",
};

export const CATEGORIA_ORDEM = ["bem_integralizado", "administracao", "alcada", "deliberacao", "procuracao", "substabelecimento",
  "forma", "temporal", "estrutura", "ocr", "comprador", "dois_lados", "tipos", "pf", "pj", "validacao_cega", "validacao_independente"];

export const TAREFA_TXT: Record<string, string> = {
  partes: "Identificando sócios, administradores e bens integralizados",
  regras: "Lendo as cláusulas de representação e assinatura",
  ata: "Lendo as deliberações da ata",
  procuracao: "Lendo outorgante, poderes, prazo e substabelecimento",
  substabelecimento: "Lendo o substabelecimento (origem e reserva)",
  revogacao: "Lendo a revogação",
  crlv: "Conferindo o proprietário no CRLV",
  atpv: "Lendo a ATPV-e (veículo, vendedor, comprador e assinaturas)",
  classificar: "Classificando o documento",
};

/** Hash determinístico simples (para jitter estável em gráficos). */
export function hash01(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ((h >>> 0) % 10000) / 10000;
}
