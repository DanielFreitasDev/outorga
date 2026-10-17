import { useRef, useState } from "react";
import { ArrowRight, Building2, FileCheck2, FilePlus2, FileText, Plus, ScanLine, Trash2, UploadCloud, UserRound, X } from "lucide-react";
import { api } from "../lib/api";
import { Link, navegar } from "../lib/router";
import { LADOS, type Lado, type LeituraATPV } from "../lib/types";
import { LADO_LONGO, PF_FORA_ESCOPO, dataBR, docFmt, moeda, soDigitos } from "../lib/format";
import { Botao, CabecalhoPagina, ErroCaixa, Painel, cx } from "../components/ui";

const ACEITOS = ".pdf,.docx,.txt,.md,.png,.jpg,.jpeg,.tif,.tiff,.webp";
const ACEITOS_ATPV = ".pdf,.png,.jpg,.jpeg,.tif,.tiff,.webp";

function Campo({ rotulo, children, dica }: { rotulo: string; children: React.ReactNode; dica?: string }) {
  return (
    <label className="block text-[12.5px] font-medium text-ink-2">
      {rotulo}
      <div className="mt-1">{children}</div>
      {dica && <div className="mt-0.5 text-[11.5px] font-normal text-muted">{dica}</div>}
    </label>
  );
}

const inpBase = "h-9 rounded-md border border-line-strong bg-surface px-3 text-[13.5px] text-ink placeholder:text-muted";
const inp = `${inpBase} w-full`;

interface Assinante { nome: string; cpf: string }
/** `procurador`: pessoa física que não assina em nome próprio — quem assina por ela precisa de procuração. */
interface Parte { tipo: "PJ" | "PF"; nome: string; documento: string; assinantes: Assinante[]; procurador?: boolean }

const parteVazia = (tipo: "PJ" | "PF"): Parte => ({ tipo, nome: "", documento: "", assinantes: [{ nome: "", cpf: "" }], procurador: false });

