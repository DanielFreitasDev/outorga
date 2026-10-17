import type {
  AnaliseCompleta, AnaliseResumo, Auditoria, Calibracao, CasoDemo, Lado, LeituraATPV, Politica, Resultado, ResumoAvaliacao, Saude,
  Simulacao, VeiculoBase,
} from "./types";

export class ErroApi extends Error {
  status: number;
  constructor(status: number, mensagem: string) {
    super(mensagem);
    this.status = status;
  }
}

async function pedir<T>(url: string, init?: RequestInit): Promise<T> {
  let r: Response;
  try {
    r = await fetch(url, init);
  } catch {
    throw new ErroApi(0, "Sem conexão com a API do Outorga (http://127.0.0.1:8765).");
  }
  if (!r.ok) {
    let msg = `${r.status} ${r.statusText}`;
    try {
      const j = await r.json();
      if (j && typeof j.detail === "string") msg = j.detail;
    } catch {
      /* corpo não é JSON */
    }
    throw new ErroApi(r.status, msg);
  }
  return (await r.json()) as T;
}

const json = (corpo: unknown, metodo = "POST"): RequestInit => ({
  method: metodo,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(corpo),
});

export const api = {
  saude: () => pedir<Saude>("/api/saude"),
  demo: () => pedir<CasoDemo[]>("/api/demo"),
  precalculado: (caso: string) => pedir<{ run: string; resultado: Resultado }>(`/api/demo/${caso}/precalculado`),
  analisarDemo: (caso: string, amostras = 1) =>
    pedir<{ id: string }>(`/api/demo/${caso}/analisar?amostras=${amostras}`, { method: "POST" }),
  novaAnalise: (arquivos: File[], pedido: unknown) => {
    const fd = new FormData();
    arquivos.forEach((a) => fd.append("arquivos", a, a.name));
    fd.append("pedido", JSON.stringify(pedido));
    return pedir<{ id: string }>("/api/analises", { method: "POST", body: fd });
  },
  analises: () => pedir<AnaliseResumo[]>("/api/analises"),
  analise: (id: string) => pedir<AnaliseCompleta>(`/api/analises/${id}`),
  reprocessar: (id: string) => pedir<Resultado>(`/api/analises/${id}/reprocessar`, { method: "POST" }),
  /** Proprietário pela placa/RENAVAM (base veicular; no protótipo, simulada). 404 = não encontrado. */
  veiculo: (placa: string, renavam: string) => {
    const q = new URLSearchParams();
    if (placa.trim()) q.set("placa", placa.trim().toUpperCase());
    if (renavam.trim()) q.set("renavam", renavam.trim());
    return pedir<VeiculoBase>(`/api/veiculo?${q}`);
  },
  lerAtpv: (arquivo: File) => {
    const fd = new FormData();
    fd.append("arquivo", arquivo, arquivo.name);
    return pedir<LeituraATPV>("/api/atpv/ler", { method: "POST", body: fd });
  },
  simular: (id: string, corpo: {
    lado?: Lado; assinantes: { nome: string; cpf: string | null }[]; valor?: number | null; data_venda?: string;
  }) => pedir<Simulacao>(`/api/analises/${id}/simular`, json(corpo)),
  revisar: (id: string, corpo: { decisao: "aprovar" | "recusar"; justificativa: string; revisor: string }) =>
    pedir<{ ok: boolean; hash: string }>(`/api/analises/${id}/revisao`, json(corpo)),
  politica: () => pedir<Politica>("/api/politica"),
  salvarPolitica: (p: Partial<Politica>) => pedir<Politica>("/api/politica", json(p, "PUT")),
  calibracao: (alfa = 0.05) => pedir<Calibracao>(`/api/calibracao?alfa=${alfa}`),
  auditoria: () => pedir<Auditoria>("/api/auditoria"),
  avaliacoes: () => pedir<ResumoAvaliacao[]>("/api/avaliacoes"),
  parecerHtmlDeResultado: async (resultado: Resultado): Promise<string> => {
    const r = await fetch("/api/parecer?formato=html", json(resultado));
    if (!r.ok) throw new ErroApi(r.status, "Falha ao gerar o parecer");
    return r.text();
  },
  parecerPdfDeResultado: async (resultado: Resultado): Promise<Blob> => {
    const r = await fetch("/api/parecer?formato=pdf", json(resultado));
    if (!r.ok) throw new ErroApi(r.status, "Falha ao gerar o PDF");
    return r.blob();
  },
};

export function baixarBlob(blob: Blob, nome: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nome;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
