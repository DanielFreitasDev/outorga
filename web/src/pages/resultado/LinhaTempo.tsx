import { useMemo } from "react";
import type { EventoTempo, Resultado } from "../../lib/types";
import { dataBR } from "../../lib/format";
import { Painel, cx } from "../../components/ui";
import { useNav } from "./comum";

const DIA = 86400000;
const t = (iso: string) => new Date(`${iso.slice(0, 10)}T12:00:00`).getTime();

const COR_TIPO: Record<string, string> = {
  ato: "var(--accent)", procuracao: "var(--ok)", vencimento: "var(--bad)", fim_mandato: "var(--warn)",
  substabelecimento: "var(--ok)", revogacao: "var(--bad)", deliberacao: "var(--accent)", venda: "var(--ink)",
};
const ROTULO_TIPO: Record<string, string> = {
  ato: "Ato societário", procuracao: "Procuração", vencimento: "Vencimento", fim_mandato: "Fim de mandato",
  substabelecimento: "Substabelecimento", revogacao: "Revogação", deliberacao: "Deliberação", venda: "Venda (ATPV-e)",
};

interface Barra { doc: string; titulo: string; inicio: number; fim: number | null; vencida: boolean }

export function AbaLinhaTempo({ r }: { r: Resultado }) {
  const { abrirFonte } = useNav();
  const ev = r.linha_do_tempo;
  const venda = ev.find((e) => e.tipo === "venda");
  const { min, max, barras, pontos } = useMemo(() => {
    const ts = ev.map((e) => t(e.data));
    let mn = Math.min(...ts), mx = Math.max(...ts);
    const pad = Math.max((mx - mn) * 0.06, 45 * DIA);
    mn -= pad;
    mx += pad;
    const bs: Barra[] = [];
    for (const e of ev.filter((x) => x.tipo === "procuracao")) {
      const venc = ev.find((x) => x.tipo === "vencimento" && x.doc === e.doc);
      bs.push({ doc: e.doc ?? "", titulo: e.titulo.replace("Procuração para ", ""), inicio: t(e.data), fim: venc ? t(venc.data) : null,
        vencida: !!(venc && venda && t(venc.data) < t(venda.data)) });
    }
    return { min: mn, max: mx, barras: bs, pontos: ev.filter((x) => x.tipo !== "procuracao" && x.tipo !== "vencimento") };
  }, [ev, venda]);

  const W = 1000, X0 = 150, X1 = W - 20;
  const xs = (ts: number) => X0 + ((ts - min) / (max - min)) * (X1 - X0);
  const linhas: { rot: string; itens: EventoTempo[] }[] = [
    { rot: "Atos societários", itens: pontos.filter((p) => p.tipo === "ato" || p.tipo === "deliberacao") },
    { rot: "Mandatos", itens: pontos.filter((p) => p.tipo === "fim_mandato") },
    { rot: "Substab. / revogação", itens: pontos.filter((p) => p.tipo === "substabelecimento" || p.tipo === "revogacao") },
  ].filter((l) => l.itens.length);
  const alturaBarras = barras.length ? 26 + barras.length * 30 : 0;
  const H = 46 + linhas.length * 40 + alturaBarras + 20;
  const anos: number[] = [];
  for (let a = new Date(min).getFullYear() + 1; a <= new Date(max).getFullYear(); a++) anos.push(a);
  const abrir = (doc: string | null) => {
    if (!doc) return;
    const d = r.documentos.find((x) => x.id === doc);
    abrirFonte({ doc_id: doc, doc_titulo: d?.titulo ?? doc, trecho: null, clausula: null, ancoragem: null, pagina: null, inicio: null, fim: null });
  };

  return (
    <div>
      <p className="mb-3 text-[13.5px] text-muted">
        O regime que vale é o vigente <b className="text-ink-2">na data da venda</b>: alterações posteriores não contam, e procurações
        precisam estar no prazo e sem revogação nesse dia.
      </p>
      <Painel className="overflow-x-auto p-3">
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", minWidth: 720 }} role="img" aria-label="Linha do tempo dos documentos">
          {anos.map((a) => {
            const x = xs(new Date(`${a}-01-01T00:00:00`).getTime());
            return (
              <g key={a}>
                <line x1={x} y1={22} x2={x} y2={H - 12} stroke="var(--line)" />
                <text x={x + 4} y={18} fontSize="10.5" fill="var(--muted)" className="num">{a}</text>
              </g>
            );
          })}
          {linhas.map((l, i) => {
            const y = 50 + i * 40;
            return (
              <g key={l.rot}>
                <text x={10} y={y + 4} fontSize="11" fill="var(--ink-2)">{l.rot}</text>
                <line x1={X0} y1={y} x2={X1} y2={y} stroke="var(--line)" strokeDasharray="2 4" />
                {l.itens.map((e, k) => (
                  <g key={k} className="cursor-pointer" onClick={() => abrir(e.doc)}>
                    <circle cx={xs(t(e.data))} cy={y} r={6.5} fill={COR_TIPO[e.tipo] ?? "var(--muted)"} stroke="var(--surface)" strokeWidth={2}>
                      <title>{`${dataBR(e.data)} — ${e.titulo}${e.detalhe ? ` (${e.detalhe})` : ""}`}</title>
                    </circle>
                  </g>
                ))}
              </g>
            );
          })}
          {barras.length > 0 && (
            <g>
              <text x={10} y={50 + linhas.length * 40 + 8} fontSize="11" fill="var(--ink-2)">Procurações</text>
              {barras.map((b, i) => {
                const y = 50 + linhas.length * 40 + 22 + i * 30;
                const x1 = xs(b.inicio), x2 = b.fim ? xs(b.fim) : X1;
                const cor = b.vencida ? "var(--bad)" : "var(--ok)";
                return (
                  <g key={b.doc + i} className="cursor-pointer" onClick={() => abrir(b.doc)}>
                    <rect x={x1} y={y - 7} width={Math.max(4, x2 - x1)} height={14} rx={7} fill={cor} fillOpacity={0.22} stroke={cor} />
                    {!b.fim && <path d={`M ${X1 - 8} ${y - 7} L ${X1} ${y} L ${X1 - 8} ${y + 7}`} fill="none" stroke={cor} />}
                    <text x={x1 + 8} y={y + 3.8} fontSize="10.5" fill="var(--ink)">{b.titulo}{b.fim ? "" : " · sem prazo final"}</text>
                    <title>{`${b.titulo}: ${dataBR(new Date(b.inicio).toISOString())} → ${b.fim ? dataBR(new Date(b.fim).toISOString()) : "sem prazo"}`}</title>
                  </g>
                );
              })}
            </g>
          )}
          {venda && (
            <g>
              <line x1={xs(t(venda.data))} y1={24} x2={xs(t(venda.data))} y2={H - 8} stroke="var(--ink)" strokeWidth={2} />
              <rect x={Math.min(xs(t(venda.data)) - 56, X1 - 112)} y={H - 22} width={112} height={18} rx={9} fill="var(--ink)" />
              <text x={Math.min(xs(t(venda.data)), X1 - 56)} y={H - 9.5} textAnchor="middle" fontSize="10.5" fontWeight={600} fill="var(--bg)">
                venda {dataBR(venda.data)}
              </text>
            </g>
          )}
        </svg>
      </Painel>
      <Painel className="mt-4 divide-y divide-line">
        {ev.map((e, i) => (
          <button key={i} onClick={() => abrir(e.doc)} disabled={!e.doc}
            className={cx("flex w-full items-center gap-3 px-4 py-2.5 text-left text-[13.5px]", e.doc && "hover:bg-surface-2",
              e.tipo === "venda" && "bg-surface-2 font-medium")}>
            <span className="num w-[86px] shrink-0 font-mono text-[12.5px] text-muted">{dataBR(e.data)}</span>
            <span className="size-2.5 shrink-0 rounded-full" style={{ background: COR_TIPO[e.tipo] ?? "var(--muted)" }} />
            <span className="w-[130px] shrink-0 text-[12px] text-muted">{ROTULO_TIPO[e.tipo] ?? e.tipo}</span>
            <span className="text-ink">{e.titulo}</span>
            {e.detalhe && <span className="text-[12.5px] text-muted">· {e.detalhe.replace(/_/g, " ")}</span>}
          </button>
        ))}
      </Painel>
    </div>
  );
}
