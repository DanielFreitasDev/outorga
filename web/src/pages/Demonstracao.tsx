import { useEffect, useMemo, useState } from "react";
import { Bot, Car, Eye, FileText, Search, Sparkles } from "lucide-react";
import { api } from "../lib/api";
import { Link, navegar } from "../lib/router";
import { useApp } from "../lib/ctx";
import { LADOS, type CasoDemo, type Esperado, type ResumoAvaliacao } from "../lib/types";
import { CATEGORIA_CURTA, CATEGORIA_ORDEM, CATEGORIA_TXT, LADO_TXT, pct } from "../lib/format";
import { Botao, CabecalhoPagina, Carregando, ChipVeredito, ErroCaixa, Painel, SeloFaixa, cx } from "../components/ui";

const AUDIO = new Set(["C13", "C14", "C15"]);

function esperadoDe(c: CasoDemo, perfil: string | undefined): Esperado {
  return perfil !== "generica" && c.esperado_ce ? c.esperado_ce : c.esperado;
}

function PlacarAvaliacao({ r }: { r: ResumoAvaliacao }) {
  const itens = [
    { rot: "vereditos corretos", val: `${r.veredito_correto}/${r.casos}` },
    { rot: "faixa adequada", val: `${r.faixa_aceitavel}/${r.casos}` },
    { rot: "erros perigosos", val: String(r.erros_perigosos), destaque: r.erros_perigosos === 0 ? "text-ok" : "text-bad" },
    { rot: "decidido automaticamente", val: pct(r.cobertura_automatica) },
  ];
  return (
    <Painel className="mb-6 flex flex-wrap items-center gap-x-8 gap-y-3 px-5 py-4">
      <div className="min-w-[200px]">
        <div className="text-[12px] font-medium uppercase tracking-wide text-muted">
          Última avaliação {r.modo === "llm" ? "com a IA local" : "do motor (leitura de gabarito)"}
        </div>
        <div className="text-[12.5px] text-muted">{r.run} · política {r.politica?.nome ?? "—"}</div>
      </div>
      {itens.map((i) => (
        <div key={i.rot}>
          <div className={cx("num text-[22px] font-semibold leading-none", i.destaque ?? "text-ink")}>{i.val}</div>
          <div className="mt-1 text-[12px] text-muted">{i.rot}</div>
        </div>
      ))}
    </Painel>
  );
}