function valorBR(v: number): string {
  return v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** Bloco de uma parte da ATPV-e: PJ (com quem vai assinar por ela) ou pessoa física (assina em nome próprio). */
function BlocoParte({ lado, p, onChange }: { lado: Lado; p: Parte; onChange: (p: Parte) => void }) {
  const muda = (campo: Partial<Parte>) => onChange({ ...p, ...campo });
  const mudaAss = (i: number, campo: Partial<Assinante>) =>
    muda({ assinantes: p.assinantes.map((a, k) => (k === i ? { ...a, ...campo } : a)) });
  const pj = p.tipo === "PJ";
  return (
    <fieldset className="min-w-0 rounded-lg border border-line p-3.5">
      <legend className="px-1 text-[12.5px] font-semibold text-ink">{LADO_LONGO[lado]}</legend>
      <div className="mb-3 inline-flex rounded-lg border border-line bg-surface-2 p-0.5" role="group" aria-label={`Tipo do ${lado}`}>
        {(["PJ", "PF"] as const).map((t) => (
          <button key={t} type="button" aria-pressed={p.tipo === t} onClick={() => muda({ tipo: t })}
            className={cx("inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[12.5px] font-medium transition",
              p.tipo === t ? "bg-surface text-ink shadow-card" : "text-muted hover:text-ink")}>
            {t === "PJ" ? <Building2 className="size-3.5" /> : <UserRound className="size-3.5" />}
            {t === "PJ" ? "Pessoa jurídica" : "Pessoa física"}
          </button>
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-[1fr_190px]">
        <Campo rotulo={pj ? "Razão social" : "Nome"}>
          <input className={inp} value={p.nome} onChange={(e) => muda({ nome: e.target.value })} placeholder={pj ? "opcional se vier da ATPV-e" : "opcional"} />
        </Campo>
        <Campo rotulo={pj ? "CNPJ" : "CPF"}>
          <input className={inp} value={p.documento} onChange={(e) => muda({ documento: e.target.value })} inputMode="numeric"
            placeholder={pj ? "00.000.000/0000-00" : "000.000.000-00"} />
        </Campo>
      </div>
      {pj ? (
        <>
          <div className="mt-3 mb-2 flex flex-wrap items-center justify-between gap-2">
            <div className="text-[12.5px] font-medium text-ink-2">
              Quem vai assinar a ATPV-e por ela <span className="font-normal text-muted">(em branco = consultar quem pode assinar)</span>
            </div>
            <Botao type="button" tamanho="sm" variante="fantasma" icone={<Plus className="size-3.5" />}
              onClick={() => muda({ assinantes: [...p.assinantes, { nome: "", cpf: "" }] })}>Adicionar</Botao>
          </div>
          <div className="space-y-2">
            {p.assinantes.map((a, i) => (
              <div key={i} className="flex flex-wrap gap-2 sm:flex-nowrap">
                <input className={cx(inpBase, "min-w-0 basis-full sm:flex-1 sm:basis-auto")} placeholder="Nome completo" value={a.nome} aria-label="Nome do assinante"
                  onChange={(e) => mudaAss(i, { nome: e.target.value })} />
                <input className={cx(inpBase, "min-w-0 flex-1 sm:w-40 sm:flex-none")} placeholder="CPF" value={a.cpf} inputMode="numeric" aria-label="CPF do assinante"
                  onChange={(e) => mudaAss(i, { cpf: e.target.value })} />
                {p.assinantes.length > 1 && (
                  <button type="button" className="rounded-md px-2 text-muted hover:bg-surface-2 hover:text-bad" aria-label="Remover assinante"
                    onClick={() => muda({ assinantes: p.assinantes.filter((_, k) => k !== i) })}><Trash2 className="size-4" /></button>
                )}
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="mt-2.5 space-y-2">
          <label className="flex cursor-pointer items-start gap-2 text-[12.5px] text-ink-2">
            <input type="checkbox" className="mt-0.5 size-4 accent-[var(--accent)]" checked={!!p.procurador}
              onChange={(e) => muda({ procurador: e.target.checked })} />
            <span>Vai assinar por <b className="font-medium text-ink">procurador</b> (não é o próprio {lado === "vendedor" ? "dono" : "comprador"})</span>
          </label>
          {p.procurador ? (
            <>
              <div className="flex flex-wrap gap-2 sm:flex-nowrap">
                <input className={cx(inpBase, "min-w-0 basis-full sm:flex-1 sm:basis-auto")} placeholder="Nome do procurador" value={p.assinantes[0]?.nome ?? ""}
                  aria-label="Nome do procurador" onChange={(e) => mudaAss(0, { nome: e.target.value })} />
                <input className={cx(inpBase, "min-w-0 flex-1 sm:w-40 sm:flex-none")} placeholder="CPF" value={p.assinantes[0]?.cpf ?? ""} inputMode="numeric"
                  aria-label="CPF do procurador" onChange={(e) => mudaAss(0, { cpf: e.target.value })} />
              </div>
              <div className="text-[12px] text-muted">Anexe a procuração (e os substabelecimentos, se houver): o sistema confere se ela dá a esse CPF poder para {lado === "vendedor" ? "vender" : "comprar"} o veículo.</div>
            </>
          ) : (
            <div className="text-[12.5px] text-muted">{PF_FORA_ESCOPO[0].toUpperCase() + PF_FORA_ESCOPO.slice(1)}.</div>
          )}
        </div>
      )}
    </fieldset>
  );
}

export function NovaAnalise() {
  const [arquivos, setArquivos] = useState<File[]>([]);
  const [arrastando, setArrastando] = useState(false);
  const [atpv, setAtpv] = useState<File | null>(null);
  const [leitura, setLeitura] = useState<LeituraATPV | null>(null);
  const [lendoAtpv, setLendoAtpv] = useState(false);
  const [erroAtpv, setErroAtpv] = useState<string | null>(null);
  const [placa, setPlaca] = useState("");
  const [renavam, setRenavam] = useState("");
  const [chassi, setChassi] = useState("");
  const [descricao, setDescricao] = useState("");
  const [data, setData] = useState(new Date().toISOString().slice(0, 10));
  const [valor, setValor] = useState("");
  const [partes, setPartes] = useState<Record<Lado, Parte>>({ vendedor: parteVazia("PJ"), comprador: parteVazia("PF") });
  const [profunda, setProfunda] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const inputAtpv = useRef<HTMLInputElement>(null);

  const adicionar = (lista: FileList | null) => {
    if (!lista) return;
    const novos = [...lista].filter((f) => !arquivos.some((a) => a.name === f.name && a.size === f.size));
    setArquivos((a) => [...a, ...novos]);
  };

  async function lerAtpv(f: File | undefined) {
    if (!f) return;
    setAtpv(f);
    setLeitura(null);
    setErroAtpv(null);
    setLendoAtpv(true);
    try {
      const l = await api.lerAtpv(f);
      const a = l.atpv;
      setLeitura(l);
      if (a.placa) setPlaca(a.placa);
      if (a.renavam) setRenavam(a.renavam);
      if (a.chassi) setChassi(a.chassi);
      if (a.marca_modelo) setDescricao(a.marca_modelo);
      if (a.data) setData(a.data.slice(0, 10));
      if (a.valor !== null && a.valor !== undefined) setValor(valorBR(a.valor));
      setPartes((atual) => {
        const out = { ...atual };
        LADOS.forEach((lado) => {
          const pa = a[lado];
          const ass = a.assinaturas.filter((s) => s.lado === lado).map((s) => ({ nome: s.nome, cpf: s.cpf ?? "" }));
          const docPa = soDigitos(pa.documento);
          out[lado] = {
            tipo: pa.tipo,
            nome: pa.nome ?? "",
            documento: pa.documento ? docFmt(pa.documento) : "",
            assinantes: ass.length ? ass : atual[lado].assinantes,
            // pessoa física cuja assinatura registrada é de outro CPF: assinou por procuração
            procurador: pa.tipo === "PF" && ass.some((x) => soDigitos(x.cpf) && soDigitos(x.cpf) !== docPa),
          };
        });
        return out;
      });
    } catch (e) {
      setErroAtpv(`Não consegui ler a ATPV-e automaticamente (${(e as Error).message}). Ela ainda vai junto com os documentos; preencha o pedido à mão.`);
    } finally {
      setLendoAtpv(false);
    }
  }

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    if (!arquivos.length) return setErro("Anexe os documentos da(s) empresa(s): ato constitutivo e alterações, atas, procurações, CRLV…");
    if (!atpv && !placa.trim()) return setErro("Informe a placa do veículo (ou envie a ATPV-e).");
    if (!atpv && !data) return setErro("Informe a data da venda (ou envie a ATPV-e).");
    const { vendedor, comprador } = partes;
    const verifica = (p: Parte) => p.tipo === "PJ" || (!!p.procurador && !!p.assinantes[0]?.cpf.trim());
    if (!verifica(vendedor) && !verifica(comprador)) {
      return setErro("Nenhuma das partes precisa de verificação: as duas são pessoas físicas assinando em nome próprio. Marque \"vai assinar por procurador\" ou use a Consulta por CPF.");
    }
    for (const p of [vendedor, comprador]) {
      if (p.tipo === "PF" && p.procurador && !p.documento.trim()) {
        return setErro("Informe o CPF da pessoa física representada por procurador (ou envie a ATPV-e), para conferir quem outorgou a procuração.");
      }
    }
    if (!atpv && vendedor.tipo === "PJ" && comprador.tipo === "PJ" && (!vendedor.documento.trim() || !comprador.documento.trim())) {
      return setErro("Com empresa dos dois lados, informe o CNPJ de cada uma (ou envie a ATPV-e) para separar os documentos de cada empresa.");
    }
    const parte = (p: Parte) => ({
      tipo: p.tipo,
      nome: p.nome.trim() || null,
      documento: p.documento.trim() || null,
      assinantes: p.tipo === "PJ" || p.procurador
        ? p.assinantes.filter((a) => a.nome.trim() || a.cpf.trim()).slice(0, p.tipo === "PJ" ? undefined : 1)
          .map((a) => ({ nome: a.nome.trim() || `CPF ${a.cpf.trim()}`, cpf: a.cpf.trim() || null }))
        : [],
    });
    const v = valor.trim() ? Number(valor.replace(/\./g, "").replace(",", ".")) : null;
    const docs = atpv && !arquivos.some((f) => f.name === atpv.name && f.size === atpv.size) ? [atpv, ...arquivos] : arquivos;
    setEnviando(true);
    try {
      const r = await api.novaAnalise(docs, {
        veiculo: { placa: placa.trim().toUpperCase() || null, renavam: renavam.trim() || null, chassi: chassi.trim().toUpperCase() || null, descricao: descricao.trim() || null },
        data_venda: data || null,
        valor: Number.isFinite(v as number) ? v : null,
        vendedor: parte(vendedor),
        comprador: parte(comprador),
        amostras: profunda ? 3 : 1,
        forma_assinatura: "ATPV-e",
      });
      navegar(`/analise/${r.id}`);
    } catch (err) {
      setErro((err as Error).message);
      setEnviando(false);
    }
  }

  const a = leitura?.atpv;
  return (
    <form onSubmit={enviar}>
      <CabecalhoPagina titulo="Análise com ATPV-e"
        sub="Antes de assinar a ATPV-e: envie a ATPV-e e os documentos da(s) empresa(s) e confira se quem vai assinar tem poder — vendendo ou comprando. A IA local lê tudo na sua máquina; nada sai do computador."
        acoes={<Link href="/consulta" className="inline-flex items-center gap-1 text-[13px] font-medium text-accent hover:underline">
          Ainda sem a ATPV-e? Consulta por CPF <ArrowRight className="size-3.5" /></Link>} />
      <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
        <div className="min-w-0 space-y-4">
          <Painel className="p-4">
            <div className="flex items-start gap-3">
              <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-accent-soft text-accent"><ScanLine className="size-5" /></span>
              <div className="min-w-0 flex-1">
                <div className="font-semibold text-ink">1. Comece pela ATPV-e <span className="font-normal text-muted">(opcional)</span></div>
                <p className="mt-0.5 text-[12.5px] text-muted">
                  O sistema lê veículo, vendedor, comprador, valor, data e as assinaturas já registradas, e preenche o pedido ao lado.
                </p>
                {!atpv ? (
                  <Botao type="button" className="mt-3" icone={<UploadCloud className="size-4" />} onClick={() => inputAtpv.current?.click()}>
                    Enviar a ATPV-e (PDF)
                  </Botao>
                ) : (
                  <div className="mt-3 rounded-lg border border-line bg-surface-2 px-3 py-2.5 text-[13px]">
                    <div className="flex items-center gap-2">
                      <FileCheck2 className="size-4 shrink-0 text-accent" />
                      <span className="min-w-0 flex-1 truncate font-medium text-ink">{atpv.name}</span>
                      <button type="button" className="rounded p-1 text-muted hover:bg-surface hover:text-bad" aria-label="Tirar a ATPV-e"
                        onClick={() => { setAtpv(null); setLeitura(null); setErroAtpv(null); }}><X className="size-4" /></button>
                    </div>
                    {lendoAtpv && <div className="mt-1.5 text-[12.5px] text-muted">Lendo a ATPV-e…</div>}
                    {a && (
                      <div className="mt-2 grid gap-x-4 gap-y-1.5 text-[12.5px] sm:grid-cols-2">
                        <div><span className="text-muted">Veículo: </span><span className="font-mono">{a.placa ?? "—"}</span> {a.marca_modelo}</div>
                        <div><span className="text-muted">Venda: </span>{dataBR(a.data)} · {moeda(a.valor)}</div>
                        {LADOS.map((l) => (
                          <div key={l} className="min-w-0">
                            <span className="text-muted">{l === "vendedor" ? "Vendedor" : "Comprador"} ({a[l].tipo}): </span>
                            <span className="break-words">{a[l].nome}</span>
                            {a[l].documento && <span className="ml-1 font-mono text-[11.5px] text-muted">{docFmt(a[l].documento)}</span>}
                          </div>
                        ))}
                        <div className="sm:col-span-2 text-muted">
                          {a.assinaturas.length
                            ? `Assinaturas já registradas: ${a.assinaturas.map((s) => `${s.nome} (${s.lado})`).join(", ")}`
                            : "Nenhuma assinatura registrada ainda — verificação antes de assinar."}
                          {" · "}lida {leitura?.metodo === "llm" ? "pela IA local" : "diretamente do texto"}
                        </div>
                      </div>
                    )}
                    {erroAtpv && <div className="mt-2 text-[12.5px] text-warn">{erroAtpv}</div>}
                  </div>
                )}
                <input ref={inputAtpv} type="file" accept={ACEITOS_ATPV} className="hidden"
                  onChange={(e) => { lerAtpv(e.target.files?.[0]); e.target.value = ""; }} />
              </div>
            </div>
          </Painel>

          <div>
            <div className="mb-2 font-semibold text-ink">2. Documentos da(s) empresa(s)</div>
            <div
              onDragOver={(e) => { e.preventDefault(); setArrastando(true); }}
              onDragLeave={() => setArrastando(false)}
              onDrop={(e) => { e.preventDefault(); setArrastando(false); adicionar(e.dataTransfer.files); }}
              onClick={() => input.current?.click()}
              className={cx("flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-9 text-center transition",
                arrastando ? "border-accent bg-accent-soft" : "border-line-strong bg-surface hover:bg-surface-2")}
              role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") input.current?.click(); }}>
              <UploadCloud className="size-9 text-accent" />
              <div className="mt-3 font-medium text-ink">Arraste os documentos aqui ou clique para escolher</div>
              <div className="mt-1 max-w-sm text-[12.5px] text-muted">
                De cada empresa envolvida (vendedora e/ou compradora): contrato social e alterações, estatuto e atas de eleição,
                CCMEI, procurações, substabelecimentos, revogações e o CRLV. PDF (digital ou escaneado), DOCX ou imagens.
              </div>
              <input ref={input} type="file" multiple accept={ACEITOS} className="hidden" onChange={(e) => { adicionar(e.target.files); e.target.value = ""; }} />
            </div>
            {arquivos.length > 0 && (
              <Painel className="mt-3 divide-y divide-line">
                {arquivos.map((f, i) => (
                  <div key={f.name + i} className="flex items-center gap-3 px-4 py-2.5 text-[13.5px]">
                    <FileText className="size-4 shrink-0 text-muted" />
                    <span className="min-w-0 flex-1 truncate text-ink">{f.name}</span>
                    <span className="num text-[12px] text-muted">{(f.size / 1024).toFixed(0)} KB</span>
                    <button type="button" onClick={() => setArquivos((l) => l.filter((_, k) => k !== i))} className="rounded p-1 text-muted hover:bg-surface-2 hover:text-bad"
                      aria-label={`Remover ${f.name}`}><X className="size-4" /></button>
                  </div>
                ))}
              </Painel>
            )}
          </div>
        </div>

        <Painel className="min-w-0 p-5">
          <div className="mb-3 font-semibold text-ink">3. Pedido de transferência (ATPV-e)</div>
          <div className="grid gap-3 sm:grid-cols-2">
            <Campo rotulo={atpv ? "Placa" : "Placa *"}><input className={inp} value={placa} onChange={(e) => setPlaca(e.target.value)} placeholder="ABC1D23" /></Campo>
            <Campo rotulo="RENAVAM"><input className={inp} value={renavam} onChange={(e) => setRenavam(e.target.value)} inputMode="numeric" /></Campo>
            <Campo rotulo="Chassi"><input className={inp} value={chassi} onChange={(e) => setChassi(e.target.value)} /></Campo>
            <Campo rotulo="Marca/modelo"><input className={inp} value={descricao} onChange={(e) => setDescricao(e.target.value)} placeholder="opcional" /></Campo>
            <Campo rotulo={atpv ? "Data da venda" : "Data da venda *"}><input className={inp} type="date" value={data} onChange={(e) => setData(e.target.value)} /></Campo>
            <Campo rotulo="Valor (R$)" dica="Necessário quando o contrato tem alçada por valor.">
              <input className={inp} value={valor} onChange={(e) => setValor(e.target.value)} inputMode="decimal" placeholder="ex.: 98.500,00" />
            </Campo>
          </div>
          <div className="mt-5 space-y-4">
            {LADOS.map((l) => (
              <BlocoParte key={l} lado={l} p={partes[l]} onChange={(p) => setPartes((atual) => ({ ...atual, [l]: p }))} />
            ))}
          </div>
          <label className="mt-5 flex cursor-pointer items-start gap-2.5 rounded-lg border border-line bg-surface-2 p-3">
            <input type="checkbox" className="mt-0.5 size-4 accent-[var(--accent)]" checked={profunda} onChange={(e) => setProfunda(e.target.checked)} />
            <span>
              <span className="block text-[13.5px] font-medium text-ink">Análise profunda (autoconsistência)</span>
              <span className="block text-[12.5px] text-muted">A IA lê cada documento 3 vezes; se as leituras discordarem, o caso vai para a faixa intermediária. ~3× mais lento.</span>
            </span>
          </label>
          {erro && <div className="mt-4"><ErroCaixa mensagem={erro} /></div>}
          <Botao type="submit" variante="primario" className="mt-5 w-full" carregando={enviando} icone={<FilePlus2 className="size-4" />}>
            Verificar poderes
          </Botao>
        </Painel>
      </div>
    </form>
  );
}
