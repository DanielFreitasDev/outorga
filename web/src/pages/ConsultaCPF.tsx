import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  AlertTriangle, ArrowRight, Building2, CarFront, CheckCircle2, ChevronDown, CircleHelp, FileText, IdCard, Info, Paperclip,
  Search, ShoppingCart, Tag, UploadCloud, UserRound, UserRoundSearch, X,
} from "lucide-react";
import { ErroApi, api } from "../lib/api";
import { Link, navegar } from "../lib/router";
import { useApp } from "../lib/ctx";
import type { VeiculoBase } from "../lib/types";
import { PENDENCIA_TXT, cnpjValido, cpfFmt, cpfMascarado, cpfValido, docFmt, soDigitos } from "../lib/format";
import { Botao, CabecalhoPagina, ErroCaixa, Painel, cx } from "../components/ui";

const ACEITOS = ".pdf,.docx,.txt,.md,.png,.jpg,.jpeg,.tif,.tiff,.webp";
const inp = "h-9 w-full rounded-md border border-line-strong bg-surface px-3 text-[13.5px] text-ink placeholder:text-muted";

type Papel = "vender" | "comprar";
type Busca = "idle" | "buscando" | "ok" | "nao_encontrado" | "erro";

function Campo({ rotulo, children, dica, erro }: { rotulo: string; children: ReactNode; dica?: ReactNode; erro?: string | null }) {
  return (
    <label className="block min-w-0 text-[12.5px] font-medium text-ink-2">
      {rotulo}
      <div className="mt-1">{children}</div>
      {erro ? <div className="mt-0.5 text-[11.5px] font-normal text-bad">{erro}</div>
        : dica && <div className="mt-0.5 text-[11.5px] font-normal text-muted">{dica}</div>}
    </label>
  );
}

function Passo({ n, titulo, sub, children }: { n: number; titulo: string; sub?: ReactNode; children: ReactNode }) {
  return (
    <Painel className="min-w-0 p-4 md:p-5">
      <div className="mb-3 flex items-start gap-3">
        <span className="num grid size-7 shrink-0 place-items-center rounded-full bg-accent-soft text-[13px] font-semibold text-accent">{n}</span>
        <div className="min-w-0">
          <div className="font-semibold text-ink">{titulo}</div>
          {sub && <div className="mt-0.5 text-[12.5px] text-muted">{sub}</div>}
        </div>
      </div>
      {children}
    </Painel>
  );
}

/** Orientação antes de enviar: o que anexar (ou que não precisa de nada). */
function Orientacao({ tom, icone, titulo, children }: { tom: "ok" | "warn" | "info"; icone: ReactNode; titulo: ReactNode; children?: ReactNode }) {
  const cls = tom === "ok" ? "border-ok/35 bg-ok-soft" : tom === "warn" ? "border-warn/35 bg-warn-soft" : "border-line bg-surface-2";
  const cor = tom === "ok" ? "text-ok" : tom === "warn" ? "text-warn" : "text-accent";
  return (
    <div className={cx("rounded-lg border px-4 py-3", cls)} role={tom === "warn" ? "status" : undefined}>
      <div className="flex items-start gap-2.5">
        <span className={cx("mt-0.5 shrink-0", cor)}>{icone}</span>
        <div className="min-w-0 text-[13.5px] text-ink">
          <div className="font-medium">{titulo}</div>
          {children && <div className="mt-1 text-[12.5px] text-ink-2">{children}</div>}
        </div>
      </div>
    </div>
  );
}

function hoje() {
  return new Date().toISOString().slice(0, 10);
}

/** Lê os parâmetros de "refazer a consulta" (vindos do resultado, quando falta a procuração ou outro documento). */
function lerQuery() {
  const q = new URLSearchParams(window.location.search);
  const lista = (k: string, sep: string) => (q.get(k) ?? "").split(sep).map((s) => s.trim()).filter(Boolean);
  return {
    placa: q.get("placa") ?? "", renavam: q.get("renavam") ?? "",
    papel: (q.get("papel") === "comprar" ? "comprar" : "vender") as Papel,
    cpf: q.get("cpf") ?? "", nome: q.get("nome") ?? "",
    comprador: q.get("comprador") ?? "", compradorNome: q.get("comprador_nome") ?? "",
    valor: q.get("valor") ?? "", data: q.get("data") ?? "",
    anexar: lista("anexar", ","), docs: lista("docs", "|"),
  };
}

