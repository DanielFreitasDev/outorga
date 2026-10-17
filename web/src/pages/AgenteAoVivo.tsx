import { useEffect, useMemo, useRef, useState } from "react";
import { Bot, Check, CircleAlert, FileSearch, FileText, Gavel, Layers, Loader2, ScanText, Scale } from "lucide-react";
import type { EventoAgente } from "../lib/types";
import { FAIXA_TXT, TAREFA_TXT } from "../lib/format";
import { Painel, cx } from "../components/ui";

interface Tarefa { tarefa: string; fim?: EventoAgente; amostra?: EventoAgente; inicio: EventoAgente }
interface BlocoDoc { doc: string; nome: string; i: number; n: number; classificado?: EventoAgente; tarefas: Tarefa[]; t: number }

function montar(eventos: EventoAgente[]) {
  const docs: BlocoDoc[] = [];
  const gerais: EventoAgente[] = [];
  for (const e of eventos) {
    const doc = typeof e.doc === "string" ? e.doc : undefined;
    if (e.tipo === "documento_inicio") {
      docs.push({ doc: String(e.doc), nome: String(e.nome), i: Number(e.i), n: Number(e.n), tarefas: [], t: e.t });
      continue;
    }
    const bloco = doc ? [...docs].reverse().find((d) => d.doc === doc) : undefined;
    if (bloco && e.tipo === "classificado") bloco.classificado = e;
    else if (bloco && e.tipo === "tarefa_inicio") bloco.tarefas.push({ tarefa: String(e.tarefa), inicio: e });
    else if (e.tipo === "amostra") {
      const ult = docs[docs.length - 1]?.tarefas.findLast((t) => t.tarefa === e.tarefa && !t.fim);
      if (ult) ult.amostra = e;
    } else if (bloco && e.tipo === "tarefa_fim") {
      const t = bloco.tarefas.findLast((x) => x.tarefa === e.tarefa && !x.fim);
      if (t) t.fim = e;
      else bloco.tarefas.push({ tarefa: String(e.tarefa), inicio: e, fim: e });
    } else if (!doc || !bloco) gerais.push(e);
  }
  return { docs, gerais };
}

function Linha({ icone, children, ativo, ok, erro }: { icone: React.ReactNode; children: React.ReactNode; ativo?: boolean; ok?: boolean; erro?: boolean }) {
  return (
    <div className="surgir flex gap-3">
      <div className={cx("mt-0.5 grid size-6 shrink-0 place-items-center rounded-full border",
        erro ? "border-bad/40 bg-bad-soft text-bad" : ok ? "border-ok/40 bg-ok-soft text-ok" : ativo ? "border-accent/40 bg-accent-soft text-accent" : "border-line bg-surface-2 text-muted")}>
        {ativo ? <Loader2 className="size-3.5 animate-spin" /> : icone}
      </div>
      <div className="min-w-0 flex-1 pb-3 text-[13.5px] text-ink-2">{children}</div>
    </div>
  );
}

