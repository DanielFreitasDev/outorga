import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, FlaskConical, Loader2, RotateCcw, UserRound } from "lucide-react";
import { api } from "../../lib/api";
import type { Lado, Resultado, Simulacao, SimulacaoLado } from "../../lib/types";
import { FAIXA_TXT, LADO_TXT, VEREDITO_TXT, cpfFmt } from "../../lib/format";
import { Botao, ErroCaixa, Painel, SeloFaixa, cx } from "../../components/ui";
import { Medidor } from "../../components/Medidor";
import { useApp } from "../../lib/ctx";
import type { SimulacaoCtx } from "./comum";

export interface PessoaSim { chave: string; nome: string; cpf: string | null; papel: string }

/** Pessoas que podem entrar na simulação: todas as dos documentos + assinantes informados sem vínculo. */
export function pessoasSimulaveis(r: Resultado): PessoaSim[] {
  const papel = new Map<string, string>();
  r.grafo.nos.forEach((n) => { if (n.tipo === "pessoa") papel.set(n.id, (n.papeis ?? []).join(" · ")); });
  const out: PessoaSim[] = Object.entries(r.pessoas).map(([chave, p]) => ({ chave, nome: p.nome, cpf: p.cpf, papel: papel.get(chave) ?? "" }));
  r.assinantes.forEach((a) => {
    if (!out.some((p) => p.chave === a.chave)) out.push({ chave: a.chave, nome: a.nome, cpf: a.cpf, papel: "sem vínculo nos documentos" });
  });
  return out.sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
}