function valorBR(v: string): string {
  const n = Number(v);
  return Number.isFinite(n) && v.trim() ? n.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : v;
}

export function ConsultaCPF() {
  const inicial = useMemo(lerQuery, []);
  const refazendo = inicial.anexar.length > 0 || inicial.docs.length > 0;
  const { saude } = useApp();
  const [placa, setPlaca] = useState(inicial.placa);
  const [renavam, setRenavam] = useState(inicial.renavam);
  const [veic, setVeic] = useState<VeiculoBase | null>(null);
  const [busca, setBusca] = useState<Busca>("idle");
  const [erroBusca, setErroBusca] = useState<string | null>(null);
  const [papel, setPapel] = useState<Papel>(inicial.papel);
  const [compradorDoc, setCompradorDoc] = useState(inicial.comprador ? docFmt(inicial.comprador) : "");
  const [compradorNome, setCompradorNome] = useState(inicial.compradorNome);
  const [cpf, setCpf] = useState(inicial.cpf ? cpfFmt(inicial.cpf) : "");
  const [nome, setNome] = useState(inicial.nome);
  const [detalhes, setDetalhes] = useState(!!inicial.valor || inicial.anexar.includes("valor"));
  const [valor, setValor] = useState(inicial.valor ? valorBR(inicial.valor) : "");
  const [data, setData] = useState(inicial.data || hoje());
  const [temProcuracao, setTemProcuracao] = useState<boolean | null>(inicial.anexar.includes("procuracao") ? true : null);
  const [anexarMesmoAssim, setAnexarMesmoAssim] = useState(false);
  const [arquivos, setArquivos] = useState<File[]>([]);
  const [arrastando, setArrastando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const areaDocs = useRef<HTMLDivElement>(null);

  async function buscar(): Promise<VeiculoBase | null> {
    if (!placa.trim() && !renavam.trim()) {
      setErroBusca("Informe a placa ou o RENAVAM.");
      return null;
    }
    setBusca("buscando");
    setErroBusca(null);
    try {
      const v = await api.veiculo(placa, renavam);
      setVeic(v);
      setBusca("ok");
      if (!placa.trim() && v.placa) setPlaca(v.placa);
      if (!renavam.trim() && v.renavam) setRenavam(v.renavam);
      return v;
    } catch (e) {
      setVeic(null);
      if (e instanceof ErroApi && e.status === 404) setBusca("nao_encontrado");
      else {
        setBusca("erro");
        setErroBusca((e as Error).message);
      }
      return null;
    }
  }

  // refazer a consulta a partir do resultado: já busca o veículo
  useEffect(() => {
    if (inicial.placa || inicial.renavam) void buscar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const adicionar = (lista: FileList | null) => {
    if (!lista) return;
    const novos = [...lista].filter((f) => !arquivos.some((a) => a.name === f.name && a.size === f.size));
    setArquivos((a) => [...a, ...novos]);
  };

  // quem está sendo representado: o dono (vender) ou o comprador (comprar)
  const compradorDig = soDigitos(compradorDoc);
  const compradorTipo: "PF" | "PJ" | null = compradorDig.length === 11 && cpfValido(compradorDig) ? "PF"
    : compradorDig.length === 14 && cnpjValido(compradorDig) ? "PJ" : null;
  const erroComprador = compradorDig && !compradorTipo
    ? (compradorDig.length === 11 ? "CPF inválido (confira os dígitos)" : compradorDig.length === 14 ? "CNPJ inválido (confira os dígitos)"
      : "Informe um CPF (11 dígitos) ou CNPJ (14 dígitos)") : null;
  const parteTipo: "PF" | "PJ" | null = papel === "vender" ? (veic?.proprietario.tipo ?? null) : compradorTipo;
  const parteDoc = papel === "vender" ? veic?.proprietario.documento ?? "" : compradorDoc;
  const parteNome = papel === "vender" ? veic?.proprietario.nome ?? "" : compradorNome;
  const quemParte = papel === "vender" ? "dono do veículo" : "comprador";
  const cpfDig = soDigitos(cpf);
  const cpfOk = cpfValido(cpfDig);
  const erroCpf = cpfDig.length >= 11 && !cpfOk ? "CPF inválido (confira os dígitos)" : null;
  const mesmoTitular = parteTipo === "PF" && cpfOk && cpfDig === soDigitos(parteDoc);
  const outroCpfPF = parteTipo === "PF" && cpfOk && !mesmoTitular;
  const donoDesconhecido = papel === "vender" && busca === "nao_encontrado";
  const mostrarDocs = !mesmoTitular || anexarMesmoAssim || arquivos.length > 0;
  const iaDesligada = saude ? !saude.llm_disponivel : false;

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    if (!placa.trim() && !renavam.trim()) return setErro("Informe a placa ou o RENAVAM do veículo.");
    let v = veic;
    if (busca === "idle" || (busca === "erro" && !v)) v = await buscar();
    if (papel === "vender" && !v && !arquivos.length) {
      return setErro("Não achei o dono do veículo na base: anexe o CRLV para identificar o proprietário.");
    }
    if (papel === "comprar" && !compradorTipo) return setErro("Informe o CPF ou o CNPJ do comprador (com os dígitos certos).");
    if (!cpfOk) return setErro("Informe um CPF válido de quem vai assinar.");
    if (outroCpfPF && temProcuracao === true && !arquivos.length) {
      return setErro("Anexe a procuração (e os substabelecimentos, se houver) — ou marque que ele não tem procuração.");
    }
    const vNum = valor.trim() ? Number(valor.replace(/\./g, "").replace(",", ".")) : null;
    setEnviando(true);
    try {
      const r = await api.novaAnalise(arquivos, {
        veiculo: { placa: placa.trim().toUpperCase() || null, renavam: renavam.trim() || null },
        papel,
        cpf: cpfFmt(cpfDig),
        nome: nome.trim() || null,
        ...(papel === "comprar" ? { comprador: { tipo: compradorTipo, nome: compradorNome.trim() || null, documento: docFmt(compradorDig) } } : {}),
        valor: vNum !== null && Number.isFinite(vNum) ? vNum : null,
        data_venda: data || null,
      });
      navegar(`/analise/${r.id}`);
    } catch (err) {
      setErro((err as Error).message);
      setEnviando(false);
    }
  }

  // ------------------------------------------------------------------ orientação do que anexar
  let orientacao: ReactNode = null;
  if (donoDesconhecido) {
    orientacao = (
      <Orientacao tom="warn" icone={<AlertTriangle className="size-4" />} titulo="Anexe o CRLV para identificar o dono do veículo.">
        Depois, conforme o dono, anexe o contrato social/estatuto (empresa) ou a procuração (se quem assina não for o próprio dono).
      </Orientacao>
    );
  } else if (parteTipo === "PJ") {
    orientacao = (
      <Orientacao tom="info" icone={<Building2 className="size-4" />}
        titulo={papel === "vender" ? "O dono é uma empresa: anexe o contrato social ou estatuto (e alterações/atas)." : "O comprador é uma empresa: anexe o contrato social ou estatuto (e alterações/atas)."}>
        Se quem assina for procurador, anexe também a procuração (e os substabelecimentos, se houver). Sem os documentos da empresa,
        o resultado vai pedir o ato constitutivo.
      </Orientacao>
    );
  } else if (mesmoTitular) {
    orientacao = (
      <Orientacao tom="ok" icone={<CheckCircle2 className="size-4" />} titulo={`É o próprio ${quemParte}: pode verificar sem documentos.`}>
        Pessoa física assinando em nome próprio não tem poderes a comprovar — só a identidade (CPF).
      </Orientacao>
    );
  } else if (outroCpfPF) {
    orientacao = (
      <Orientacao tom="warn" icone={<CircleHelp className="size-4" />} titulo={`Esse CPF não é do ${quemParte}. Ele tem procuração?`}>
        <p>Para assinar por {parteNome ? <b className="font-medium text-ink">{parteNome}</b> : `o ${quemParte}`} é preciso procuração
          com poderes para {papel === "vender" ? "vender" : "comprar"} este veículo (no DETRAN-CE: pública, específica e com até 1 ano).</p>
        <div className="mt-2.5 flex flex-wrap gap-2">
          <Botao type="button" tamanho="sm" variante={temProcuracao === true ? "primario" : "secundario"} icone={<Paperclip className="size-3.5" />}
            onClick={() => { setTemProcuracao(true); setTimeout(() => areaDocs.current?.scrollIntoView({ behavior: "smooth", block: "center" }), 30); }}>
            Tem — vou anexar
          </Botao>
          <Botao type="button" tamanho="sm" variante={temProcuracao === false ? "primario" : "secundario"} onClick={() => setTemProcuracao(false)}>
            Não tem procuração
          </Botao>
        </div>
        {temProcuracao === false && (
          <p className="mt-2 text-[12.5px] text-ink-2">
            Sem procuração, só {parteNome ? <b className="font-medium text-ink">{parteNome}</b> : `o ${quemParte}`} pode assinar. Você pode verificar
            assim mesmo: o resultado vai registrar que falta a procuração.
          </p>
        )}
      </Orientacao>
    );
  } else if (papel === "comprar" && !compradorTipo) {
    orientacao = <Orientacao tom="info" icone={<Info className="size-4" />} titulo="Informe o CPF ou CNPJ do comprador para ver o que anexar." />;
  } else if (!cpfOk) {
    orientacao = <Orientacao tom="info" icone={<Info className="size-4" />} titulo="Informe o CPF de quem vai assinar para ver o que é preciso anexar." />;
  }

  return (
    <form onSubmit={enviar} className="max-w-[880px]">
      <CabecalhoPagina titulo="Consulta por CPF"
        sub={<>Antes da ATPV-e: informe o veículo, se a pessoa vai vender ou comprar e o CPF de quem vai assinar. Se o dono (ou o
          comprador) for empresa, o sistema confere se esse CPF tem poder por ela; se for pessoa física e o CPF for outro, pergunta
          pela procuração e confere se ela dá poder àquele CPF.</>}
        acoes={<Link href="/nova" className="inline-flex items-center gap-1 text-[13px] font-medium text-accent hover:underline">
          Já tem a ATPV-e? Analise com ela <ArrowRight className="size-3.5" /></Link>} />

      {refazendo && (
        <div className="mb-4 rounded-lg border border-warn/35 bg-warn-soft px-4 py-3 text-[13px] text-ink">
          <div className="font-medium">Refazendo a consulta com o que faltou{inicial.anexar.length
            ? `: ${inicial.anexar.map((t) => PENDENCIA_TXT[t] ?? t).join(", ")}` : ""}.</div>
          {inicial.docs.length > 0 && (
            <div className="mt-1 text-[12.5px] text-ink-2">
              Anexe de novo os documentos enviados antes ({inicial.docs.join(", ")}) junto com os novos — cada consulta lê o conjunto completo.
            </div>
          )}
        </div>
      )}

      <div className="space-y-4">
        <Passo n={1} titulo="Veículo" sub="O dono vem da base veicular pela placa ou pelo RENAVAM (no protótipo, uma base simulada com dados fictícios).">
          <div className="grid gap-3 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
            <Campo rotulo="Placa">
              <input className={cx(inp, "font-mono uppercase")} value={placa} placeholder="ABC1D23" autoComplete="off"
                onChange={(e) => { setPlaca(e.target.value); setBusca("idle"); setVeic(null); }} />
            </Campo>
            <Campo rotulo="RENAVAM">
              <input className={cx(inp, "font-mono")} value={renavam} inputMode="numeric" placeholder="opcional" autoComplete="off"
                onChange={(e) => { setRenavam(e.target.value); setBusca("idle"); setVeic(null); }} />
            </Campo>
            <Botao type="button" icone={<Search className="size-4" />} carregando={busca === "buscando"} onClick={() => void buscar()}>
              Buscar dono
            </Botao>
          </div>
          {erroBusca && <div className="mt-3"><ErroCaixa mensagem={erroBusca} /></div>}
          {busca === "ok" && veic && (
            <div className="mt-3 flex min-w-0 flex-wrap items-start gap-3 rounded-lg border border-line bg-surface-2 px-4 py-3">
              <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-surface text-accent">
                {veic.proprietario.tipo === "PJ" ? <Building2 className="size-5" /> : <UserRound className="size-5" />}
              </span>
              <div className="min-w-[160px] flex-1">
                <div className="text-[11.5px] font-medium uppercase tracking-wide text-muted">
                  Proprietário · {veic.proprietario.tipo === "PJ" ? "pessoa jurídica" : "pessoa física"}
                </div>
                <div className="break-words font-medium text-ink">{veic.proprietario.nome}</div>
                <div className="font-mono text-[12px] text-muted">
                  {veic.proprietario.tipo === "PJ" ? `CNPJ ${docFmt(veic.proprietario.documento)}` : `CPF ${cpfMascarado(veic.proprietario.documento)}`}
                </div>
              </div>
              <div className="min-w-0 basis-full border-t border-line pt-2 text-[12.5px] text-ink-2 sm:basis-auto sm:border-0 sm:pt-0 sm:text-right">
                <div className="inline-flex items-center gap-1.5"><CarFront className="size-4 text-muted" /><span className="font-mono">{veic.placa}</span></div>
                <div className="text-muted">{veic.marca_modelo}{veic.ano_modelo ? ` · ${veic.ano_modelo}` : ""}</div>
                {veic.fonte && <div className="text-[11.5px] text-muted">{veic.fonte}</div>}
              </div>
            </div>
          )}
          {busca === "nao_encontrado" && (
            <div className="mt-3">
              <Orientacao tom="warn" icone={<AlertTriangle className="size-4" />} titulo="Veículo não encontrado na base.">
                No protótipo a base veicular é simulada (só os veículos fictícios do corpus). No DETRAN, essa consulta é feita na
                base RENAVAM. Para seguir, anexe o CRLV no passo 4: o sistema identifica o dono por ele.
              </Orientacao>
            </div>
          )}
        </Passo>

        <Passo n={2} titulo="Vai assinar para">
          <div className="grid gap-2 sm:grid-cols-2" role="radiogroup" aria-label="Papel de quem vai assinar">
            {([
              { v: "vender" as Papel, icone: <Tag className="size-4" />, titulo: "Vender", sub: "pelo proprietário (antigo dono)" },
              { v: "comprar" as Papel, icone: <ShoppingCart className="size-4" />, titulo: "Comprar", sub: "pelo comprador (novo dono)" },
            ]).map((o) => (
              <button key={o.v} type="button" role="radio" aria-checked={papel === o.v} onClick={() => setPapel(o.v)}
                className={cx("flex items-start gap-3 rounded-lg border px-4 py-3 text-left transition",
                  papel === o.v ? "border-accent bg-accent-soft ring-2 ring-accent/20" : "border-line bg-surface hover:bg-surface-2")}>
                <span className={cx("mt-0.5", papel === o.v ? "text-accent" : "text-muted")}>{o.icone}</span>
                <span>
                  <span className={cx("block font-medium", papel === o.v ? "text-accent" : "text-ink")}>{o.titulo}</span>
                  <span className="block text-[12.5px] text-muted">{o.sub}</span>
                </span>
              </button>
            ))}
          </div>
          {papel === "comprar" && (
            <div className="mt-3 grid gap-3 sm:grid-cols-[220px_1fr]">
              <Campo rotulo="CPF ou CNPJ do comprador *" erro={erroComprador}
                dica={compradorTipo ? (compradorTipo === "PJ" ? "pessoa jurídica" : "pessoa física") : undefined}>
                <input className={cx(inp, "font-mono")} value={compradorDoc} inputMode="numeric" placeholder="CPF ou CNPJ"
                  onChange={(e) => setCompradorDoc(e.target.value)} onBlur={() => compradorTipo && setCompradorDoc(docFmt(compradorDig))} />
              </Campo>
              <Campo rotulo={compradorTipo === "PJ" ? "Razão social" : "Nome do comprador"} dica="opcional">
                <input className={inp} value={compradorNome} onChange={(e) => setCompradorNome(e.target.value)} />
              </Campo>
            </div>
          )}
        </Passo>

        <Passo n={3} titulo="Quem vai assinar" sub="O CPF de quem vai assinar a ATPV-e (o próprio dono, um administrador da empresa ou um procurador).">
          <div className="grid gap-3 sm:grid-cols-[220px_1fr]">
            <Campo rotulo="CPF *" erro={erroCpf} dica={cpfOk ? "CPF válido" : undefined}>
              <input className={cx(inp, "font-mono")} value={cpf} inputMode="numeric" placeholder="000.000.000-00" autoComplete="off"
                onChange={(e) => setCpf(e.target.value)} onBlur={() => cpfOk && setCpf(cpfFmt(cpfDig))} />
            </Campo>
            <Campo rotulo="Nome" dica="opcional — ajuda a conferir com os documentos">
              <input className={inp} value={nome} onChange={(e) => setNome(e.target.value)} autoComplete="off" />
            </Campo>
          </div>
          <button type="button" onClick={() => setDetalhes((d) => !d)} aria-expanded={detalhes}
            className="mt-3 inline-flex items-center gap-1 text-[12.5px] font-medium text-accent hover:underline">
            <ChevronDown className={cx("size-3.5 transition", detalhes && "rotate-180")} /> Valor e data da venda (opcional)
          </button>
          {detalhes && (
            <div className="mt-2 grid gap-3 sm:grid-cols-2">
              <Campo rotulo="Valor previsto da venda (R$)" dica="Necessário quando o contrato da empresa tem alçada por valor.">
                <input className={inp} value={valor} onChange={(e) => setValor(e.target.value)} inputMode="decimal" placeholder="ex.: 95.000,00" />
              </Campo>
              <Campo rotulo="Data de referência" dica="Padrão: hoje (prazo de procuração e mandatos são conferidos nesta data).">
                <input className={inp} type="date" value={data} onChange={(e) => setData(e.target.value)} />
              </Campo>
            </div>
          )}
        </Passo>

        <Passo n={4} titulo="Documentos" sub="Só o que for preciso: o sistema diz abaixo o que anexar.">
          <div className="space-y-3">
            {orientacao}
            {mesmoTitular && !mostrarDocs && (
              <button type="button" className="text-[12.5px] font-medium text-accent hover:underline" onClick={() => setAnexarMesmoAssim(true)}>
                Anexar documentos mesmo assim
              </button>
            )}
            {mostrarDocs && (
              <div ref={areaDocs}>
                <div
                  onDragOver={(e) => { e.preventDefault(); setArrastando(true); }}
                  onDragLeave={() => setArrastando(false)}
                  onDrop={(e) => { e.preventDefault(); setArrastando(false); adicionar(e.dataTransfer.files); }}
                  onClick={() => input.current?.click()}
                  className={cx("flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-5 py-7 text-center transition",
                    arrastando ? "border-accent bg-accent-soft" : outroCpfPF && temProcuracao ? "border-warn/60 bg-surface hover:bg-surface-2"
                      : "border-line-strong bg-surface hover:bg-surface-2")}
                  role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") input.current?.click(); }}>
                  <UploadCloud className="size-8 text-accent" />
                  <div className="mt-2 font-medium text-ink">
                    {outroCpfPF ? "Arraste a procuração (e substabelecimentos) ou clique para escolher"
                      : donoDesconhecido ? "Arraste o CRLV e os demais documentos ou clique para escolher"
                        : "Arraste os documentos ou clique para escolher"}
                  </div>
                  <div className="mt-1 max-w-md text-[12.5px] text-muted">
                    Contrato social, alterações, estatuto e atas, CCMEI, procurações, substabelecimentos, revogações e CRLV — PDF (digital
                    ou escaneado), DOCX ou imagens.
                  </div>
                  <input ref={input} type="file" multiple accept={ACEITOS} className="hidden" onChange={(e) => { adicionar(e.target.files); e.target.value = ""; }} />
                </div>
                {arquivos.length > 0 && (
                  <div className="mt-3 divide-y divide-line rounded-lg border border-line">
                    {arquivos.map((f, i) => (
                      <div key={f.name + i} className="flex items-center gap-3 px-3.5 py-2 text-[13.5px]">
                        <FileText className="size-4 shrink-0 text-muted" />
                        <span className="min-w-0 flex-1 truncate text-ink">{f.name}</span>
                        <span className="num text-[12px] text-muted">{(f.size / 1024).toFixed(0)} KB</span>
                        <button type="button" onClick={() => setArquivos((l) => l.filter((_, k) => k !== i))}
                          className="rounded p-1 text-muted hover:bg-surface-2 hover:text-bad" aria-label={`Remover ${f.name}`}><X className="size-4" /></button>
                      </div>
                    ))}
                  </div>
                )}
                {arquivos.length > 0 && iaDesligada && (
                  <div className="mt-2 text-[12.5px] text-warn">
                    A IA local está desligada: os documentos só serão lidos quando ela for ligada. Consultas sem documentos funcionam normalmente.
                  </div>
                )}
              </div>
            )}
          </div>
        </Passo>

        {erro && <ErroCaixa mensagem={erro} />}
        <div className="flex flex-wrap items-center gap-3">
          <Botao type="submit" variante="primario" carregando={enviando} icone={<UserRoundSearch className="size-4" />} className="min-w-[220px] flex-1 sm:flex-none">
            Verificar
          </Botao>
          <span className="inline-flex items-center gap-1.5 text-[12.5px] text-muted">
            <IdCard className="size-4" />
            Só o lado de quem vai assinar é verificado; o resultado sai na mesma escala (aceito · revisão humana · recusado).
          </span>
        </div>
      </div>
    </form>
  );
}
