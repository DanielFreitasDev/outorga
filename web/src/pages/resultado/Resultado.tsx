import { useMemo, useState, type ReactNode } from "react";
import {
  ArrowLeftRight, Building2, CalendarClock, ClipboardCheck, FileSearch, FilePlus2, FileSignature, Gavel, ListChecks, Network,
  Paperclip, ScrollText, UserRound,
} from "lucide-react";
import { LADOS, type AnaliseCompleta, type Fonte, type Lado, type ParteATPV, type Pendencia, type Resultado } from "../../lib/types";
import {
  FAIXA_LONGO, LADO_LONGO, LADO_TXT, PENDENCIA_TXT, PF_FORA_ESCOPO, VEREDITO_TXT, cpfFmt, dataBR, docFmt, moeda, nomeInformado,
} from "../../lib/format";
import { navegar } from "../../lib/router";
import { useApp } from "../../lib/ctx";
import { Abas, Painel, Rotulo, SeloFaixa, cx } from "../../components/ui";
import { Medidor } from "../../components/Medidor";
import { NavCtx } from "./comum";
import { AbaDecisao } from "./Decisao";
import { AbaGrafo } from "./Grafo";
import { AbaLinhaTempo } from "./LinhaTempo";
import { AbaDocumentos } from "./Documentos";
import { AbaClausulas } from "./Clausulas";
import { AbaParecer } from "./Parecer";
import { AbaRevisao } from "./Revisao";
import { PainelSimulacao } from "./Simulacao";

export type OrigemResultado =
  | { tipo: "analise"; id: string; analise: AnaliseCompleta; recarregar: () => void }
  | { tipo: "precalculado"; caso: string; run: string };

type AbaId = "decisao" | "grafo" | "tempo" | "documentos" | "clausulas" | "parecer" | "revisao";

function Fato({ rotulo, children }: { rotulo: string; children: ReactNode }) {
  return (
    <div className="min-w-0">
      <Rotulo>{rotulo}</Rotulo>
      <div className="mt-0.5 text-[13.5px] text-ink">{children}</div>
    </div>
  );
}

const BARRA: Record<string, string> = { VERDE: "bg-ok", VERMELHO: "bg-bad", AMARELO: "bg-warn" };

/** Consulta por CPF (antes da ATPV-e): só o lado de quem vai assinar foi verificado. */
export function ehConsulta(r: Resultado): boolean {
  return r.pedido_atpv?.origem === "consulta por CPF" || !!r.pedido_atpv?.alvo;
}

/** Monta o link para refazer a consulta com o que faltou (mesmo veículo, CPF e papel; anexar o que a pendência pede). */
export function urlRefazerConsulta(r: Resultado, pendencias: Pendencia[]): string {
  const p = r.pedido_atpv;
  const q = new URLSearchParams();
  if (p?.veiculo.placa) q.set("placa", p.veiculo.placa);
  if (p?.veiculo.renavam) q.set("renavam", p.veiculo.renavam);
  const alvo = p?.alvo ?? r.lado ?? "vendedor";
  q.set("papel", alvo === "comprador" ? "comprar" : "vender");
  const ass = p?.[alvo]?.assinantes?.[0] ?? null;
  const cpf = ass?.cpf ?? r.assinantes[0]?.cpf ?? null;
  if (cpf) q.set("cpf", cpf);
  const nome = nomeInformado(ass?.nome ?? r.assinantes[0]?.informado);
  if (nome) q.set("nome", nome);
  if (alvo === "comprador" && p?.comprador) {
    if (p.comprador.documento) q.set("comprador", p.comprador.documento);
    if (p.comprador.nome) q.set("comprador_nome", p.comprador.nome);
  }
  if (p?.valor !== null && p?.valor !== undefined) q.set("valor", String(p.valor));
  if (p?.data_venda) q.set("data", p.data_venda);
  q.set("anexar", [...new Set(pendencias.map((x) => x.tipo))].join(","));
  const docs = [...new Set((r.lados ? LADOS.map((l) => r.lados?.[l]).filter(Boolean) as Resultado[] : [r])
    .flatMap((x) => x.documentos.map((d) => d.nome)))];
  if (docs.length) q.set("docs", docs.join("|"));
  return `/consulta?${q}`;
}

