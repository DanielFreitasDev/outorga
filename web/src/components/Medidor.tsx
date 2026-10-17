import type { Faixa } from "../lib/types";

/** Medidor semicircular do índice de aceitação (0–100) com as três zonas da política. */
export function Medidor({ indice, aceite, recusa, faixa, tamanho = 210 }: {
  indice: number; aceite: number; recusa: number; faixa: Faixa; tamanho?: number;
}) {
  const cx = 110, cy = 112, r = 88, w = 16;
  const ang = (v: number) => Math.PI - (Math.max(0, Math.min(100, v)) / 100) * Math.PI;
  const ponto = (v: number, raio = r) => [cx + raio * Math.cos(ang(v)), cy - raio * Math.sin(ang(v))];
  const arco = (a: number, b: number) => {
    const [x1, y1] = ponto(a);
    const [x2, y2] = ponto(b);
    return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 0 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`;
  };
  const [mx, my] = ponto(indice, r);
  const cor = faixa === "VERDE" ? "var(--ok)" : faixa === "VERMELHO" ? "var(--bad)" : "var(--warn)";
  const marca = (v: number) => {
    const [x1, y1] = ponto(v, r + w / 2 + 2);
    const [x2, y2] = ponto(v, r + w / 2 + 9);
    const [tx, ty] = ponto(v, r + w / 2 + 19);
    return (
      <g key={v}>
        <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--muted)" strokeWidth={1.4} />
        <text x={tx} y={ty + 3} textAnchor="middle" fontSize="9.5" fill="var(--muted)" className="num">{v}</text>
      </g>
    );
  };
  return (
    <svg viewBox="0 -6 220 146" width={tamanho} height={(tamanho * 146) / 220} role="img"
      aria-label={`Índice de aceitação ${indice.toFixed(0)} de 100; recusa até ${recusa}, aceite a partir de ${aceite}`}>
      <path d={arco(0, recusa)} stroke="var(--zona-bad)" strokeWidth={w} fill="none" />
      <path d={arco(recusa, aceite)} stroke="var(--zona-warn)" strokeWidth={w} fill="none" />
      <path d={arco(aceite, 100)} stroke="var(--zona-ok)" strokeWidth={w} fill="none" />
      {marca(recusa)}
      {marca(aceite)}
      <circle cx={mx} cy={my} r={11} fill="var(--surface)" stroke="var(--ink)" strokeWidth={2.4} />
      <circle cx={mx} cy={my} r={5} fill={cor} />
      <text x={cx} y={cy - 18} textAnchor="middle" fontSize="34" fontWeight="600" fill="var(--ink)" className="num">
        {Math.round(indice)}
      </text>
      <text x={cx} y={cy - 2} textAnchor="middle" fontSize="8.6" fill="var(--muted)" letterSpacing="0.4">ÍNDICE DE ACEITAÇÃO</text>
      <text x={22} y={136} textAnchor="middle" fontSize="8.5" fill="var(--muted)">0</text>
      <text x={198} y={136} textAnchor="middle" fontSize="8.5" fill="var(--muted)">100</text>
    </svg>
  );
}

/** Barra horizontal compacta do índice (listas). */
export function BarraIndice({ indice, faixa }: { indice: number | null; faixa: Faixa | null }) {
  if (indice === null) return <span className="text-muted">—</span>;
  const cor = faixa === "VERDE" ? "bg-ok" : faixa === "VERMELHO" ? "bg-bad" : "bg-warn";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-surface-3">
        <div className={`h-full ${cor}`} style={{ width: `${Math.max(3, indice)}%` }} />
      </div>
      <span className="num text-[12px] text-ink-2">{Math.round(indice)}</span>
    </div>
  );
}
