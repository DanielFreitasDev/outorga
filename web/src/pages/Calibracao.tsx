import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Info, Save, SlidersHorizontal, Wand2 } from "lucide-react";
import { api } from "../lib/api";
import { useApp } from "../lib/ctx";
import type { Calibracao as TCal, Faixa, ItemCalibracao, Politica, PontoCurva, Sev } from "../lib/types";
import { FAIXA_TXT, VEREDITO_TXT, hash01, pct } from "../lib/format";
import { Botao, CabecalhoPagina, Carregando, ErroCaixa, Painel, Secao, cx } from "../components/ui";

const LIMIAR_RUN_ACEITE = 85, LIMIAR_RUN_RECUSA = 15; // limiares usados quando a avaliação foi gerada

/** Faixa que o item teria com os limiares escolhidos. Alertas e indeterminados ficam sempre na faixa intermediária. */
function faixaCom(it: ItemCalibracao, aceite: number, recusa: number): Faixa {
  const forcado = it.previsto === "INDETERMINADO" ||
    (it.faixa === "AMARELO" && (it.indice >= LIMIAR_RUN_ACEITE || it.indice <= LIMIAR_RUN_RECUSA));
  if (forcado) return "AMARELO";
  if (it.previsto === "PODE" && it.indice >= aceite) return "VERDE";
  if (it.previsto === "NAO_PODE" && it.indice <= recusa) return "VERMELHO";
  return "AMARELO";
}

function metricas(itens: ItemCalibracao[], aceite: number, recusa: number) {
  let verde = 0, vermelho = 0, amarelo = 0, perigosos = 0, caros = 0, errosAuto = 0, segurados = 0;
  for (const it of itens) {
    const f = faixaCom(it, aceite, recusa);
    if (f === "VERDE") {
      verde++;
      if (it.esperado !== "PODE") { perigosos++; errosAuto++; }
    } else if (f === "VERMELHO") {
      vermelho++;
      if (it.esperado !== "NAO_PODE") { errosAuto++; if (it.esperado === "PODE") caros++; }
    } else {
      amarelo++;
      if (it.previsto !== it.esperado) segurados++;
    }
  }
  const n = itens.length || 1;
  const auto = verde + vermelho;
  return { verde, vermelho, amarelo, perigosos, caros, errosAuto, segurados, cobertura: auto / n,
    acertoAuto: auto ? 1 - errosAuto / auto : null };
}