/** O que falta (procuração, contrato social, valor…): em destaque, com o atalho para refazer com o documento. */
function PainelPendencias({ r, podeRefazer }: { r: Resultado; podeRefazer: boolean }) {
  const pend = r.pendencias ?? [];
  if (!pend.length) return null;
  const consulta = ehConsulta(r);
  const variosLados = new Set(pend.map((p) => p.lado)).size > 1;
  return (
    <div className="mt-4 rounded-lg border border-warn/40 bg-warn-soft px-4 py-3" role="status">
      <div className="space-y-2">
        {pend.map((p, i) => (
          <div key={i} className="flex items-start gap-2.5">
            <Paperclip className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />
            <div className="min-w-0 text-[13.5px] text-ink">
              <span className="font-semibold">Falta: {PENDENCIA_TXT[p.tipo] ?? p.tipo}</span>
              {variosLados && p.lado && <span className="text-muted"> · {LADO_TXT[p.lado].toLowerCase()}</span>}
              <span className="text-ink-2"> — {p.mensagem}</span>
            </div>
          </div>
        ))}
      </div>
      {podeRefazer && (
        <div className="mt-3 flex flex-wrap items-center gap-2 pl-6">
          {consulta ? (
            <button type="button" onClick={() => navegar(urlRefazerConsulta(r, pend))}
              className="inline-flex h-8 items-center gap-1.5 rounded-md bg-accent px-3 text-[12.5px] font-medium text-accent-ink hover:brightness-110">
              <FilePlus2 className="size-3.5" /> Anexar e verificar de novo
            </button>
          ) : (
            <button type="button" onClick={() => navegar("/nova")}
              className="inline-flex h-8 items-center gap-1.5 rounded-md border border-line-strong bg-surface px-3 text-[12.5px] font-medium text-ink hover:bg-surface-2">
              <FilePlus2 className="size-3.5" /> Nova análise com o que falta
            </button>
          )}
          <span className="text-[12px] text-muted">mesmo veículo e mesmo CPF; anexe o que falta junto com os documentos já usados</span>
        </div>
      )}
    </div>
  );
}

/** Cartão de uma parte da ATPV-e: verificada (PJ ou pessoa física com procurador; clicável quando há dois lados) ou não. */
function CartaoParte({ lado, res, parte, ativo, clicavel, onClick, consulta }: {
  lado: Lado; res?: Resultado; parte?: ParteATPV; ativo: boolean; clicavel: boolean; onClick: () => void; consulta?: boolean;
}) {
  if (!res) {
    const pf = parte?.tipo === "PF";
    return (
      <div className="flex min-w-0 items-start gap-3 rounded-xl border border-dashed border-line-strong px-4 py-3">
        <UserRound className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />
        <div className="min-w-0">
          <Rotulo>{LADO_LONGO[lado]}</Rotulo>
          <div className="mt-0.5 truncate font-medium text-ink" title={parte?.nome ?? ""}>{parte?.nome || "não identificado"}</div>
          {parte?.documento && <div className="font-mono text-[12px] text-muted">{docFmt(parte.documento)}</div>}
          <div className="mt-1 text-[12.5px] text-muted">
            {consulta ? "não verificado nesta consulta"
              : !parte?.documento ? "não verificado (sem CPF/CNPJ no pedido)"
              : pf ? PF_FORA_ESCOPO : "sem verificação de poderes"}
          </div>
        </div>
      </div>
    );
  }
  const corpo = (
    <>
      <div className={cx("absolute inset-y-0 left-0 w-1", BARRA[res.faixa])} aria-hidden />
      <div className="flex items-start justify-between gap-2">
        <Rotulo>{LADO_LONGO[lado]}</Rotulo>
        <SeloFaixa faixa={res.faixa} />
      </div>
      <div className="mt-1 flex items-start gap-2">
        {res.empresa.tipo === "PF" ? <UserRound className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />
          : <Building2 className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />}
        <div className="min-w-0">
          <div className="line-clamp-2 font-medium text-ink" title={res.empresa.razao_social}>{res.empresa.razao_social}</div>
          <div className="font-mono text-[12px] text-muted">
            {res.empresa.tipo === "PF" ? <>pessoa física · CPF {res.empresa.cpf ? cpfFmt(res.empresa.cpf) : "—"}</>
              : <>{res.empresa.cnpj ? docFmt(res.empresa.cnpj) : "CNPJ não identificado"} · {res.empresa.tipo}</>}
          </div>
        </div>
      </div>
      <div className="mt-1.5 text-[12.5px] text-ink-2">
        {VEREDITO_TXT[res.veredito]} · índice <span className="num">{Math.round(res.indice)}</span>
        {clicavel && !ativo && <span className="ml-2 text-accent">ver este lado →</span>}
      </div>
    </>
  );
  const base = "relative min-w-0 overflow-hidden rounded-xl border bg-surface py-3 pl-5 pr-4 text-left";
  if (!clicavel) return <div className={cx(base, "border-line")}>{corpo}</div>;
  return (
    <button type="button" onClick={onClick} aria-pressed={ativo}
      className={cx(base, "transition", ativo ? "border-accent ring-2 ring-accent/25" : "border-line hover:border-accent/50 hover:bg-surface-2")}>
      {corpo}
    </button>
  );
}

