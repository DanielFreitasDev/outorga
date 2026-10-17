import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, ChevronDown, History, RefreshCw, Sparkles, XCircle } from "lucide-react";
import { api } from "../lib/api";
import { Link, navegar } from "../lib/router";
import { useApp } from "../lib/ctx";
import { LADOS, type AnaliseCompleta, type CasoDemo, type Lado, type Resultado } from "../lib/types";
import { FAIXA_TXT, LADO_TXT, VEREDITO_TXT, dataHoraBR } from "../lib/format";
import { Botao, Carregando, ErroCaixa, Painel, SeloFaixa, cx } from "../components/ui";
import { VisaoResultado } from "./resultado/Resultado";
import { AgenteAoVivo, TimelineAgente } from "./AgenteAoVivo";

function Voltar({ href, rotulo }: { href: string; rotulo: string }) {
  return (
    <Link href={href} className="mb-4 inline-flex items-center gap-1.5 text-[13px] text-muted hover:text-accent">
      <ArrowLeft className="size-4" /> {rotulo}
    </Link>
  );
}

export function PaginaAnalise({ id }: { id: string }) {
  const [a, setA] = useState<AnaliseCompleta | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [rastro, setRastro] = useState(false);
  const [reproc, setReproc] = useState(false);
  const { atualizar } = useApp();

  const carregar = useCallback(() => {
    api.analise(id).then(setA).catch((e) => setErro(e.message));
  }, [id]);

  useEffect(() => { carregar(); }, [carregar]);

  if (erro) return <><Voltar href="/historico" rotulo="Histórico" /><ErroCaixa mensagem={erro} /></>;
  if (!a) return <Carregando texto="Carregando análise…" />;

  if (a.status === "processando") {
    return (
      <div>
        <Voltar href="/" rotulo="Demonstração" />
        <h1 className="mb-1 text-[20px] font-semibold text-ink">Análise {a.caso_demo ? `do cenário ${a.caso_demo}` : "em andamento"}</h1>
        <p className="mb-5 text-[13.5px] text-muted">Placa {a.placa ?? "—"} · iniciada {dataHoraBR(a.criado_em)} · {a.provedor}</p>
        <AgenteAoVivo id={id} onFim={() => { carregar(); atualizar(); }} />
      </div>
    );
  }

  if (a.status === "erro" || !a.resultado) {
    return (
      <div>
        <Voltar href="/historico" rotulo="Histórico" />
        <ErroCaixa mensagem={`A análise falhou: ${a.erro ?? "erro desconhecido"}`} />
        {a.eventos.length > 0 && <Painel className="mt-4 p-5"><TimelineAgente eventos={a.eventos} encerrado /></Painel>}
      </div>
    );
  }

  const topo = (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div>
        <Voltar href={a.caso_demo ? "/" : "/historico"} rotulo={a.caso_demo ? "Demonstração" : "Histórico"} />
        <div className="text-[13px] text-muted">
          Análise <span className="font-mono">{a.id}</span>{a.caso_demo && <> · cenário {a.caso_demo}</>} · {dataHoraBR(a.criado_em)}
          {a.duracao_s ? <> · {a.duracao_s.toFixed(0)} s de leitura</> : null}
        </div>
      </div>
      <div className="flex gap-2">
        {a.eventos.length > 0 && (
          <Botao tamanho="sm" variante="fantasma" icone={<History className="size-4" />} onClick={() => setRastro((v) => !v)}>
            Rastro do agente <ChevronDown className={cx("size-3.5 transition", rastro && "rotate-180")} />
          </Botao>
        )}
        <Botao tamanho="sm" icone={<RefreshCw className="size-4" />} carregando={reproc} title="Reaplicar o motor com a política atual (sem reler os documentos)"
          onClick={async () => {
            setReproc(true);
            try { await api.reprocessar(id); carregar(); } catch (e) { setErro((e as Error).message); } finally { setReproc(false); }
          }}>Reprocessar com a política atual</Botao>
      </div>
    </div>
  );

  return (
    <div>
      {topo}
      {rastro && <Painel className="mb-4 p-5"><TimelineAgente eventos={a.eventos} encerrado /></Painel>}
      <VisaoResultado r={a.resultado} origem={{ tipo: "analise", id, analise: a, recarregar: carregar }} />
    </div>
  );
}

