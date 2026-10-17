import { useState, type ButtonHTMLAttributes, type ReactNode } from "react";
import {
  AlertTriangle, Check, CheckCircle2, Copy, Info, Loader2, OctagonX, ShieldAlert, XCircle,
} from "lucide-react";
import type { Faixa, Sev, Veredito } from "../lib/types";
import { FAIXA_TXT, SEV_TXT, VEREDITO_TXT, hashCurto } from "../lib/format";

export function cx(...c: (string | false | null | undefined)[]) {
  return c.filter(Boolean).join(" ");
}

/* ----------------------------------------------------------------------------- faixa */
const FAIXA_CLS: Record<Faixa, { solido: string; suave: string; icone: typeof CheckCircle2 }> = {
  VERDE: { solido: "bg-ok text-white", suave: "bg-ok-soft text-ok border-ok/30", icone: CheckCircle2 },
  AMARELO: { solido: "bg-warn text-white dark:text-[#1a1305]", suave: "bg-warn-soft text-warn border-warn/30", icone: AlertTriangle },
  VERMELHO: { solido: "bg-bad text-white dark:text-[#1f0b09]", suave: "bg-bad-soft text-bad border-bad/30", icone: XCircle },
};

export function SeloFaixa({ faixa, grande = false }: { faixa: Faixa; grande?: boolean }) {
  const c = FAIXA_CLS[faixa];
  const I = c.icone;
  if (grande) {
    return (
      <div className={cx("inline-flex items-center gap-2.5 rounded-lg px-4 py-2.5 shadow-card", c.solido)}>
        <I className="size-6" aria-hidden />
        <div className="leading-tight">
          <div className="text-[15px] font-semibold tracking-wide uppercase">{FAIXA_TXT[faixa]}</div>
          <div className="text-[11.5px] opacity-90">
            {faixa === "VERDE" ? "aceite automático" : faixa === "VERMELHO" ? "recusa automática" : "faixa intermediária"}
          </div>
        </div>
      </div>
    );
  }
  return (
    <span className={cx("inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[11.5px] font-medium", c.suave)}>
      <I className="size-3.5" aria-hidden />
      {FAIXA_TXT[faixa]}
    </span>
  );
}

export function ChipVeredito({ v }: { v: Veredito }) {
  const cls = v === "PODE" ? "text-ok" : v === "NAO_PODE" ? "text-bad" : "text-warn";
  return <span className={cx("text-[12px] font-medium", cls)}>{VEREDITO_TXT[v]}</span>;
}

/* -------------------------------------------------------------------------- severidade */
const SEV_CLS: Record<Sev, { cls: string; icone: typeof Info }> = {
  bloqueio: { cls: "bg-bad-soft text-bad border-bad/35", icone: OctagonX },
  alerta: { cls: "bg-warn-soft text-warn border-warn/35", icone: AlertTriangle },
  atencao: { cls: "bg-surface-2 text-warn border-line-strong", icone: ShieldAlert },
  info: { cls: "bg-surface-2 text-muted border-line", icone: Info },
  ok: { cls: "bg-ok-soft text-ok border-ok/30", icone: Check },
};

export function SevTag({ sev, compacto = false }: { sev: Sev; compacto?: boolean }) {
  const c = SEV_CLS[sev] ?? SEV_CLS.info;
  const I = c.icone;
  return (
    <span className={cx("inline-flex shrink-0 items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide",
      c.cls)} title={SEV_TXT[sev]}>
      <I className="size-3" aria-hidden />
      {!compacto && SEV_TXT[sev]}
    </span>
  );
}

/* ------------------------------------------------------------------------------ botões */
type Variante = "primario" | "secundario" | "fantasma" | "perigo" | "sucesso";
const VAR_CLS: Record<Variante, string> = {
  primario: "bg-accent text-accent-ink hover:brightness-110 border-transparent",
  secundario: "bg-surface text-ink border-line-strong hover:bg-surface-2",
  fantasma: "bg-transparent text-ink-2 border-transparent hover:bg-surface-2",
  perigo: "bg-bad text-white border-transparent hover:brightness-110",
  sucesso: "bg-ok text-white border-transparent hover:brightness-110",
};

export function Botao({
  variante = "secundario", tamanho = "md", carregando = false, icone, children, className, disabled, ...p
}: ButtonHTMLAttributes<HTMLButtonElement> & { variante?: Variante; tamanho?: "sm" | "md"; carregando?: boolean; icone?: ReactNode }) {
  return (
    <button
      {...p}
      disabled={disabled || carregando}
      className={cx(
        "inline-flex items-center justify-center gap-1.5 rounded-md border font-medium transition disabled:opacity-55",
        tamanho === "sm" ? "h-8 px-2.5 text-[12.5px]" : "h-9 px-3.5 text-[13.5px]",
        VAR_CLS[variante],
        className,
      )}
    >
      {carregando ? <Loader2 className="size-4 animate-spin" aria-hidden /> : icone}
      {children}
    </button>
  );
}

