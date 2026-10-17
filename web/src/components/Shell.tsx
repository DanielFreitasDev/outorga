import { useState, type ReactNode } from "react";
import {
  BookOpenText, Cpu, FileStack, History, Menu, Moon, ScrollText, ShieldCheck, SlidersHorizontal, Sun, Upload, UserRoundSearch, X,
} from "lucide-react";
import { Link } from "../lib/router";
import { useApp } from "../lib/ctx";
import { cx } from "./ui";

const NAV = [
  { href: "/", rotulo: "Demonstração", icone: FileStack, ativo: (r: string) => r === "/" || r.startsWith("/demo") },
  { href: "/consulta", rotulo: "Consulta por CPF", icone: UserRoundSearch, ativo: (r: string) => r === "/consulta" },
  { href: "/nova", rotulo: "Análise com ATPV-e", icone: Upload, ativo: (r: string) => r === "/nova" },
  { href: "/historico", rotulo: "Histórico", icone: History, ativo: (r: string) => r === "/historico" || r.startsWith("/analise") },
  { href: "/calibracao", rotulo: "Faixa intermediária", icone: SlidersHorizontal, ativo: (r: string) => r === "/calibracao" },
  { href: "/auditoria", rotulo: "Auditoria", icone: ScrollText, ativo: (r: string) => r === "/auditoria" },
  { href: "/como-funciona", rotulo: "Como funciona", icone: BookOpenText, ativo: (r: string) => r === "/como-funciona" },
];

function Marca() {
  return (
    <Link href="/" className="flex items-center gap-2.5 px-1">
      <span className="grid size-8 place-items-center rounded-lg bg-accent text-accent-ink shadow-card">
        <ShieldCheck className="size-[18px]" aria-hidden />
      </span>
      <span className="leading-tight">
        <span className="block text-[15px] font-semibold tracking-tight text-ink">Outorga</span>
        <span className="block text-[11px] text-muted">poderes para assinar a ATPV-e</span>
      </span>
    </Link>
  );
}

function StatusLLM() {
  const { saude, erroConexao } = useApp();
  const on = !!saude?.llm_disponivel && !erroConexao;
  const rotulo = saude?.rotulo_ia ?? (saude?.provedor === "llamacpp" ? `IA local · ${saude?.modelo}` : saude?.modelo ?? "IA");
  const txt = erroConexao ? "API indisponível" : !saude ? "verificando…"
    : saude.demonstracao && !on ? "Demonstração · sem IA" : on ? rotulo : `${rotulo} · desligada`;
  return (
    <div className="flex items-center gap-2 rounded-md border border-line bg-surface px-2.5 py-1 text-[12px]"
      title={saude ? `Provedor: ${saude.provedor} · modelo ${saude.modelo} · fila ${saude.fila}` : undefined}>
      <span className={cx("size-2 rounded-full", on ? "bg-ok" : erroConexao ? "bg-bad" : "bg-warn")} aria-hidden />
      <Cpu className="size-3.5 text-muted" aria-hidden />
      <span className="text-ink-2">{txt}</span>
      {!!saude?.fila && <span className="num rounded bg-surface-2 px-1 text-muted">fila {saude.fila}</span>}
    </div>
  );
}

function SeloPolitica() {
  const { politica } = useApp();
  if (!politica) return null;
  return (
    <Link href="/calibracao" className="hidden items-center gap-2 rounded-md border border-line bg-surface px-2.5 py-1 text-[12px] hover:bg-surface-2 md:flex"
      title="Política de aceitação em vigor — clique para ajustar">
      <span className="font-medium text-ink">{politica.nome}</span>
      <span className="text-muted">·</span>
      <span className="num text-ok">aceite ≥ {politica.limiar_aceite}</span>
      <span className="num text-bad">recusa ≤ {politica.limiar_recusa}</span>
    </Link>
  );
}

function FaixaDemonstracao() {
  const { saude } = useApp();
  if (!saude?.demonstracao) return null;
  return (
    <div className="border-b border-warn/40 bg-warn/10 px-4 py-2 text-center text-[12.5px] text-ink-2 md:px-6">
      <b className="text-ink">Demonstração pública</b> com dados fictícios. A consulta por CPF sem documentos, os cenários de
      exemplo, a simulação e o parecer funcionam; o envio de documentos fica desativado.{" "}
      <a className="text-accent underline-offset-2 hover:underline" href="https://github.com/DanielFreitasDev/outorga">
        Código e instalação local
      </a>
    </div>
  );
}

export function Shell({ rota, children }: { rota: string; children: ReactNode }) {
  const { tema, alternarTema } = useApp();
  const [aberto, setAberto] = useState(false);
  const nav = (
    <nav className="flex flex-col gap-0.5" aria-label="Navegação principal">
      {NAV.map((n) => {
        const I = n.icone;
        const ativo = n.ativo(rota);
        return (
          <Link key={n.href} href={n.href} onClick={() => setAberto(false)}
            className={cx("flex items-center gap-2.5 rounded-md px-2.5 py-2 text-[13.5px] transition",
              ativo ? "bg-accent-soft font-medium text-accent" : "text-ink-2 hover:bg-surface-2 hover:text-ink")}
            aria-current={ativo ? "page" : undefined}>
            <I className="size-4" aria-hidden />
            {n.rotulo}
          </Link>
        );
      })}
    </nav>
  );
  return (
    <div className="min-h-full">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[232px] flex-col border-r border-line bg-surface px-3 py-4 lg:flex">
        <Marca />
        <div className="mt-6">{nav}</div>
        <div className="mt-auto rounded-lg border border-line bg-surface-2 p-3 text-[11.5px] leading-snug text-muted">
          Leitura por IA generativa <b className="text-ink-2">conferida</b> por regras jurídicas. Casos duvidosos vão para
          revisão humana.
          <div className="mt-1.5">Res. CONTRAN nº 1.027/2026, art. 28, § 7º.</div>
        </div>
      </aside>
      {aberto && (
        <div className="fixed inset-0 z-40 bg-black/40 lg:hidden" onClick={() => setAberto(false)}>
          <aside className="h-full w-[260px] border-r border-line bg-surface px-3 py-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <Marca />
              <button className="rounded p-1 text-muted hover:bg-surface-2" onClick={() => setAberto(false)} aria-label="Fechar menu">
                <X className="size-5" />
              </button>
            </div>
            <div className="mt-6">{nav}</div>
          </aside>
        </div>
      )}
      <div className="lg:pl-[232px]">
        <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-line bg-bg/85 px-4 backdrop-blur md:px-6">
          <button className="rounded p-1.5 text-ink-2 hover:bg-surface-2 lg:hidden" onClick={() => setAberto(true)} aria-label="Abrir menu">
            <Menu className="size-5" />
          </button>
          <div className="lg:hidden"><Marca /></div>
          <div className="ml-auto flex items-center gap-2">
            <SeloPolitica />
            <StatusLLM />
            <button onClick={alternarTema} className="grid size-8 place-items-center rounded-md border border-line bg-surface text-ink-2 hover:bg-surface-2"
              aria-label={tema === "escuro" ? "Usar tema claro" : "Usar tema escuro"} title={tema === "escuro" ? "Tema claro" : "Tema escuro"}>
              {tema === "escuro" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </button>
          </div>
        </header>
        <FaixaDemonstracao />
        <main className="mx-auto max-w-[1240px] px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}
