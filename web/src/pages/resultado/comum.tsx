import { createContext, useContext } from "react";
import { Quote } from "lucide-react";
import type { Fonte, Resultado } from "../../lib/types";

export interface SimulacaoCtx {
  selecionados: Set<string>;
  alternar: (chave: string) => void;
  definir: (chaves: string[]) => void;
}

export interface NavResultado {
  abrirFonte: (f: Fonte) => void;
  simulacao?: SimulacaoCtx;
}

export const NavCtx = createContext<NavResultado>({ abrirFonte: () => undefined });
export const useNav = () => useContext(NavCtx);

export function Citacao({ fonte, max = 220, compacta = false }: { fonte: Fonte | null | undefined; max?: number; compacta?: boolean }) {
  const { abrirFonte } = useNav();
  if (!fonte || !fonte.trecho) return null;
  const t = fonte.trecho.replace(/\s+/g, " ").trim();
  const curto = t.length > max ? `${t.slice(0, max)}…` : t;
  const fraca = fonte.ancoragem !== null && fonte.ancoragem < 90;
  return (
    <button
      type="button"
      onClick={() => abrirFonte(fonte)}
      className="group mt-1.5 flex w-full items-start gap-2 rounded-md border border-line bg-surface-2 px-2.5 py-1.5 text-left transition hover:border-accent/50 hover:bg-accent-soft"
      title="Abrir o trecho no documento original"
    >
      <Quote className="mt-0.5 size-3.5 shrink-0 text-muted group-hover:text-accent" aria-hidden />
      <span className="min-w-0 text-[12.5px] leading-snug text-ink-2">
        {!compacta && <span className="italic">“{curto}”</span>}
        <span className="ml-1 whitespace-nowrap not-italic text-muted group-hover:text-accent">
          — {fonte.doc_titulo}{fonte.clausula ? `, ${fonte.clausula}` : ""}{fonte.pagina ? `, p. ${fonte.pagina}` : ""}
          {fraca && <span className="ml-1 text-warn">(citação {Math.round(fonte.ancoragem ?? 0)}% ancorada)</span>}
        </span>
      </span>
    </button>
  );
}

/** Todas as fontes citadas no resultado (sem repetição), para destacar nos documentos. */
export function coletarFontes(r: Resultado): Fonte[] {
  const out: Fonte[] = [];
  const add = (f: Fonte | null | undefined) => {
    if (f && f.doc_id && f.inicio !== null && f.fim !== null) out.push(f);
  };
  r.regras.forEach((g) => add(g.fonte));
  r.achados.forEach((a) => a.fontes.forEach(add));
  r.caminho_escolhido?.achados.forEach((a) => a.fontes.forEach(add));
  r.quem_pode.forEach((alt) => alt.achados.forEach((a) => a.fontes.forEach(add)));
  r.caminhos_invalidos.forEach((alt) => alt.achados.forEach((a) => a.fontes.forEach(add)));
  r.precondicoes.forEach((p) => p.fontes.forEach(add));
  r.comprovacao_poderes?.fontes.forEach(add);
  const vistos = new Set<string>();
  return out.filter((f) => {
    const k = `${f.doc_id}:${f.inicio}:${f.fim}`;
    if (vistos.has(k)) return false;
    vistos.add(k);
    return true;
  });
}
