import { useMemo, useState } from "react";
import type { ArestaGrafo, NoGrafo, Resultado } from "../../lib/types";
import { cpfFmt } from "../../lib/format";
import { Painel } from "../../components/ui";
import { useNav } from "./comum";

type Status = ArestaGrafo["status"];
const PRIORIDADE: Record<Status, number> = { invalido: 3, alerta: 2, valido: 1, neutro: 0 };
const COR: Record<Status, string> = { valido: "var(--ok)", alerta: "var(--warn)", invalido: "var(--bad)", neutro: "var(--line-strong)" };

interface Ligacao { a: string; b: string; status: Status; rotulos: string[]; curtos: string[]; tipos: Set<string>; docs: string[]; motivos: string[] }
interface Pos { x: number; y: number; w: number; h: number; col: number }

function trunc(s: string, n: number) {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

const DIM = { veiculo: { w: 200, h: 54 }, empresa: { w: 224, h: 66 }, pessoa: { w: 204, h: 56 } };
const GAP_X = 132, GAP_Y = 22, PAD = 18, GAP_VEIC = 46;

/** Rótulo curto para caber entre as colunas (o texto completo fica na dica). */
function rotuloCurto(e: ArestaGrafo): string {
  const r = e.rotulo ?? "";
  if (e.tipo === "socio") return r;
  if (e.tipo === "administracao") {
    const t = r.replace(/^administra · /, "");
    if (t.startsWith("sem poder")) return "sem poder";
    if (t.startsWith("mandato encerrado")) return t.replace("mandato encerrado em", "venceu");
    return t;
  }
  if (e.tipo === "procuracao") return `proc. ${r.replace(/^procuração /, "").split(" · ")[0]}${e.status === "invalido" ? " ✕" : ""}`;
  if (e.tipo === "substabelecimento") {
    const t = r.split(" · ")[0];
    return t.includes("sem reserva") ? "substab. s/ reserva" : t.includes("com reserva") ? "substab. c/ reserva" : "substab.";
  }
  if (e.tipo === "clausula") return "cláusula específica";
  return r;
}

interface Layout { pos: Map<string, Pos>; W: number; H: number; gaps: number[][]; centrosX: number[] }

function layout(nos: NoGrafo[], arestas: ArestaGrafo[]): Layout {
  const col = new Map<string, number>();
  nos.forEach((n) => col.set(n.id, n.tipo === "pessoa" ? 1 : 0));
  for (let it = 0; it < 4; it++) {
    for (const e of arestas) {
      if (e.tipo === "procuracao") col.set(e.para, Math.max(col.get(e.para) ?? 1, 2, (col.get(e.de) ?? 0) + 1));
      if (e.tipo === "substabelecimento") col.set(e.para, Math.max(col.get(e.para) ?? 1, (col.get(e.de) ?? 2) + 1));
    }
  }
  const usados = [...new Set(col.values())].sort((a, b) => a - b);
  const idxCol = new Map(usados.map((c, i) => [c, i]));
  const colunas: NoGrafo[][] = usados.map(() => []);
  const ordem = (n: NoGrafo) => {
    if (n.tipo === "empresa") return -10;
    if (n.tipo === "veiculo") return -9;
    const adm = arestas.some((e) => e.tipo === "administracao" && e.para === n.id && e.status !== "invalido");
    return adm ? 0 : 1;
  };
  nos.forEach((n) => colunas[idxCol.get(col.get(n.id)!)!].push(n));
  colunas.forEach((c) => c.sort((a, b) => ordem(a) - ordem(b)));
  const espaco = (c: NoGrafo[], i: number) => (c[i].tipo === "empresa" && c[i + 1]?.tipo === "veiculo" ? GAP_VEIC : GAP_Y);
  const larguras = colunas.map((c) => Math.max(...c.map((n) => DIM[n.tipo].w)));
  const alturas = colunas.map((c) => c.reduce((s, n, i) => s + DIM[n.tipo].h + (i < c.length - 1 ? espaco(c, i) : 0), 0));
  const H = Math.max(...alturas) + PAD * 2;
  const pos = new Map<string, Pos>();
  const gaps: number[][] = [];
  const centrosX: number[] = [];
  let x = PAD;
  colunas.forEach((c, i) => {
    let y = PAD + (H - PAD * 2 - alturas[i]) / 2;
    const g: number[] = [y - GAP_Y / 2];
    c.forEach((n, k) => {
      const d = DIM[n.tipo];
      pos.set(n.id, { x: x + (larguras[i] - d.w) / 2, y, w: d.w, h: d.h, col: i });
      y += d.h;
      g.push(y + (k < c.length - 1 ? espaco(c, k) : GAP_Y) / 2);
      y += k < c.length - 1 ? espaco(c, k) : 0;
    });
    gaps.push(g);
    centrosX.push(x + larguras[i] / 2);
    x += larguras[i] + GAP_X;
  });
  return { pos, W: x - GAP_X + PAD, H, gaps, centrosX };
}

/** Caminho suave por "corredores" (vãos entre cartões) quando a ligação pula colunas. */
function caminho(pa: Pos, pb: Pos, L: Layout): { d: string; lx: number; ly: number } {
  const x1 = pa.x + pa.w, y1 = pa.y + pa.h / 2, x2 = pb.x - 2, y2 = pb.y + pb.h / 2;
  const pts: [number, number][] = [[x1, y1]];
  for (let c = pa.col + 1; c < pb.col; c++) {
    const t = (c - pa.col) / (pb.col - pa.col);
    const alvo = y1 + (y2 - y1) * t;
    const gy = L.gaps[c].reduce((m, g) => (Math.abs(g - alvo) < Math.abs(m - alvo) ? g : m), L.gaps[c][0]);
    pts.push([L.centrosX[c], gy]);
  }
  pts.push([x2, y2]);
  let d = `M ${pts[0][0]} ${pts[0][1]}`;
  for (let i = 1; i < pts.length; i++) {
    const [ax, ay] = pts[i - 1], [bx, by] = pts[i];
    const dx = (bx - ax) * 0.5;
    d += ` C ${ax + dx} ${ay}, ${bx - dx} ${by}, ${bx} ${by}`;
  }
  const pula = pb.col - pa.col > 1;
  const lx = pula ? x2 - GAP_X / 2 : (x1 + x2) / 2;
  const ly = pula ? (pts[pts.length - 2][1] + y2) / 2 : (y1 + y2) / 2;
  return { d, lx, ly };
}

function ligacoes(arestas: ArestaGrafo[]): Ligacao[] {
  const m = new Map<string, Ligacao>();
  for (const e of arestas) {
    const [a, b] = [e.de, e.para];
    const k = [a, b].sort().join("|");
    const l = m.get(k) ?? { a, b, status: "neutro" as Status, rotulos: [], curtos: [], tipos: new Set<string>(), docs: [], motivos: [] };
    if (e.tipo !== "socio") {
      l.a = a;
      l.b = b;
    }
    if (PRIORIDADE[e.status] > PRIORIDADE[l.status]) l.status = e.status;
    if (e.rotulo) {
      l.rotulos.push(e.tipo === "socio" ? `sócio ${e.rotulo}` : e.rotulo);
      l.curtos.push(rotuloCurto(e));
    }
    l.tipos.add(e.tipo);
    if (e.doc) l.docs.push(e.doc);
    if (e.motivo) l.motivos.push(e.motivo);
    m.set(k, l);
  }
  return [...m.values()];
}

export function AbaGrafo({ r }: { r: Resultado }) {
  const { abrirFonte, simulacao } = useNav();
  const L = useMemo(() => layout(r.grafo.nos, r.grafo.arestas), [r]);
  const { pos, W, H } = L;
  const ligs = useMemo(() => ligacoes(r.grafo.arestas), [r]);
  const [dica, setDica] = useState<{ x: number; y: number; l: Ligacao } | null>(null);
  const tituloDoc = (id: string) => r.documentos.find((d) => d.id === id)?.titulo ?? id;

  const abrirDoc = (id: string) => abrirFonte({ doc_id: id, doc_titulo: tituloDoc(id), trecho: null, clausula: null, ancoragem: null,
    pagina: null, inicio: null, fim: null });

  return (
    <div>
      <p className="mb-3 text-[13.5px] text-muted">
        {r.empresa.tipo === "PF"
          ? <>Da esquerda para a direita: o veículo, o titular (pessoa física), os procuradores que ele constituiu e os substabelecidos.</>
          : <>Da esquerda para a direita: o veículo, a empresa proprietária, quem a administra (pelo contrato), os procuradores e
            os substabelecidos.</>} Passe o mouse numa ligação para ver o motivo; clique para abrir o documento.
      </p>
      <Painel className="relative overflow-x-auto p-2">
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", minWidth: Math.min(W, 760), maxWidth: W }} role="img"
          aria-label="Grafo de poderes de representação">
          <defs>
            {(["valido", "alerta", "invalido", "neutro"] as Status[]).map((s) => (
              <marker key={s} id={`seta-${s}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill={COR[s]} />
              </marker>
            ))}
          </defs>
          {ligs.map((l, i) => {
            let pa = pos.get(l.a), pb = pos.get(l.b);
            if (!pa || !pb) return null;
            let inv = false;
            if (pa.col > pb.col || (pa.col === pb.col && pa.y > pb.y)) { [pa, pb] = [pb, pa]; inv = true; }
            const vertical = pa.col === pb.col;
            let d: string, mx: number, my: number;
            if (vertical) {
              const xv = pa.x + pa.w / 2;
              d = `M ${xv} ${pa.y + pa.h} L ${xv} ${pb.y - 2}`;
              mx = xv + 4;
              my = (pa.y + pa.h + pb.y) / 2;
            } else {
              const c = caminho(pa, pb, L);
              d = c.d; mx = c.lx; my = c.ly;
            }
            const so_socio = l.tipos.size === 1 && l.tipos.has("socio");
            const rot = trunc(l.curtos.join(" · "), 21);
            const tw = rot.length * 5.9 + 14;
            const seta = so_socio ? undefined : `url(#seta-${l.status})`;
            return (
              <g key={i} className="cursor-pointer" onMouseEnter={(e) => setDica({ x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY, l })}
                onMouseLeave={() => setDica(null)} onClick={() => l.docs[0] && abrirDoc(l.docs[0])}>
                <path d={d} fill="none" stroke="transparent" strokeWidth={14} />
                <path d={d} fill="none" stroke={COR[l.status]} strokeWidth={l.status === "neutro" ? 1.4 : 2.2}
                  strokeDasharray={l.status === "invalido" ? "6 5" : undefined}
                  markerEnd={!inv ? seta : undefined} markerStart={inv ? seta : undefined} />
                {rot && (
                  vertical ? (
                    <text x={mx + 6} y={my + 3.5} fontSize="10.5" fill="var(--muted)">{rot}</text>
                  ) : (
                    <g>
                      <rect x={mx - tw / 2} y={my - 9.5} width={tw} height={19} rx={9.5} fill="var(--surface)" stroke={COR[l.status]} strokeWidth={0.9} />
                      <text x={mx} y={my + 3.8} textAnchor="middle" fontSize="10.5" fill="var(--ink-2)">{rot}</text>
                    </g>
                  )
                )}
              </g>
            );
          })}
          {r.grafo.nos.map((n) => {
            const p = pos.get(n.id);
            if (!p) return null;
            const ass = !!n.assinante;
            const borda = ass ? "var(--accent)" : n.tipo === "empresa" ? "var(--ink-2)" : "var(--line-strong)";
            const pf = r.empresa.tipo === "PF";
            const sub = n.tipo === "pessoa" ? (n.papeis ?? []).join(" · ")
              : n.tipo === "empresa" && pf ? `CPF ${cpfFmt(r.empresa.cpf ?? "") || "—"}` : n.sub ?? "";
            const clicavel = !!simulacao && n.tipo === "pessoa";
            const naSim = clicavel && simulacao!.selecionados.has(n.id);
            return (
              <g key={n.id} className={clicavel ? "cursor-pointer" : undefined} onClick={clicavel ? () => simulacao!.alternar(n.id) : undefined}>
                {clicavel && <title>Clique para incluir/tirar na simulação “E se…?”</title>}
                {naSim && !ass && <rect x={p.x - 5} y={p.y - 5} width={p.w + 10} height={p.h + 10} rx={13} fill="none" stroke="var(--accent)" strokeWidth={1.6} strokeDasharray="5 4" />}
                {ass && <rect x={p.x - 4} y={p.y - 4} width={p.w + 8} height={p.h + 8} rx={12} fill="none" stroke="var(--accent)" strokeOpacity={0.35} strokeWidth={4} />}
                <rect x={p.x} y={p.y} width={p.w} height={p.h} rx={9}
                  fill={n.tipo === "empresa" ? "var(--surface-2)" : "var(--surface)"} stroke={borda} strokeWidth={ass ? 2 : 1.2} />
                <text x={p.x + 12} y={p.y + (n.tipo === "empresa" ? 24 : 22)} fontSize={n.tipo === "empresa" ? 12 : 12.2} fontWeight={600} fill="var(--ink)">
                  {n.tipo === "veiculo" ? n.sub ?? "veículo" : trunc(n.rotulo, n.tipo === "empresa" ? 27 : 26)}
                </text>
                <text x={p.x + 12} y={p.y + (n.tipo === "empresa" ? 42 : 39)} fontSize="10.2" fill="var(--muted)">
                  {n.tipo === "veiculo" ? trunc(n.rotulo, 24) : trunc(sub, n.tipo === "empresa" ? 33 : 31)}
                </text>
                {n.tipo === "empresa" && <text x={p.x + 12} y={p.y + 57} fontSize="9.5" fill="var(--muted)">
                  {(r.lado ?? r.pedido.lado) === "comprador"
                    ? (pf ? "pessoa física compradora (novo proprietário)" : "empresa compradora (novo proprietário)")
                    : (pf ? "pessoa física proprietária (vendedora)" : "empresa proprietária (vendedora)")}</text>}
                {ass && (
                  <g>
                    <rect x={p.x + p.w - 66} y={p.y - 9} width={60} height={17} rx={8.5} fill="var(--accent)" />
                    <text x={p.x + p.w - 36} y={p.y + 3} textAnchor="middle" fontSize="9.5" fontWeight={600} fill="var(--accent-ink)">assinante</text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
        {dica && (
          <div className="pointer-events-none absolute z-10 max-w-xs rounded-lg border border-line bg-surface px-3 py-2 text-[12.5px] shadow-pop"
            style={{ left: Math.min(dica.x + 14, 640), top: dica.y + 14 }}>
            <div className="font-medium text-ink">{dica.l.rotulos.join(" · ") || "ligação"}</div>
            {dica.l.motivos.length > 0 && <div className="mt-0.5 text-bad">{dica.l.motivos.join("; ")}</div>}
            {dica.l.docs.length > 0 && <div className="mt-0.5 text-muted">{dica.l.docs.map(tituloDoc).join(", ")}</div>}
          </div>
        )}
      </Painel>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5 text-[12px] text-muted">
        {([["valido", "poder válido para este ato"], ["alerta", "válido com alerta"], ["invalido", "sem poder / delegação inválida"],
          ["neutro", "participação societária"]] as [Status, string][]).map(([s, t]) => (
          <span key={s} className="inline-flex items-center gap-1.5">
            <svg width="26" height="8"><line x1="0" y1="4" x2="26" y2="4" stroke={COR[s]} strokeWidth="2.2" strokeDasharray={s === "invalido" ? "5 4" : undefined} /></svg>
            {t}
          </span>
        ))}
        <span className="inline-flex items-center gap-1.5"><span className="inline-block size-3 rounded border-2 border-accent" /> assinante informado</span>
        {simulacao && <span className="inline-flex items-center gap-1.5"><span className="inline-block size-3 rounded border border-dashed border-accent" /> na simulação “E se…?” (clique numa pessoa)</span>}
      </div>
    </div>
  );
}