/** Troca de lado compacta, junto às abas (para quem já rolou a página). */
function TrocaLado({ lado, lados, r, onTrocar }: { lado: Lado; lados: Lado[]; r: Resultado; onTrocar: (l: Lado) => void }) {
  return (
    <div className="mb-3 flex flex-wrap items-center gap-2 text-[12.5px] text-muted">
      <ArrowLeftRight className="size-4" aria-hidden />
      <span>Mostrando o lado:</span>
      <div className="inline-flex rounded-lg border border-line bg-surface p-0.5" role="group" aria-label="Lado da ATPV-e">
        {lados.map((l) => (
          <button key={l} type="button" onClick={() => onTrocar(l)} aria-pressed={l === lado}
            className={cx("inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 font-medium transition",
              l === lado ? "bg-accent text-accent-ink" : "text-ink-2 hover:bg-surface-2")}>
            {LADO_TXT[l]}
            <span className={cx("size-2 rounded-full", BARRA[r.lados?.[l]?.faixa ?? "AMARELO"])} aria-hidden />
          </button>
        ))}
      </div>
      <span>· parecer e revisão valem para a ATPV-e inteira</span>
    </div>
  );
}

export function VisaoResultado({ r, origem, extraTopo }: { r: Resultado; origem: OrigemResultado; extraTopo?: ReactNode }) {
  const { politica } = useApp();
  const ladosDisp = useMemo(() => LADOS.filter((l) => !!r.lados?.[l]), [r]);
  const doisLados = ladosDisp.length > 1;
  const temPartes = !!r.pedido_atpv || ladosDisp.length > 0;
  const [lado, setLado] = useState<Lado>(() => ladosDisp[0] ?? r.lado ?? "vendedor");
  const rl: Resultado = r.lados?.[lado] ?? r;
  const ladoAtual: Lado = rl.lado ?? r.lado ?? lado;
  const [aba, setAba] = useState<AbaId>("decisao");
  const [alvo, setAlvo] = useState<Fonte | null>(null);
  const [selPorLado, setSelPorLado] = useState<Record<string, Set<string>>>(() => {
    const out: Record<string, Set<string>> = {};
    (ladosDisp.length ? ladosDisp : [r.lado ?? "vendedor"]).forEach((l) => {
      out[l] = new Set((r.lados?.[l] ?? r).assinantes.map((a) => a.chave));
    });
    return out;
  });
  const [simAberto, setSimAberto] = useState(false);
  const aceite = politica?.limiar_aceite ?? 85;
  const recusa = politica?.limiar_recusa ?? 15;
  // na consulta por CPF, o /simular reaproveita o pedido já resolvido (dono da base veicular, lado consultado)
  const podeSimular = origem.tipo === "analise";
  const selecionados = useMemo(() => selPorLado[lado] ?? new Set<string>(), [selPorLado, lado]);

  const trocarLado = (l: Lado) => {
    setLado(l);
    setAlvo(null);
  };

  const simulacao = useMemo(() => podeSimular ? {
    selecionados,
    alternar: (chave: string) => {
      setSimAberto(true);
      setSelPorLado((m) => {
        const n = new Set(m[lado] ?? []);
        if (n.has(chave)) n.delete(chave);
        else n.add(chave);
        return { ...m, [lado]: n };
      });
    },
    definir: (chaves: string[]) => {
      setSimAberto(true);
      setSelPorLado((m) => ({ ...m, [lado]: new Set(chaves) }));
    },
  } : undefined, [podeSimular, selecionados, lado]);

  const nav = useMemo(() => ({
    abrirFonte: (f: Fonte) => {
      setAlvo({ ...f });
      setAba("documentos");
      setTimeout(() => document.getElementById("abas-resultado")?.scrollIntoView({ behavior: "smooth", block: "start" }), 30);
    },
    simulacao,
  }), [simulacao]);

  const alertas = [...rl.achados, ...(rl.caminho_escolhido?.achados ?? [])].filter((a) => a.severidade === "alerta").length;
  const correcoes = rl.regras.reduce((n, g) => n + g.verificacoes.filter((v) => v.divergiu).length, 0);
  const abas: { id: AbaId; rotulo: string; icone: ReactNode; contador?: number; destaque?: boolean }[] = [
    { id: "decisao", rotulo: "Decisão", icone: <Gavel className="size-4" />, contador: alertas, destaque: alertas > 0 },
    { id: "grafo", rotulo: "Grafo de poderes", icone: <Network className="size-4" /> },
    { id: "tempo", rotulo: "Linha do tempo", icone: <CalendarClock className="size-4" /> },
    { id: "documentos", rotulo: "Documentos", icone: <FileSearch className="size-4" />, contador: rl.documentos.length },
    { id: "clausulas", rotulo: "Cláusulas", icone: <ListChecks className="size-4" />, contador: correcoes, destaque: correcoes > 0 },
    { id: "parecer", rotulo: "Parecer", icone: <ScrollText className="size-4" /> },
  ];
  if (origem.tipo === "analise") abas.push({ id: "revisao", rotulo: "Revisão humana", icone: <ClipboardCheck className="size-4" />,
    contador: origem.analise.revisoes.length });

  const meta = r.meta as Record<string, string | undefined>;
  const consulta = ehConsulta(r);
  const ladosCartao: Lado[] = consulta ? [r.pedido_atpv?.alvo ?? ladoAtual] : LADOS;
  const rotuloAssinantes = consulta ? "Quem vai assinar" : doisLados ? `Assinante(s) · ${LADO_TXT[ladoAtual].toLowerCase()}` : "Assinante(s) informado(s)";
  return (
    <NavCtx.Provider value={nav}>
      {extraTopo}
      <Painel className="overflow-hidden">
        <div className={cx("h-1", BARRA[r.faixa])} />
        <div className="grid gap-6 p-5 md:grid-cols-[1fr_auto] md:p-6">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <SeloFaixa faixa={r.faixa} grande />
              <div className="text-[13px] text-muted">
                <div className="font-medium text-ink-2">{FAIXA_LONGO[r.faixa]}</div>
                {doisLados ? (
                  <div>Resultado da ATPV-e: {VEREDITO_TXT[r.veredito]} · com PJ dos dois lados, o lado mais fraco decide</div>
                ) : (
                  <div>Veredito: {VEREDITO_TXT[r.veredito]} · confiança {Math.round(r.confianca * 100)}%</div>
                )}
              </div>
            </div>
            {doisLados ? (
              <div className="mt-4 space-y-1.5 text-[15px] leading-relaxed text-ink">
                {ladosDisp.map((l) => (
                  <p key={l}><b className="font-semibold">{LADO_TXT[l]}:</b> {r.lados?.[l]?.resumo}</p>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-[15.5px] leading-relaxed text-ink">{r.resumo}</p>
            )}
            <PainelPendencias r={r} podeRefazer={origem.tipo === "analise"} />
            {temPartes && (
              <div className={cx("mt-5 grid gap-3", ladosCartao.length > 1 && "sm:grid-cols-2")}>
                {ladosCartao.map((l) => (
                  <CartaoParte key={l} lado={l} res={r.lados?.[l] ?? (ladosDisp.length === 0 && (r.lado ?? "vendedor") === l ? r : undefined)}
                    parte={r.pedido_atpv?.[l]} ativo={l === lado} clicavel={doisLados} onClick={() => trocarLado(l)} consulta={consulta} />
                ))}
              </div>
            )}
            <div className={cx("mt-5 grid grid-cols-2 gap-x-6 gap-y-4", temPartes ? "md:grid-cols-3" : "md:grid-cols-4")}>
              {!temPartes && (
                <Fato rotulo="Vendedor (PJ)">
                  <div className="line-clamp-2 font-medium" title={r.empresa.razao_social}>{r.empresa.razao_social}</div>
                  <div className="font-mono text-[12px] text-muted">{r.empresa.cnpj ?? "CNPJ não identificado"} · {r.empresa.tipo}</div>
                </Fato>
              )}
              <Fato rotulo="Veículo">
                <div className="font-mono font-medium">{rl.pedido.veiculo.placa ?? "—"}</div>
                <div className="truncate text-[12px] text-muted" title={rl.pedido.veiculo.descricao ?? ""}>{rl.pedido.veiculo.descricao}</div>
              </Fato>
              <Fato rotulo={consulta ? "Data de referência" : "Venda"}>
                <div>{dataBR(rl.pedido.data_venda)}</div>
                <div className="text-[12px] text-muted">{consulta && (rl.pedido.valor === null || rl.pedido.valor === undefined) ? "valor não informado" : moeda(rl.pedido.valor)}</div>
              </Fato>
              <Fato rotulo={rotuloAssinantes}>
                {rl.assinantes.length ? rl.assinantes.map((a) => (
                  <div key={a.chave} className="mb-1 last:mb-0" title={`${a.informado} → ${a.nome} (${a.criterio})`}>
                    <div className="truncate">{nomeInformado(a.nome) || <span className="text-muted">nome não informado</span>}</div>
                    <div className="font-mono text-[12px] text-muted">{a.cpf ? cpfFmt(a.cpf) : "sem CPF"} · {a.criterio}</div>
                  </div>
                )) : <div className="text-[12.5px] text-muted">nenhum informado — consulta de quem pode assinar</div>}
              </Fato>
            </div>
          </div>
          <div className="flex flex-col items-center justify-center gap-1 md:border-l md:border-line md:pl-6">
            <Medidor indice={r.indice} aceite={aceite} recusa={recusa} faixa={r.faixa} />
            <div className="max-w-[230px] text-center text-[11.5px] leading-snug text-muted">
              {r.motivos_faixa.slice(0, doisLados ? 4 : 3).map((m, i) => <div key={i}>{m}</div>)}
            </div>
          </div>
        </div>
        <div className="flex flex-wrap gap-x-5 gap-y-1 border-t border-line bg-surface-2 px-5 py-2 text-[12px] text-muted md:px-6">
          <span>Política: <b className="font-medium text-ink-2">{meta.politica ?? politica?.nome ?? "—"}</b></span>
          <span>Leitura: <b className="font-medium text-ink-2">{meta.provedor ? `${meta.provedor} · ${meta.modelo}`
            : origem.tipo === "precalculado" && !origem.run.startsWith("oraculo") ? `IA local · avaliação ${origem.run}` : "gabarito (oráculo)"}</b></span>
          <span>
            {doisLados && <>{LADO_TXT[ladoAtual]}: </>}
            Confiança da leitura {Math.round((rl.componentes.leitura ?? 0) * 100)}% · robustez jurídica {Math.round((rl.componentes.juridica ?? 0) * 100)}%
          </span>
          {r.pedido_atpv?.origem === "ATPV-e" && <span>Dados do pedido lidos da <b className="font-medium text-ink-2">ATPV-e</b></span>}
          {consulta && <span>Consulta por CPF, antes da ATPV-e{r.pedido_atpv?.titular_fonte
            ? <> · proprietário conferido {r.pedido_atpv.titular_fonte === "base veicular" ? "na " : "no "}<b className="font-medium text-ink-2">{r.pedido_atpv.titular_fonte}</b></> : null}</span>}
          {r.auditoria?.hash && <span className="font-mono">auditoria {r.auditoria.hash.slice(0, 12)}…</span>}
          <span className="ml-auto inline-flex items-center gap-1"><FileSignature className="size-3.5" /> {rl.comprovacao_poderes?.norma ?? "Res. CONTRAN 1.027/2026, art. 28, § 7º"}</span>
        </div>
        {(r.avisos?.length ?? 0) > 0 && (
          <div className="border-t border-line bg-warn-soft/60 px-5 py-2 text-[12.5px] text-warn md:px-6">
            {r.avisos.map((a, i) => <div key={i}>{a}</div>)}
          </div>
        )}
      </Painel>

      {simulacao && origem.tipo === "analise" && (
        <PainelSimulacao key={lado} r={rl} id={origem.id} sim={simulacao} aberto={simAberto} setAberto={setSimAberto}
          lado={ladoAtual} doisLados={doisLados} />
      )}

      <div id="abas-resultado" className="mt-6 scroll-mt-16">
        {doisLados && <TrocaLado lado={lado} lados={ladosDisp} r={r} onTrocar={trocarLado} />}
        <Abas abas={abas} atual={aba} onTrocar={setAba} />
        <div className="pt-5" key={lado}>
          {aba === "decisao" && <AbaDecisao r={rl} />}
          {aba === "grafo" && <AbaGrafo r={rl} />}
          {aba === "tempo" && <AbaLinhaTempo r={rl} />}
          {aba === "documentos" && <AbaDocumentos r={rl} alvo={alvo} />}
          {aba === "clausulas" && <AbaClausulas r={rl} />}
          {aba === "parecer" && <AbaParecer r={r} origem={origem} />}
          {aba === "revisao" && origem.tipo === "analise" && <AbaRevisao r={r} origem={origem} />}
        </div>
      </div>
    </NavCtx.Provider>
  );
}