function ComparacaoGabarito({ r, caso, perfil }: { r: Resultado; caso: CasoDemo; perfil?: string }) {
  const esp = perfil !== "generica" && caso.esperado_ce ? caso.esperado_ce : caso.esperado;
  const lados = LADOS.filter((l) => caso.esperado_lados?.[l]);
  const okLado = (l: Lado) => {
    const e = caso.esperado_lados![l]!;
    const rl = r.lados?.[l];
    return !!rl && rl.veredito === e.veredito && e.faixas_aceitaveis.includes(rl.faixa);
  };
  const okV = esp.veredito === r.veredito;
  const okF = esp.faixas_aceitaveis.includes(r.faixa);
  const ok = okV && okF && lados.every(okLado);
  return (
    <Painel className={cx("mb-4 px-5 py-3.5", ok ? "border-ok/40" : "border-bad/40")}>
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
        <div className="flex items-center gap-2">
          {ok ? <CheckCircle2 className="size-5 text-ok" /> : <XCircle className="size-5 text-bad" />}
          <div>
            <div className="text-[13.5px] font-medium text-ink">{caso.id} · {caso.titulo}</div>
            <div className="text-[12.5px] text-muted">{caso.objetivo}</div>
          </div>
        </div>
        <div className="ml-auto flex flex-wrap items-center gap-4 text-[12.5px]">
          <div>
            <div className="text-muted">Gabarito</div>
            <div className="flex items-center gap-1.5 text-ink">{VEREDITO_TXT[esp.veredito]} · {esp.faixas_aceitaveis.map((f) => FAIXA_TXT[f]).join(" ou ")}</div>
          </div>
          <div>
            <div className="text-muted">Sistema</div>
            <div className="flex items-center gap-1.5"><span className="text-ink">{VEREDITO_TXT[r.veredito]}</span><SeloFaixa faixa={r.faixa} /></div>
          </div>
        </div>
      </div>
      {lados.length > 0 && (
        <div className="mt-2.5 grid gap-2 border-t border-line pt-2.5 sm:grid-cols-2">
          {lados.map((l) => {
            const e = caso.esperado_lados![l]!;
            const rl = r.lados?.[l];
            return (
              <div key={l} className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[12.5px]">
                {okLado(l) ? <CheckCircle2 className="size-4 text-ok" /> : <XCircle className="size-4 text-bad" />}
                <b className="font-medium text-ink">{LADO_TXT[l]}</b>
                <span className="text-muted">gabarito {VEREDITO_TXT[e.veredito].toLowerCase()} · {e.faixas_aceitaveis.map((f) => FAIXA_TXT[f]).join(" ou ")}</span>
                <span className="text-muted">→ sistema</span>
                {rl ? <><span className="text-ink">{VEREDITO_TXT[rl.veredito].toLowerCase()}</span><SeloFaixa faixa={rl.faixa} /></> : <span className="text-bad">lado não verificado</span>}
              </div>
            );
          })}
        </div>
      )}
    </Painel>
  );
}

export function PaginaPrecalculado({ caso }: { caso: string }) {
  const { politica } = useApp();
  const [dados, setDados] = useState<{ run: string; resultado: Resultado } | null>(null);
  const [info, setInfo] = useState<CasoDemo | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [rodando, setRodando] = useState(false);

  useEffect(() => {
    api.precalculado(caso).then(setDados).catch((e) => setErro(e.message));
    api.demo().then((l) => setInfo(l.find((c) => c.id === caso) ?? null)).catch(() => undefined);
  }, [caso]);

  async function rodar() {
    setRodando(true);
    try {
      const r = await api.analisarDemo(caso);
      navegar(`/analise/${r.id}`);
    } catch (e) {
      setErro((e as Error).message);
      setRodando(false);
    }
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <Voltar href="/" rotulo="Demonstração" />
          <div className="text-[13px] text-muted">
            Resultado pré-calculado do cenário <b className="text-ink-2">{caso}</b>
            {dados && <> · avaliação <span className="font-mono">{dados.run}</span>{dados.run.startsWith("oraculo") && " (leitura de gabarito, sem IA)"}</>}
          </div>
        </div>
        <Botao variante="primario" icone={<Sparkles className="size-4" />} carregando={rodando} onClick={rodar}>Rodar agora com a IA local</Botao>
      </div>
      {erro && <ErroCaixa mensagem={erro} />}
      {!dados && !erro && <Carregando texto="Carregando resultado…" />}
      {dados && (
        <VisaoResultado r={dados.resultado} origem={{ tipo: "precalculado", caso, run: dados.run }}
          extraTopo={info ? <ComparacaoGabarito r={dados.resultado} caso={info} perfil={politica?.perfil} /> : undefined} />
      )}
    </div>
  );
}