/* ------------------------------------------------------------------------- gráfico principal */
function FaixaInterativa({ itens, aceite, recusa, onAceite, onRecusa }: {
  itens: ItemCalibracao[]; aceite: number; recusa: number; onAceite: (v: number) => void; onRecusa: (v: number) => void;
}) {
  const W = 860, H = 300, X0 = 78, X1 = W - 20, Y0 = 40, Y1 = H - 38;
  const x = (v: number) => X0 + (v / 100) * (X1 - X0);
  const svg = useRef<SVGSVGElement>(null);
  const [arrasto, setArrasto] = useState<"aceite" | "recusa" | null>(null);
  const [dica, setDica] = useState<{ it: ItemCalibracao; px: number; py: number } | null>(null);
  const lanes: Record<string, number> = { PODE: Y0 + 42, INDETERMINADO: (Y0 + Y1) / 2, NAO_PODE: Y1 - 42 };

  const valorDe = useCallback((clientX: number) => {
    const r = svg.current!.getBoundingClientRect();
    const vx = ((clientX - r.left) / r.width) * W;
    return Math.round(Math.max(0, Math.min(100, ((vx - X0) / (X1 - X0)) * 100)));
  }, [X0, X1]);

  const mover = (e: React.PointerEvent) => {
    if (!arrasto) return;
    const v = valorDe(e.clientX);
    if (arrasto === "aceite") onAceite(Math.max(recusa + 1, v));
    else onRecusa(Math.min(aceite - 1, v));
  };

  const Alca = ({ qual, v }: { qual: "aceite" | "recusa"; v: number }) => {
    const cor = qual === "aceite" ? "var(--ok)" : "var(--bad)";
    return (
      <g className="cursor-ew-resize" tabIndex={0} role="slider" aria-label={qual === "aceite" ? "Limiar de aceite" : "Limiar de recusa"}
        aria-valuemin={0} aria-valuemax={100} aria-valuenow={v}
        onPointerDown={(e) => { (e.target as Element).setPointerCapture?.(e.pointerId); setArrasto(qual); }}
        onKeyDown={(e) => {
          const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
          if (!d) return;
          e.preventDefault();
          if (qual === "aceite") onAceite(Math.min(100, Math.max(recusa + 1, v + d)));
          else onRecusa(Math.max(0, Math.min(aceite - 1, v + d)));
        }}>
        <line x1={x(v)} y1={Y0 - 6} x2={x(v)} y2={Y1 + 4} stroke={cor} strokeWidth={2.5} />
        <line x1={x(v)} y1={Y0 - 6} x2={x(v)} y2={Y1 + 4} stroke="transparent" strokeWidth={18} />
        <rect x={x(v) - 33} y={Y0 - 32} width={66} height={24} rx={12} fill={cor} />
        <text x={x(v)} y={Y0 - 15.5} textAnchor="middle" fontSize="12.5" fontWeight={600} fill="#fff" className="num">
          {qual === "aceite" ? "≥" : "≤"} {v}
        </text>
      </g>
    );
  };

  return (
    <div className="relative">
      <svg ref={svg} viewBox={`0 0 ${W} ${H}`} className="w-full touch-none select-none" onPointerMove={mover}
        onPointerUp={() => setArrasto(null)} onPointerLeave={() => setArrasto(null)} role="img"
        aria-label="Distribuição dos casos pelo índice de aceitação, com os limiares das três faixas">
        <rect x={x(0)} y={Y0} width={x(recusa) - x(0)} height={Y1 - Y0} fill="var(--bad-soft)" />
        <rect x={x(recusa)} y={Y0} width={x(aceite) - x(recusa)} height={Y1 - Y0} fill="var(--warn-soft)" />
        <rect x={x(aceite)} y={Y0} width={x(100) - x(aceite)} height={Y1 - Y0} fill="var(--ok-soft)" />
        {x(recusa) - x(0) > 90 && <text x={(x(0) + x(recusa)) / 2} y={Y1 + 24} textAnchor="middle" fontSize="11.5" fill="var(--bad)" fontWeight={600}>RECUSA</text>}
        <text x={(x(recusa) + x(aceite)) / 2} y={Y1 + 24} textAnchor="middle" fontSize="11.5" fill="var(--warn)" fontWeight={600}>
          {x(aceite) - x(recusa) > 260 ? "FAIXA INTERMEDIÁRIA · REVISÃO HUMANA" : "REVISÃO"}
        </text>
        {x(100) - x(aceite) > 90 && <text x={(x(aceite) + x(100)) / 2} y={Y1 + 24} textAnchor="middle" fontSize="11.5" fill="var(--ok)" fontWeight={600}>ACEITE</text>}
        {[0, 25, 50, 75, 100].map((v) => (
          <text key={v} x={x(v)} y={Y1 + 12} textAnchor="middle" fontSize="10" fill="var(--muted)" className="num" opacity={0.85}>{v}</text>
        ))}
        {Object.entries(lanes).map(([k, y]) => (
          <g key={k}>
            <line x1={X0} y1={y} x2={X1} y2={y} stroke="var(--line-strong)" strokeDasharray="2 5" />
            <text x={X0 - 10} y={y + 4} textAnchor="end" fontSize="12" fill="var(--ink-2)">{k === "PODE" ? "pode" : k === "NAO_PODE" ? "não pode" : "indeterm."}</text>
          </g>
        ))}
        {itens.map((it, i) => {
          const f = faixaCom(it, aceite, recusa);
          const auto = f !== "AMARELO";
          const acerto = it.previsto === it.esperado;
          const cor = acerto ? "var(--ok)" : "var(--bad)";
          const jx = (hash01(it.caso + "x") - 0.5) * 3.2;
          const jy = (hash01(it.caso) - 0.5) * 30;
          const cx0 = x(Math.max(0, Math.min(100, it.indice + jx))), cy0 = (lanes[it.previsto] ?? lanes.INDETERMINADO) + jy;
          return (
            <circle key={it.caso + i} cx={cx0} cy={cy0} r={auto ? 6.8 : 6.2} fill={auto ? cor : "var(--surface)"} stroke={cor}
              strokeWidth={auto ? 1.2 : 2.2} className="cursor-pointer"
              onMouseEnter={(e) => setDica({ it, px: e.nativeEvent.offsetX, py: e.nativeEvent.offsetY })} onMouseLeave={() => setDica(null)} />
          );
        })}
        <Alca qual="recusa" v={recusa} />
        <Alca qual="aceite" v={aceite} />
      </svg>
      {dica && (
        <div className="pointer-events-none absolute z-10 w-64 rounded-lg border border-line bg-surface px-3 py-2 text-[12.5px] shadow-pop"
          style={{ left: Math.min(dica.px + 12, 700), top: dica.py + 12 }}>
          <div className="font-medium text-ink">{dica.it.caso}{dica.it.titulo ? ` · ${dica.it.titulo}` : ""}</div>
          <div className="mt-0.5 text-muted">índice <span className="num text-ink">{dica.it.indice}</span> · fonte {dica.it.fonte}</div>
          <div className="mt-0.5">sistema: <b className="font-medium">{VEREDITO_TXT[dica.it.previsto]}</b> · gabarito: <b className="font-medium">{VEREDITO_TXT[dica.it.esperado]}</b></div>
          <div className="mt-0.5">com estes limiares: <b className="font-medium">{FAIXA_TXT[faixaCom(dica.it, aceite, recusa)]}</b></div>
        </div>
      )}
    </div>
  );
}