export function Demonstracao() {
  const { politica } = useApp();
  const nomePolitica = politica?.nome;
  const [casos, setCasos] = useState<CasoDemo[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [filtro, setFiltro] = useState<string>("todas");
  const [busca, setBusca] = useState("");
  const [rodando, setRodando] = useState<string | null>(null);
  const [placar, setPlacar] = useState<ResumoAvaliacao | null>(null);

  useEffect(() => {
    api.demo().then(setCasos).catch((e) => setErro(e.message));
  }, []);

  useEffect(() => {
    api.avaliacoes().then((runs) => {
      const mesma = (r: ResumoAvaliacao) => !nomePolitica || r.politica?.nome === nomePolitica;
      const llm = runs.find((r) => r.modo === "llm" && r.casos >= 30 && mesma(r)) ?? runs.find((r) => r.modo === "llm" && r.casos >= 30);
      setPlacar(llm ?? runs.find((r) => r.modo === "oraculo" && mesma(r)) ?? runs.find((r) => r.modo === "oraculo") ?? null);
    }).catch(() => undefined);
  }, [nomePolitica]);

  const grupos = useMemo(() => {
    if (!casos) return [];
    const q = busca.trim().toLowerCase();
    const vis = casos.filter((c) => (filtro === "todas" || c.categoria === filtro) &&
      (!q || `${c.id} ${c.titulo} ${c.objetivo} ${c.empresa}`.toLowerCase().includes(q)));
    return CATEGORIA_ORDEM.map((cat) => ({ cat, itens: vis.filter((c) => c.categoria === cat) })).filter((g) => g.itens.length);
  }, [casos, filtro, busca]);

  async function analisar(id: string) {
    setRodando(id);
    try {
      const r = await api.analisarDemo(id);
      navegar(`/analise/${r.id}`);
    } catch (e) {
      setErro((e as Error).message);
      setRodando(null);
    }
  }

  return (
    <div>
      <CabecalhoPagina
        titulo="Quem pode assinar a ATPV-e?"
        sub={<>{casos ? casos.length : "Os"} cenários jurídicos com gabarito, em documentos fictícios redigidos como peças reais
          (contratos registrados na JUCEC, estatutos, escrituras de procuração, substabelecimentos, atas, CRLV e ATPV-e). A empresa
          pode estar vendendo ou comprando — e ser Ltda, SLU, S.A., EI/MEI, EIRELI, sociedade simples, cooperativa ou associação.
          Abra o resultado já calculado ou peça à IA local para ler os documentos agora.</>}
      />
      {placar && <PlacarAvaliacao r={placar} />}
      <Painel className="mb-6 flex flex-wrap items-start gap-3 px-5 py-3.5">
        <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-accent-soft text-accent"><Bot className="size-4" /></span>
        <div className="min-w-[240px] flex-1 text-[13px] text-ink-2">
          <b className="text-ink">Antes da ATPV-e, só com o veículo e o CPF.</b> Na{" "}
          <Link href="/consulta" className="font-medium text-accent hover:underline">Consulta por CPF</Link>, o sistema acha o dono pela
          placa e confere se aquele CPF pode vender ou comprar — inclusive pessoa física representada por procurador (ele pergunta
          pela procuração e confere se ela dá poder àquele CPF).{" "}
          <b className="text-ink">Modo agente, na máquina local:</b> o comando <code className="rounded bg-surface-2 px-1 font-mono text-[12px]">outorga agente</code>{" "}
          vigia uma pasta e analisa sozinho cada pedido que chega, com parecer em PDF, resumo e registro na trilha de auditoria.
          Os casos fora da faixa de aceite automático continuam indo para revisão humana.
        </div>
      </Painel>
      {erro && <div className="mb-4"><ErroCaixa mensagem={erro} /></div>}

      <div className="mb-5 flex flex-wrap items-center gap-2">
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-2.5 size-4 text-muted" aria-hidden />
          <input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Buscar cenário, empresa…"
            className="h-9 w-64 rounded-md border border-line-strong bg-surface pl-8 pr-3 text-[13.5px] text-ink placeholder:text-muted" />
        </div>
        <div className="flex flex-wrap gap-1.5">
          {["todas", ...CATEGORIA_ORDEM].map((c) => (
            <button key={c} onClick={() => setFiltro(c)}
              className={cx("rounded-full border px-3 py-1 text-[12.5px] transition",
                filtro === c ? "border-accent bg-accent-soft text-accent" : "border-line bg-surface text-ink-2 hover:bg-surface-2")}>
              {c === "todas" ? "Todas" : CATEGORIA_CURTA[c] ?? CATEGORIA_TXT[c] ?? c}
            </button>
          ))}
        </div>
      </div>

      {!casos && !erro && <Carregando texto="Carregando cenários…" />}
      {grupos.map((g) => (
        <section key={g.cat} className="mb-8">
          <h2 className="mb-2.5 flex items-center gap-2 text-[14px] font-semibold text-ink">
            {g.cat === "bem_integralizado" && <Car className="size-4 text-accent" aria-hidden />}
            {CATEGORIA_TXT[g.cat] ?? g.cat}
            <span className="num text-[12px] font-normal text-muted">{g.itens.length}</span>
          </h2>
          <Painel className="divide-y divide-line overflow-hidden">
            {g.itens.map((c) => {
              const esp = esperadoDe(c, politica?.perfil);
              const audio = AUDIO.has(c.id);
              return (
                <div key={c.id} className={cx("flex flex-wrap items-center gap-x-5 gap-y-2 px-4 py-3.5", audio && "bg-accent-soft/50")}>
                  <div className={cx("w-1 self-stretch rounded-full", audio ? "bg-accent" : "bg-transparent")} aria-hidden />
                  <div className="min-w-[280px] flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded bg-surface-2 px-1.5 py-0.5 font-mono text-[11.5px] text-muted">{c.id}</span>
                      <span className="font-medium text-ink">{c.titulo}</span>
                      {audio && (
                        <span className="rounded-full bg-accent px-2 py-0.5 text-[11px] font-medium text-accent-ink">exemplo do áudio</span>
                      )}
                    </div>
                    <div className="mt-1 text-[13px] text-muted">{c.objetivo}</div>
                    <div className="mt-1 flex items-center gap-1.5 text-[12px] text-muted">
                      <FileText className="size-3.5" aria-hidden /> {c.empresa} ·{" "}
                      {c.esperado_lados
                        ? `${c.documentos.length + (c.documentos.includes("ATPV-e") ? 1 : 2)} documento(s) com o CRLV e a ATPV-e`
                        : `${c.documentos.length + 1} documento(s) com o CRLV`}
                    </div>
                  </div>
                  <div className="w-[210px]">
                    <div className="text-[11px] uppercase tracking-wide text-muted">Gabarito</div>
                    <div className="mt-0.5 flex flex-wrap items-center gap-1.5">
                      <ChipVeredito v={esp.veredito} />
                      {esp.faixas_aceitaveis.map((f) => <SeloFaixa key={f} faixa={f} />)}
                    </div>
                    {c.esperado_lados && (
                      <div className="mt-1 space-y-0.5">
                        {LADOS.filter((l) => c.esperado_lados?.[l]).map((l) => {
                          const e = c.esperado_lados![l]!;
                          return (
                            <div key={l} className="text-[11.5px] leading-snug">
                              <span className="text-muted">{LADO_TXT[l]}: </span>
                              <ChipVeredito v={e.veredito} />
                              {e.conjuntos_minimos_nomes?.length ? (
                                <div className="truncate text-muted" title={e.conjuntos_minimos_nomes.map((g) => g.join(" + ")).join(" ou ")}>
                                  quem pode: {e.conjuntos_minimos_nomes.map((g) => g.map((n) => n.split(" ")[0]).join(" + ")).join(" ou ")}
                                </div>
                              ) : null}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Botao tamanho="sm" icone={<Eye className="size-4" />} onClick={() => navegar(`/demo/${c.id}`)}
                      disabled={!c.precalculado} title={c.precalculado ? "Abrir o resultado já calculado" : "Ainda sem resultado calculado"}>
                      Ver resultado
                    </Botao>
                    <Botao tamanho="sm" variante="primario" icone={<Sparkles className="size-4" />} carregando={rodando === c.id}
                      disabled={!!rodando && rodando !== c.id} onClick={() => analisar(c.id)} title="Ler os documentos agora com a IA local">
                      Analisar com IA
                    </Botao>
                  </div>
                </div>
              );
            })}
          </Painel>
        </section>
      ))}
    </div>
  );
}
