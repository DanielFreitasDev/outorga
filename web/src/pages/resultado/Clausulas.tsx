import { ArrowRight, BadgeCheck, CircleHelp, CircleX, Sparkles, Target } from "lucide-react";
import type { RegraAvaliada, Resultado } from "../../lib/types";
import { ESCOPO_TXT, MODO_TXT, moeda } from "../../lib/format";
import { Painel, cx } from "../../components/ui";
import { Citacao } from "./comum";

function valorTxt(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "string") return ESCOPO_TXT[v] ?? MODO_TXT[v] ?? v.replace(/_/g, " ");
  if (typeof v === "number") return moeda(v);
  return String(v);
}

function Aplicabilidade({ g }: { g: RegraAvaliada }) {
  if (g.aplicavel === true) return <span className="inline-flex items-center gap-1 text-[12px] font-medium text-ok"><BadgeCheck className="size-4" />aplicável</span>;
  if (g.aplicavel === null) return <span className="inline-flex items-center gap-1 text-[12px] font-medium text-warn"><CircleHelp className="size-4" />depende</span>;
  return <span className="inline-flex items-center gap-1 text-[12px] font-medium text-muted"><CircleX className="size-4" />não se aplica</span>;
}

export function AbaClausulas({ r }: { r: Resultado }) {
  const ordenadas = [...r.regras].sort((a, b) => Number(b.decisiva) - Number(a.decisiva) || Number(b.aplicavel === true) - Number(a.aplicavel === true));
  return (
    <div>
      <p className="mb-4 text-[13.5px] text-muted">
        Cada cláusula lida pela IA, com o escopo e por que vale (ou não) para esta venda. Quando a <b className="text-ink-2">conferência
        léxica</b> discorda da leitura da IA, o texto do documento prevalece e a correção fica registrada.
      </p>
      {!ordenadas.length && <Painel className="px-4 py-4 text-[13.5px] text-muted">Nenhuma cláusula de representação extraída (ex.: empresário individual) — aplicada a regra supletiva.</Painel>}
      <div className="space-y-3">
        {ordenadas.map((g) => {
          const divs = g.verificacoes.filter((v) => v.divergiu);
          const confs = g.verificacoes.filter((v) => !v.divergiu);
          return (
            <Painel key={g.regra} className={cx("p-4", g.decisiva && "border-accent/60 ring-1 ring-accent/20")}>
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[12px] font-medium text-ink-2">{ESCOPO_TXT[g.escopo] ?? g.escopo}</span>
                <Aplicabilidade g={g} />
                {g.decisiva && <span className="inline-flex items-center gap-1 rounded-full bg-accent-soft px-2 py-0.5 text-[11.5px] font-medium text-accent"><Target className="size-3.5" />decisiva</span>}
                {g.so_condicao && <span className="rounded-full border border-line px-2 py-0.5 text-[11.5px] text-muted">condição</span>}
                <span className="ml-auto font-mono text-[11px] text-muted">{g.regra}</span>
              </div>
              <div className="mt-2 text-[13.5px] text-ink-2">{g.motivo}</div>
              <div className="mt-1 text-[12.5px] text-muted">
                Forma: <b className="font-medium text-ink-2">{MODO_TXT[g.modo ?? ""] ?? g.modo ?? "—"}</b>
                {g.pessoas.length > 0 && <> · pessoas: {g.pessoas.join(", ")}</>}
                {g.cargo && <> · cargo: {g.cargo}</>}
                {g.valor_acima_de !== null && <> · acima de {moeda(g.valor_acima_de)}</>}
                {g.confianca !== null && <> · confiança da leitura {Math.round(g.confianca * 100)}%</>}
              </div>
              {divs.map((v, i) => (
                <div key={i} className="mt-2.5 flex flex-wrap items-center gap-2 rounded-md border border-warn/35 bg-warn-soft px-3 py-2 text-[12.5px] text-ink">
                  <Sparkles className="size-4 text-warn" aria-hidden />
                  <b className="font-medium text-warn">Conferência léxica corrigiu a IA</b>
                  <span>campo <b className="font-medium">{v.campo}</b>: a IA leu</span>
                  <span className="rounded bg-surface px-1.5 py-0.5 font-mono text-[12px] line-through decoration-bad/70">{valorTxt(v.valor_llm)}</span>
                  <ArrowRight className="size-3.5 text-muted" />
                  <span>o texto diz</span>
                  <span className="rounded bg-surface px-1.5 py-0.5 font-mono text-[12px] text-ok">{valorTxt(v.corrigido_para ?? v.valor_lexico)}</span>
                  {v.expressoes.length > 0 && <span className="text-muted">(expressões: {v.expressoes.slice(0, 3).map((e) => `“${e}”`).join(", ")})</span>}
                </div>
              ))}
              {confs.length > 0 && (
                <div className="mt-2 text-[12px] text-ok">
                  ✓ conferido pelo léxico: {confs.map((v) => `${v.campo} = ${valorTxt(v.valor_lexico ?? v.valor_llm)}`).join("; ")}
                </div>
              )}
              <Citacao fonte={g.fonte} max={320} />
            </Painel>
          );
        })}
      </div>
    </div>
  );
}