/* --------------------------------------------------------------------------- curva risco × cobertura */
function CurvaRisco({ titulo, pontos, alfa, atual, lado }: { titulo: string; pontos: PontoCurva[]; alfa: number; atual: number; lado: "aceite" | "recusa" }) {
  const W = 460, H = 170, X0 = 34, X1 = W - 10, Y0 = 12, Y1 = H - 26;
  const dom = lado === "aceite" ? [50, 100] : [0, 50];
  const x = (v: number) => X0 + ((v - dom[0]) / (dom[1] - dom[0])) * (X1 - X0);
  const y = (v: number) => Y1 - v * (Y1 - Y0);
  const pts = pontos.filter((p) => p.limiar >= dom[0] && p.limiar <= dom[1]).sort((a, b) => a.limiar - b.limiar);
  const linha = (f: (p: PontoCurva) => number) => pts.map((p, i) => `${i ? "L" : "M"} ${x(p.limiar).toFixed(1)} ${y(f(p)).toFixed(1)}`).join(" ");
  return (
    <div>
      <div className="mb-1 text-[12.5px] font-medium text-ink-2">{titulo}</div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
        {[0, 0.25, 0.5, 0.75, 1].map((v) => (
          <g key={v}>
            <line x1={X0} y1={y(v)} x2={X1} y2={y(v)} stroke="var(--line)" />
            <text x={X0 - 5} y={y(v) + 3} textAnchor="end" fontSize="9" fill="var(--muted)">{Math.round(v * 100)}%</text>
          </g>
        ))}
        <line x1={X0} y1={y(alfa)} x2={X1} y2={y(alfa)} stroke="var(--bad)" strokeDasharray="4 4" strokeOpacity={0.7} />
        <text x={X1} y={y(alfa) - 3} textAnchor="end" fontSize="9" fill="var(--bad)">α = {Math.round(alfa * 100)}%</text>
        {pts.length > 1 && (
          <>
            <path d={linha((p) => p.cobertura)} fill="none" stroke="var(--accent)" strokeWidth={2} />
            <path d={linha((p) => p.risco_sup)} fill="none" stroke="var(--bad)" strokeWidth={1.6} strokeOpacity={0.85} />
            <path d={linha((p) => p.risco)} fill="none" stroke="var(--warn)" strokeWidth={1.4} strokeDasharray="3 3" />
          </>
        )}
        <line x1={x(atual)} y1={Y0} x2={x(atual)} y2={Y1} stroke="var(--ink)" strokeWidth={1.2} />
        {[dom[0], (dom[0] + dom[1]) / 2, dom[1]].map((v) => (
          <text key={v} x={x(v)} y={H - 10} textAnchor="middle" fontSize="9" fill="var(--muted)" className="num">{v}</text>
        ))}
      </svg>
      <div className="flex flex-wrap gap-x-3 text-[11px] text-muted">
        <span><span className="mr-1 inline-block h-0.5 w-4 bg-accent align-middle" />cobertura</span>
        <span><span className="mr-1 inline-block h-0.5 w-4 bg-warn align-middle" />risco observado</span>
        <span><span className="mr-1 inline-block h-0.5 w-4 bg-bad align-middle" />risco máx. (95%, Clopper-Pearson)</span>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------------------------- página */
const SEVERIDADES: { campo: keyof Politica; rotulo: string; desc: string }[] = [
  { campo: "procuracao_particular_sem_firma", rotulo: "Procuração particular sem firma", desc: "DETRAN-CE exige instrumento público e específico." },
  { campo: "procuracao_particular_com_firma", rotulo: "Procuração particular com firma", desc: "Civilmente válida; o órgão pode exigir a pública." },
  { campo: "idade_max_severidade", rotulo: "Procuração acima da idade máxima", desc: "DETRAN-CE: validade de até 1 ano da expedição." },
  { campo: "substabelecimento_particular", rotulo: "Substabelecimento particular", desc: "CC art. 655 admite; prática conservadora exige a mesma forma." },
  { campo: "procuracao_sem_veiculo_identificado", rotulo: "Procuração sem identificar o veículo", desc: "“Específica para o ato”: entendimento a confirmar." },
  { campo: "crlv_ausente", rotulo: "CRLV não apresentado", desc: "Sem CRLV não dá para conferir a titularidade." },
];
const SEV_OPCOES: { v: Sev; t: string }[] = [
  { v: "bloqueio", t: "Bloqueio (recusa o caminho)" }, { v: "alerta", t: "Alerta (revisão humana)" },
  { v: "atencao", t: "Atenção (reduz o índice)" }, { v: "info", t: "Só informar" },
];

export function Calibracao() {
  const { atualizar } = useApp();
  const [cal, setCal] = useState<TCal | null>(null);
  const [pol, setPol] = useState<Politica | null>(null);
  const [rasc, setRasc] = useState<Politica | null>(null);
  const [alfa, setAlfa] = useState(0.05);
  const [aceite, setAceite] = useState(85);
  const [recusa, setRecusa] = useState(15);
  const [erro, setErro] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [salvoMsg, setSalvoMsg] = useState<string | null>(null);
  const perfilOriginal = useRef<string | null>(null);

  useEffect(() => {
    api.politica().then((p) => {
      setPol(p); setRasc(p); setAceite(p.limiar_aceite); setRecusa(p.limiar_recusa); perfilOriginal.current = p.perfil;
    }).catch((e) => setErro(e.message));
  }, []);
  useEffect(() => { api.calibracao(alfa).then(setCal).catch((e) => setErro(e.message)); }, [alfa]);

  const itens = cal?.itens ?? [];
  const m = useMemo(() => metricas(itens, aceite, recusa), [itens, aceite, recusa]);
  const base = useMemo(() => pol ? metricas(itens, pol.limiar_aceite, pol.limiar_recusa) : null, [itens, pol]);
  const perfilMudou = !!rasc && rasc.perfil !== perfilOriginal.current;
  const alterado = !!pol && !!rasc && (aceite !== pol.limiar_aceite || recusa !== pol.limiar_recusa || perfilMudou ||
    SEVERIDADES.some((s) => rasc[s.campo] !== pol[s.campo]) || rasc.idade_max_procuracao_dias !== pol.idade_max_procuracao_dias);

  async function salvar() {
    if (!rasc) return;
    setSalvando(true);
    setErro(null);
    try {
      const corpo: Partial<Politica> = perfilMudou
        ? { perfil: rasc.perfil, limiar_aceite: aceite, limiar_recusa: recusa }
        : { ...rasc, limiar_aceite: aceite, limiar_recusa: recusa };
      const p = await api.salvarPolitica(corpo);
      setPol(p); setRasc(p); perfilOriginal.current = p.perfil;
      setSalvoMsg("Política salva e registrada na trilha de auditoria. Novas análises já usam estes limiares.");
      setTimeout(() => setSalvoMsg(null), 5000);
      atualizar();
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setSalvando(false);
    }
  }

  const sug = cal?.sugestao, cons = cal?.sugestao_conservadora;
  const delta = (a: number, b: number | undefined, inverso = false, fmt = (v: number) => String(v)) => {
    if (b === undefined || a === b) return null;
    const melhor = inverso ? a < b : a > b;
    return <span className={cx("ml-1 text-[11.5px]", melhor ? "text-ok" : "text-bad")}>{a > b ? "+" : ""}{fmt(a - b)}</span>;
  };

  return (
    <div>
      <CabecalhoPagina titulo="Faixa intermediária de aceitação"
        sub={<>A IA só decide sozinha quando está segura; o resto vai para o servidor revisar. Arraste os limiares e veja, nos
          casos do corpus e nas revisões já registradas, quantos casos ficam automáticos e quantos erros escapariam.</>}
        acoes={<Botao variante="primario" icone={<Save className="size-4" />} disabled={!alterado} carregando={salvando} onClick={salvar}>Salvar política</Botao>} />
      {erro && <div className="mb-4"><ErroCaixa mensagem={erro} /></div>}
      {salvoMsg && <div className="mb-4 rounded-lg border border-ok/40 bg-ok-soft px-4 py-2.5 text-[13.5px] text-ok">{salvoMsg}</div>}
      {!cal || !pol ? <Carregando /> : (
        <>
          <div className="grid items-start gap-5 xl:grid-cols-[1fr_300px]">
            <Painel className="p-4 md:p-5">
              <div className="mb-2 flex flex-wrap items-center gap-2 text-[12.5px] text-muted">
                <SlidersHorizontal className="size-4" />
                {itens.length} casos rotulados · avaliação <span className="font-mono">{cal.run ?? "—"}</span>
                {itens.some((i) => i.fonte === "revisao") && ` · inclui ${itens.filter((i) => i.fonte === "revisao").length} revisão(ões) humana(s)`}
              </div>
              <FaixaInterativa itens={itens} aceite={aceite} recusa={recusa} onAceite={setAceite} onRecusa={setRecusa} />
              <div className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1.5 text-[12px] text-muted">
                <span className="inline-flex items-center gap-1.5"><span className="inline-block size-3 rounded-full bg-ok" />acerto decidido automaticamente</span>
                <span className="inline-flex items-center gap-1.5"><span className="inline-block size-3 rounded-full border-2 border-ok" />acerto enviado à revisão</span>
                <span className="inline-flex items-center gap-1.5"><span className="inline-block size-3 rounded-full bg-bad" />erro que escaparia</span>
                <span className="inline-flex items-center gap-1.5"><span className="inline-block size-3 rounded-full border-2 border-bad" />erro segurado pela faixa intermediária</span>
              </div>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <label className="text-[12.5px] font-medium text-ink-2">
                  Recusa automática até <span className="num text-bad">{recusa}</span>
                  <input type="range" min={0} max={99} value={recusa} onChange={(e) => setRecusa(Math.min(aceite - 1, Number(e.target.value)))}
                    className="mt-1 block w-full accent-[var(--bad)]" />
                </label>
                <label className="text-[12.5px] font-medium text-ink-2">
                  Aceite automático a partir de <span className="num text-ok">{aceite}</span>
                  <input type="range" min={1} max={100} value={aceite} onChange={(e) => setAceite(Math.max(recusa + 1, Number(e.target.value)))}
                    className="mt-1 block w-full accent-[var(--ok)]" />
                </label>
              </div>
            </Painel>
            <div className="space-y-3">
              <Painel className="p-4">
                <div className="text-[11.5px] font-medium uppercase tracking-wide text-muted">Com estes limiares</div>
                <div className="mt-3 grid grid-cols-2 gap-x-3 gap-y-4">
                  <div><div className="num text-[24px] font-semibold leading-none text-ink">{pct(m.cobertura)}{delta(Math.round(m.cobertura * 100), base ? Math.round(base.cobertura * 100) : undefined, false, (v) => `${v} p.p.`)}</div><div className="mt-1 text-[12px] text-muted">decidido sozinho</div></div>
                  <div><div className="num text-[24px] font-semibold leading-none text-warn">{m.amarelo}{delta(m.amarelo, base?.amarelo, true)}</div><div className="mt-1 text-[12px] text-muted">para revisão humana</div></div>
                  <div><div className={cx("num text-[24px] font-semibold leading-none", m.perigosos ? "text-bad" : "text-ok")}>{m.perigosos}{delta(m.perigosos, base?.perigosos, true)}</div><div className="mt-1 text-[12px] text-muted">erros perigosos <span className="block text-[11px]">aceite indevido</span></div></div>
                  <div><div className={cx("num text-[24px] font-semibold leading-none", m.caros ? "text-warn" : "text-ink")}>{m.caros}{delta(m.caros, base?.caros, true)}</div><div className="mt-1 text-[12px] text-muted">erros caros <span className="block text-[11px]">recusa indevida</span></div></div>
                </div>
                <div className="mt-4 border-t border-line pt-3 text-[12.5px] text-ink-2">
                  Acerto na faixa automática: <b className="num">{m.acertoAuto === null ? "—" : pct(m.acertoAuto, 1)}</b>
                  <div className="mt-0.5 text-muted">{m.segurados} erro(s) da IA ficam retidos na faixa intermediária.</div>
                </div>
              </Painel>
              <Painel className="p-4">
                <div className="flex items-center justify-between">
                  <div className="text-[11.5px] font-medium uppercase tracking-wide text-muted">Sugestão estatística</div>
                  <select value={alfa} onChange={(e) => setAlfa(Number(e.target.value))} aria-label="Risco máximo α"
                    className="h-7 rounded border border-line-strong bg-surface px-1.5 text-[12px] text-ink">
                    {[0.01, 0.02, 0.05, 0.1].map((a) => <option key={a} value={a}>α = {Math.round(a * 100)}%</option>)}
                  </select>
                </div>
                <div className="mt-2 space-y-2 text-[12.5px]">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-ink-2">Risco observado ≤ α: <b className="num">{sug?.aceite ? `≥ ${sug.aceite.limiar}` : "—"} / {sug?.recusa ? `≤ ${sug.recusa.limiar}` : "—"}</b></span>
                    <Botao tamanho="sm" icone={<Wand2 className="size-3.5" />} disabled={!sug?.aceite || !sug?.recusa}
                      onClick={() => { if (sug?.aceite && sug?.recusa) { setAceite(Math.max(sug.aceite.limiar, sug.recusa.limiar + 1)); setRecusa(Math.min(sug.recusa.limiar, sug.aceite.limiar - 1)); } }}>Aplicar</Botao>
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-ink-2">Conservadora (95%): <b className="num">{cons?.aceite ? `≥ ${cons.aceite.limiar}` : "—"} / {cons?.recusa ? `≤ ${cons.recusa.limiar}` : "—"}</b></span>
                    <Botao tamanho="sm" icone={<Wand2 className="size-3.5" />} disabled={!cons?.aceite || !cons?.recusa}
                      onClick={() => { if (cons?.aceite && cons?.recusa) { setAceite(Math.max(cons.aceite.limiar, cons.recusa.limiar + 1)); setRecusa(Math.min(cons.recusa.limiar, cons.aceite.limiar - 1)); } }}>Aplicar</Botao>
                  </div>
                  {(!cons?.aceite || !cons?.recusa) && (
                    <div className="flex gap-1.5 text-[11.5px] text-muted"><Info className="mt-0.5 size-3.5 shrink-0" />Com poucos casos rotulados o limite de Clopper-Pearson fica largo: o sistema só se torna mais automático à medida que prova que acerta.</div>
                  )}
                </div>
              </Painel>
            </div>
          </div>

          {sug && (
            <Secao titulo="Risco × cobertura" descricao="Quanto mais automático (cobertura), maior o risco. A linha vertical é o limiar escolhido; a tracejada vermelha, o risco máximo aceito (α).">
              <Painel className="grid gap-6 p-5 md:grid-cols-2">
                <CurvaRisco titulo="Aceite automático (limiar de aceite)" pontos={sug.curva_aceite} alfa={alfa} atual={aceite} lado="aceite" />
                <CurvaRisco titulo="Recusa automática (limiar de recusa)" pontos={sug.curva_recusa} alfa={alfa} atual={recusa} lado="recusa" />
              </Painel>
            </Secao>
          )}

          {rasc && (
            <Secao titulo="Regras da política" descricao="O que cada exigência administrativa provoca na análise. O perfil DETRAN-CE segue a página do serviço de transferência do órgão.">
              <Painel className="p-5">
                <div className="flex flex-wrap items-end gap-4">
                  <label className="text-[12.5px] font-medium text-ink-2">
                    Perfil
                    <select value={rasc.perfil} onChange={(e) => setRasc({ ...rasc, perfil: e.target.value })}
                      className="mt-1 block h-9 rounded-md border border-line-strong bg-surface px-2.5 text-[13.5px] text-ink">
                      <option value="ce">DETRAN-CE (exigências administrativas do órgão)</option>
                      <option value="generica">Genérica (só o Código Civil)</option>
                    </select>
                  </label>
                  <label className="text-[12.5px] font-medium text-ink-2">
                    Idade máxima da procuração (dias)
                    <input type="number" min={1} value={rasc.idade_max_procuracao_dias} disabled={perfilMudou}
                      onChange={(e) => setRasc({ ...rasc, idade_max_procuracao_dias: Number(e.target.value) })}
                      className="mt-1 block h-9 w-28 rounded-md border border-line-strong bg-surface px-2.5 text-[13.5px] text-ink disabled:opacity-50" />
                  </label>
                  {perfilMudou && <div className="text-[12.5px] text-warn">Salve para carregar as regras padrão do novo perfil.</div>}
                </div>
                <div className="mt-4 divide-y divide-line rounded-lg border border-line">
                  {SEVERIDADES.map((s) => (
                    <div key={s.campo} className="flex flex-wrap items-center gap-3 px-4 py-2.5">
                      <div className="min-w-[240px] flex-1">
                        <div className="text-[13.5px] text-ink">{s.rotulo}</div>
                        <div className="text-[12px] text-muted">{s.desc}</div>
                      </div>
                      <select value={String(rasc[s.campo])} disabled={perfilMudou} aria-label={s.rotulo}
                        onChange={(e) => setRasc({ ...rasc, [s.campo]: e.target.value as Sev })}
                        className="h-8 rounded-md border border-line-strong bg-surface px-2 text-[13px] text-ink disabled:opacity-50">
                        {SEV_OPCOES.map((o) => <option key={o.v} value={o.v}>{o.t}</option>)}
                      </select>
                    </div>
                  ))}
                </div>
              </Painel>
            </Secao>
          )}
        </>
      )}
    </div>
  );
}