export function TimelineAgente({ eventos, encerrado }: { eventos: EventoAgente[]; encerrado: boolean }) {
  const { docs, gerais } = useMemo(() => montar(eventos), [eventos]);
  const inicio = gerais.find((e) => e.tipo === "inicio");
  const fila = gerais.find((e) => e.tipo === "na_fila");
  const consol = gerais.find((e) => e.tipo === "consolidando");
  const conf = gerais.find((e) => e.tipo === "conferencia");
  const motor = gerais.find((e) => e.tipo === "motor");
  const fim = gerais.find((e) => e.tipo === "concluido");
  const erro = gerais.find((e) => e.tipo === "erro");
  return (
    <div>
      {fila && !inicio && (
        <Linha icone={<Layers className="size-3.5" />} ativo={!encerrado}>Na fila de processamento (posição {String(fila.posicao)}).</Linha>
      )}
      {inicio && (
        <Linha icone={<Bot className="size-3.5" />} ok>
          <b className="text-ink">{String(inicio.documentos)} documento(s)</b> para ler · IA {String(inicio.provedor)} ·{" "}
          <span className="font-mono text-[12.5px]">{String(inicio.modelo)}</span> · política {String(inicio.politica)}
        </Linha>
      )}
      {docs.map((d) => {
        const c = d.classificado;
        const ocr = c && (c.metodo === "ocr" || c.metodo === "misto");
        const emAndamento = !encerrado && (!c || d.tarefas.some((t) => !t.fim)) && d === docs[docs.length - 1] && !consol;
        return (
          <div key={d.doc + d.t} className="surgir mb-1 ml-3 border-l border-line pl-5">
            <div className="-ml-[34px] mb-2 flex items-center gap-2">
              <div className={cx("grid size-6 place-items-center rounded-full border bg-surface",
                emAndamento ? "border-accent text-accent" : "border-line-strong text-ink-2")}>
                <FileText className="size-3.5" />
              </div>
              <div className="text-[13.5px]">
                <span className="text-muted">Documento {d.i}/{d.n} · </span>
                <span className="font-medium text-ink">{d.nome}</span>
              </div>
            </div>
            {c && (
              <Linha icone={ocr ? <ScanText className="size-3.5" /> : <FileSearch className="size-3.5" />} ok>
                Reconhecido como <b className="text-ink">{String(c.titulo)}</b> · {String(c.paginas)} página(s) ·{" "}
                {ocr ? <>digitalizado, OCR com {Math.round(Number(c.ocr_confianca ?? 0))}% de confiança</> : "texto digital"}
              </Linha>
            )}
            {d.tarefas.map((t, k) => (
              <Linha key={k} icone={<Check className="size-3.5" />} ativo={!t.fim && !encerrado} ok={!!t.fim}>
                <div className="flex flex-wrap items-baseline gap-x-2">
                  <span className={t.fim ? "text-ink-2" : "text-ink"}>{TAREFA_TXT[t.tarefa] ?? t.tarefa}</span>
                  {t.fim && typeof t.fim.segundos === "number" && (
                    <span className="num text-[12px] text-muted">
                      {t.fim.metodo === "regex" ? "leitura direta dos campos" : `${Number(t.fim.segundos).toFixed(1)} s`}
                      {typeof t.fim.amostras === "number" && Number(t.fim.amostras) > 1 &&
                        ` · ${t.fim.amostras} amostras, concordância ${Math.round(Number(t.fim.concordancia) * 100)}%`}
                    </span>
                  )}
                  {!t.fim && t.amostra && <span className="num text-[12px] text-muted">amostra {String(t.amostra.i)}/{String(t.amostra.n)}</span>}
                </div>
                {t.fim && typeof t.fim.resumo === "string" && t.fim.resumo && (
                  <div className="digitar mt-1 rounded-md border-l-2 border-accent/60 bg-surface-2 px-2.5 py-1.5 font-mono text-[12.5px] text-ink">
                    {t.fim.resumo}
                  </div>
                )}
              </Linha>
            ))}
          </div>
        );
      })}
      {consol && (
        <Linha icone={<Layers className="size-3.5" />} ativo={!conf && !encerrado} ok={!!conf}>
          Consolidando os fatos: mesma pessoa em documentos diferentes (CPF/nome), datas, e cada citação da IA conferida no
          texto original.
        </Linha>
      )}
      {conf && (
        <Linha icone={<Scale className="size-3.5" />} ok>
          Conferência léxica: {String(conf.regras)} cláusula(s) lida(s),{" "}
          <b className={Number(conf.correcoes_lexicas) ? "text-warn" : "text-ink"}>{String(conf.correcoes_lexicas)} correção(ões)</b> da leitura da IA.
        </Linha>
      )}
      {motor && (
        <Linha icone={<Gavel className="size-3.5" />} ok>
          Motor de regras jurídicas: regime vigente na data da venda, especialidade das cláusulas e cadeia de procurações →{" "}
          <b className="text-ink">{String(motor.alternativas)} caminho(s) válido(s)</b>, {String(motor.invalidos)} inválido(s).
        </Linha>
      )}
      {fim && (
        <Linha icone={<Check className="size-3.5" />} ok>
          Concluído em <span className="num">{fim.t.toFixed(1)} s</span>: <b className="text-ink">{FAIXA_TXT[fim.faixa as "VERDE"] ?? String(fim.faixa)}</b>{" "}
          (índice {Math.round(Number(fim.indice))}).
        </Linha>
      )}
      {erro && (
        <Linha icone={<CircleAlert className="size-3.5" />} erro>
          <b className="text-bad">Falhou:</b> {String(erro.mensagem)}
        </Linha>
      )}
    </div>
  );
}

/** Painel ao vivo: assina o SSE da análise e chama onFim quando termina. */
export function AgenteAoVivo({ id, onFim }: { id: string; onFim: () => void }) {
  const [eventos, setEventos] = useState<EventoAgente[]>([]);
  const [encerrado, setEncerrado] = useState(false);
  const [agora, setAgora] = useState(Date.now());
  const t0 = useRef(Date.now());
  const fimRef = useRef(onFim);
  fimRef.current = onFim;

  useEffect(() => {
    const es = new EventSource(`/api/analises/${id}/eventos`);
    const vistos = new Set<number>();
    es.addEventListener("progresso", (ev) => {
      try {
        const d = JSON.parse((ev as MessageEvent).data) as EventoAgente;
        if (vistos.has(d.seq)) return;
        vistos.add(d.seq);
        setEventos((x) => [...x, d]);
      } catch {
        /* evento malformado: ignora */
      }
    });
    es.addEventListener("fim", () => {
      es.close();
      setEncerrado(true);
      fimRef.current();  // sem setTimeout: abas em segundo plano têm temporizadores atrasados pelo navegador
    });
    es.onerror = () => {
      /* o EventSource reconecta sozinho; se a análise já terminou, o servidor manda "fim" */
    };
    const tick = setInterval(() => setAgora(Date.now()), 500);
    return () => {
      es.close();
      clearInterval(tick);
    };
  }, [id]);

  const ultimoT = eventos.length ? eventos[eventos.length - 1].t : 0;
  const decorrido = Math.max((agora - t0.current) / 1000, ultimoT);
  return (
    <Painel className="p-5 md:p-6">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="grid size-9 place-items-center rounded-lg bg-accent-soft text-accent">
            <Bot className="size-5" />
          </div>
          <div>
            <div className="font-semibold text-ink">{encerrado ? "Leitura concluída" : "O agente está lendo os documentos"}</div>
            <div className="text-[12.5px] text-muted">Leitura semântica por IA local, conferida por regras jurídicas determinísticas</div>
          </div>
        </div>
        <div className="num rounded-md border border-line bg-surface-2 px-2.5 py-1 font-mono text-[13px] text-ink-2">
          {Math.floor(decorrido / 60)}:{String(Math.floor(decorrido % 60)).padStart(2, "0")}
        </div>
      </div>
      <TimelineAgente eventos={eventos} encerrado={encerrado} />
      {!eventos.length && <div className="flex items-center gap-2 text-muted"><Loader2 className="size-4 animate-spin" /> conectando…</div>}
    </Painel>
  );
}
