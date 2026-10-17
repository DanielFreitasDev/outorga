import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { FileText, ScanText } from "lucide-react";
import type { DocumentoRes, Fonte, Resultado } from "../../lib/types";
import { TIPO_DOC_TXT, dataBR } from "../../lib/format";
import { Painel, cx } from "../../components/ui";
import { coletarFontes } from "./comum";

const SEP = "\n\n";

interface Intervalo { ini: number; fim: number; fonte: Fonte }

function paginaComMarcas(texto: string, offset: number, ints: Intervalo[], alvo: Fonte | null) {
  const locais = ints
    .map((i) => ({ ini: Math.max(0, i.ini - offset), fim: Math.min(texto.length, i.fim - offset), fonte: i.fonte }))
    .filter((i) => i.fim > 0 && i.ini < texto.length && i.fim > i.ini)
    .sort((a, b) => a.ini - b.ini);
  const pedacos: React.ReactNode[] = [];
  let pos = 0;
  locais.forEach((i, k) => {
    const ini = Math.max(i.ini, pos);
    if (ini >= i.fim) return;
    if (ini > pos) pedacos.push(<Fragment key={`t${k}`}>{texto.slice(pos, ini)}</Fragment>);
    const ehAlvo = !!alvo && alvo.doc_id === i.fonte.doc_id && alvo.inicio !== null && alvo.inicio >= i.fonte.inicio! - 2 &&
      alvo.inicio <= i.fonte.fim!;
    pedacos.push(
      <mark key={`m${k}`} className={cx("fonte", ehAlvo && "alvo")} data-ini={i.fonte.inicio ?? undefined}
        title={i.fonte.clausula ?? "trecho citado na análise"}>
        {texto.slice(ini, i.fim)}
      </mark>,
    );
    pos = i.fim;
  });
  if (pos < texto.length) pedacos.push(<Fragment key="fim">{texto.slice(pos)}</Fragment>);
  return pedacos;
}

export function AbaDocumentos({ r, alvo }: { r: Resultado; alvo: Fonte | null }) {
  const [selecionado, setSel] = useState<string>(alvo?.doc_id ?? r.documentos[0]?.id ?? "");
  const fontes = useMemo(() => coletarFontes(r), [r]);
  const area = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (alvo?.doc_id) setSel(alvo.doc_id);
  }, [alvo]);

  const doc: DocumentoRes | undefined = r.documentos.find((d) => d.id === selecionado);
  const ints: Intervalo[] = fontes.filter((f) => f.doc_id === selecionado).map((f) => ({ ini: f.inicio!, fim: f.fim!, fonte: f }));

  useEffect(() => {
    if (!alvo || alvo.doc_id !== selecionado) return;
    const t = setTimeout(() => {
      const el = area.current?.querySelector("mark.alvo") as HTMLElement | null;
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
      else area.current?.scrollTo({ top: 0 });
    }, 60);
    return () => clearTimeout(t);
  }, [alvo, selecionado]);

  let offset = 0;
  return (
    <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
      <div className="space-y-1.5">
        {r.documentos.map((d) => {
          const n = fontes.filter((f) => f.doc_id === d.id).length;
          const ocr = d.metodo === "ocr" || d.metodo === "misto";
          return (
            <button key={d.id} onClick={() => setSel(d.id)}
              className={cx("w-full rounded-lg border px-3 py-2.5 text-left transition",
                d.id === selecionado ? "border-accent bg-accent-soft" : "border-line bg-surface hover:bg-surface-2")}>
              <div className="flex items-center gap-2">
                {ocr ? <ScanText className="size-4 text-warn" /> : <FileText className="size-4 text-muted" />}
                <span className="truncate text-[13.5px] font-medium text-ink">{d.titulo}</span>
              </div>
              <div className="mt-0.5 text-[12px] text-muted">
                {TIPO_DOC_TXT[d.tipo] ?? d.tipo} · {d.paginas.length} pág.{d.data ? ` · ${dataBR(d.data)}` : ""}
                {ocr && d.ocr_confianca !== null && ` · OCR ${Math.round(d.ocr_confianca)}%`}
              </div>
              {n > 0 && <div className="mt-1 text-[11.5px] text-accent">{n} trecho(s) citado(s)</div>}
            </button>
          );
        })}
      </div>
      <Painel className="min-w-0">
        {doc ? (
          <>
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-5 py-3">
              <div>
                <div className="font-medium text-ink">{doc.titulo}</div>
                <div className="text-[12px] text-muted">{doc.nome} · leitura {doc.metodo}{doc.ocr_confianca ? ` (OCR ${Math.round(doc.ocr_confianca)}%)` : ""}</div>
              </div>
              <div className="font-mono text-[11px] text-muted" title={doc.sha256}>SHA-256 {doc.sha256.slice(0, 20)}…</div>
            </div>
            <div ref={area} className="scroll-thin max-h-[70vh] overflow-y-auto px-5 py-4">
              {doc.paginas.map((p, i) => {
                const marcas = paginaComMarcas(p, offset, ints, alvo);
                offset += p.length + SEP.length;
                return (
                  <div key={i} className="mb-6">
                    <div className="mb-2 flex items-center gap-2 text-[11px] uppercase tracking-wide text-muted">
                      <span>Página {i + 1}</span><span className="h-px flex-1 bg-line" />
                    </div>
                    <div className="doc-texto text-ink-2">{marcas}</div>
                  </div>
                );
              })}
            </div>
          </>
        ) : <div className="p-5 text-muted">Nenhum documento.</div>}
      </Painel>
    </div>
  );
}