/* ------------------------------------------------------------------------- contêineres */
export function Painel({ children, className, ...p }: { children: ReactNode; className?: string } & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div {...p} className={cx("rounded-xl border border-line bg-surface shadow-card", className)}>
      {children}
    </div>
  );
}

export function Secao({ titulo, descricao, acoes, children, className, id }: {
  titulo: ReactNode; descricao?: ReactNode; acoes?: ReactNode; children: ReactNode; className?: string; id?: string;
}) {
  return (
    <section className={cx(className ?? "mt-7 first:mt-0")} id={id}>
      <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
        <div>
          <h2 className="text-[15.5px] font-semibold text-ink">{titulo}</h2>
          {descricao && <p className="mt-0.5 text-[13px] text-muted">{descricao}</p>}
        </div>
        {acoes}
      </div>
      {children}
    </section>
  );
}

export function CabecalhoPagina({ titulo, sub, acoes }: { titulo: ReactNode; sub?: ReactNode; acoes?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
      <div className="max-w-3xl">
        <h1 className="text-[22px] font-semibold tracking-tight text-ink">{titulo}</h1>
        {sub && <p className="mt-1 text-[14px] text-muted">{sub}</p>}
      </div>
      {acoes && <div className="flex flex-wrap gap-2">{acoes}</div>}
    </div>
  );
}

export function Carregando({ texto = "Carregando…" }: { texto?: string }) {
  return (
    <div className="flex items-center gap-2 py-10 text-muted">
      <Loader2 className="size-4 animate-spin" aria-hidden /> {texto}
    </div>
  );
}

export function Vazio({ titulo, children, icone }: { titulo: string; children?: ReactNode; icone?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-line-strong px-6 py-12 text-center">
      {icone && <div className="mb-3 text-muted">{icone}</div>}
      <div className="font-medium text-ink">{titulo}</div>
      {children && <div className="mt-1 max-w-md text-[13px] text-muted">{children}</div>}
    </div>
  );
}

export function ErroCaixa({ mensagem }: { mensagem: string }) {
  return (
    <div className="rounded-lg border border-bad/35 bg-bad-soft px-4 py-3 text-[13.5px] text-bad" role="alert">
      {mensagem}
    </div>
  );
}

export function HashCopiavel({ valor, n = 10 }: { valor: string | null | undefined; n?: number }) {
  const [ok, setOk] = useState(false);
  if (!valor) return <span className="text-muted">—</span>;
  return (
    <button
      type="button"
      onClick={() => {
        navigator.clipboard?.writeText(valor).then(() => {
          setOk(true);
          setTimeout(() => setOk(false), 1400);
        }).catch(() => undefined);
      }}
      className="group inline-flex items-center gap-1 rounded px-1 font-mono text-[12px] text-ink-2 hover:bg-surface-2"
      title={`${valor} — clique para copiar`}
    >
      {hashCurto(valor, n)}
      {ok ? <Check className="size-3 text-ok" aria-hidden /> : <Copy className="size-3 opacity-0 group-hover:opacity-70" aria-hidden />}
    </button>
  );
}

/* --------------------------------------------------------------------------------- abas */
export function Abas<T extends string>({ abas, atual, onTrocar }: {
  abas: { id: T; rotulo: string; icone?: ReactNode; contador?: number; destaque?: boolean }[];
  atual: T;
  onTrocar: (id: T) => void;
}) {
  return (
    <div role="tablist" className="scroll-thin flex gap-0.5 overflow-x-auto overflow-y-hidden border-b border-line" aria-label="Seções do resultado">
      {abas.map((a) => (
        <button
          key={a.id}
          role="tab"
          aria-selected={a.id === atual}
          onClick={() => onTrocar(a.id)}
          className={cx(
            "relative inline-flex shrink-0 items-center gap-1.5 px-3.5 py-2.5 text-[13.5px] font-medium transition",
            a.id === atual ? "text-accent" : "text-muted hover:text-ink",
          )}
        >
          {a.icone}
          {a.rotulo}
          {a.contador !== undefined && a.contador > 0 && (
            <span className={cx("num rounded-full px-1.5 text-[11px]", a.destaque ? "bg-warn-soft text-warn" : "bg-surface-2 text-muted")}>
              {a.contador}
            </span>
          )}
          {a.id === atual && <span className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-accent" />}
        </button>
      ))}
    </div>
  );
}

export function Rotulo({ children }: { children: ReactNode }) {
  return <div className="text-[11.5px] font-medium uppercase tracking-wide text-muted">{children}</div>;
}