export function PainelSimulacao({ r, id, sim, aberto, setAberto, lado = "vendedor", doisLados = false }: {
  r: Resultado; id: string; sim: SimulacaoCtx; aberto: boolean; setAberto: (v: boolean) => void; lado?: Lado; doisLados?: boolean;
}) {
  const { politica } = useApp();
  const pessoas = useMemo(() => pessoasSimulaveis(r), [r]);
  const originais = useMemo(() => r.assinantes.map((a) => a.chave).sort().join("|"), [r]);
  const [valor, setValor] = useState<string>(r.pedido.valor !== null && r.pedido.valor !== undefined ? String(r.pedido.valor) : "");
  const [data, setData] = useState<string>(r.pedido.data_venda.slice(0, 10));
  const [resp, setResp] = useState<Simulacao | null>(null);
  const res: SimulacaoLado | null = resp ? (resp.lados?.[lado] ?? resp) : null;
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const seq = useRef(0);

  const chaves = [...sim.selecionados].sort().join("|");
  const alterado = chaves !== originais || data !== r.pedido.data_venda.slice(0, 10) ||
    valor !== (r.pedido.valor !== null && r.pedido.valor !== undefined ? String(r.pedido.valor) : "");

  useEffect(() => {
    if (!aberto) return;
    const meu = ++seq.current;
    const t = setTimeout(async () => {
      setCarregando(true);
      setErro(null);
      try {
        const assinantes = [...sim.selecionados].map((k) => {
          const p = pessoas.find((x) => x.chave === k);
          return { nome: p?.nome ?? k.replace(/^\?/, ""), cpf: p?.cpf ?? null };
        });
        const v = valor.trim() === "" ? null : Number(valor.replace(/\./g, "").replace(",", "."));
        const out = await api.simular(id, { lado, assinantes, valor: Number.isFinite(v as number) ? v : null, data_venda: data });
        if (meu === seq.current) setResp(out);
      } catch (e) {
        if (meu === seq.current) setErro((e as Error).message);
      } finally {
        if (meu === seq.current) setCarregando(false);
      }
    }, 220);
    return () => clearTimeout(t);
  }, [aberto, chaves, valor, data, id, pessoas, sim.selecionados, lado]);

  if (!aberto) {
    return (
      <button onClick={() => setAberto(true)}
        className="mt-4 flex w-full items-center gap-3 rounded-xl border border-dashed border-accent/50 bg-accent-soft/40 px-4 py-3 text-left transition hover:bg-accent-soft">
        <FlaskConical className="size-5 text-accent" />
        <div>
          <div className="text-[14px] font-medium text-ink">
            E se…? Simule outra combinação de assinantes{doisLados && <> pelo {LADO_TXT[lado].toLowerCase()}</>}
          </div>
          <div className="text-[12.5px] text-muted">Troque quem assina, o valor ou a data e veja o novo selo na hora — sem reler os documentos.</div>
        </div>
        <ArrowRight className="ml-auto size-4 text-accent" />
      </button>
    );
  }

  const mudouFaixa = res && res.faixa !== r.faixa;
  return (
    <Painel className="mt-4 overflow-hidden border-accent/40">
      <div className="flex flex-wrap items-center gap-2 border-b border-line bg-accent-soft/50 px-5 py-3">
        <FlaskConical className="size-4 text-accent" />
        <span className="font-semibold text-ink">E se…?</span>
        {doisLados && <span className="rounded-md bg-accent px-1.5 py-0.5 text-[11.5px] font-medium text-accent-ink">lado do {LADO_TXT[lado].toLowerCase()}</span>}
        <span className="text-[12.5px] text-muted">simulação instantânea sobre as leituras já feitas · não é gravada</span>
        <div className="ml-auto flex gap-2">
          <Botao tamanho="sm" variante="fantasma" icone={<RotateCcw className="size-3.5" />} disabled={!alterado}
            onClick={() => {
              sim.definir(r.assinantes.map((a) => a.chave));
              setValor(r.pedido.valor !== null && r.pedido.valor !== undefined ? String(r.pedido.valor) : "");
              setData(r.pedido.data_venda.slice(0, 10));
            }}>Restaurar</Botao>
          <Botao tamanho="sm" variante="fantasma" onClick={() => setAberto(false)}>Fechar</Botao>
        </div>
      </div>
      <div className="grid gap-5 p-5 lg:grid-cols-[1fr_340px]">
        <div>
          <div className="text-[12px] font-medium uppercase tracking-wide text-muted">
            Quem assina na simulação{doisLados && <> · pelo {LADO_TXT[lado].toLowerCase()}</>}
          </div>
          <p className="mt-0.5 text-[12.5px] text-muted">Clique para incluir ou tirar. Também dá para clicar nas pessoas em “Quem pode assinar” ou no grafo.</p>
          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {pessoas.map((p) => {
              const on = sim.selecionados.has(p.chave);
              return (
                <button key={p.chave} onClick={() => sim.alternar(p.chave)} aria-pressed={on}
                  title={`${p.nome}${p.cpf ? ` · ${cpfFmt(p.cpf)}` : ""}${p.papel ? ` · ${p.papel}` : ""}`}
                  className={cx("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[12.5px] transition",
                    on ? "border-accent bg-accent text-accent-ink" : "border-line-strong bg-surface text-ink-2 hover:border-accent/60")}>
                  <UserRound className="size-3.5" />
                  {p.nome}
                  {p.papel && <span className={cx("text-[11px]", on ? "opacity-80" : "text-muted")}>· {p.papel.split(" · ")[0]}</span>}
                </button>
              );
            })}
          </div>
          <div className="mt-4 flex flex-wrap gap-4">
            <label className="text-[12px] font-medium text-ink-2">
              Valor da venda (R$)
              <input value={valor} onChange={(e) => setValor(e.target.value)} inputMode="decimal" placeholder="não informado"
                className="mt-1 block h-9 w-44 rounded-md border border-line-strong bg-surface px-3 text-[13.5px] text-ink" />
            </label>
            <label className="text-[12px] font-medium text-ink-2">
              Data da venda
              <input type="date" value={data} onChange={(e) => setData(e.target.value)}
                className="mt-1 block h-9 rounded-md border border-line-strong bg-surface px-3 text-[13.5px] text-ink" />
            </label>
          </div>
        </div>
        <div className="rounded-lg border border-line bg-surface-2 p-4">
          <div className="flex items-center justify-between">
            <div className="text-[12px] font-medium uppercase tracking-wide text-muted">Resultado simulado</div>
            {carregando && <Loader2 className="size-4 animate-spin text-muted" />}
          </div>
          {erro && <div className="mt-2"><ErroCaixa mensagem={erro} /></div>}
          {res && (
            <div className={cx("mt-2 transition", carregando && "opacity-60")}>
              <div className="flex flex-wrap items-center gap-2">
                <SeloFaixa faixa={res.faixa} />
                <span className="text-[12.5px] text-ink-2">{VEREDITO_TXT[res.veredito]}</span>
              </div>
              <div className="mt-1 flex justify-center">
                <Medidor indice={res.indice} faixa={res.faixa} aceite={politica?.limiar_aceite ?? 85} recusa={politica?.limiar_recusa ?? 15} tamanho={170} />
              </div>
              {mudouFaixa && (
                <div className="mt-2 text-[12.5px] font-medium text-accent">
                  {FAIXA_TXT[r.faixa]} → {FAIXA_TXT[res.faixa]} em relação à análise original
                </div>
              )}
              <p className="mt-2 text-[13px] leading-relaxed text-ink">{res.resumo}</p>
              {res.faltantes.length > 0 && res.veredito !== "PODE" && (
                <div className="mt-2 text-[12.5px] text-ink-2">
                  Faltaria: {res.faltantes.slice(0, 2).map((f) => f.faltam_nomes.join(" + ") || "—").join(" ou ")}
                </div>
              )}
              {res.caminho_escolhido && (
                <div className="mt-2 text-[12px] text-muted">Caminho: {res.caminho_escolhido.descricao}</div>
              )}
              {doisLados && resp?.geral && (
                <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-line pt-2.5 text-[12.5px] text-ink-2">
                  <span>ATPV-e com os dois lados:</span>
                  <SeloFaixa faixa={resp.geral.faixa} />
                  <span className="text-muted">{VEREDITO_TXT[resp.geral.veredito]}</span>
                </div>
              )}
            </div>
          )}
          {!res && !erro && <div className="mt-3 text-[13px] text-muted">Calculando…</div>}
        </div>
      </div>
    </Painel>
  );
}
