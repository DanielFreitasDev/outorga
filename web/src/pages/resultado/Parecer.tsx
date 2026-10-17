import { useEffect, useState } from "react";
import { Download, ExternalLink } from "lucide-react";
import { api, baixarBlob } from "../../lib/api";
import type { Resultado } from "../../lib/types";
import { Botao, Carregando, ErroCaixa, Painel } from "../../components/ui";
import type { OrigemResultado } from "./Resultado";

export function AbaParecer({ r, origem }: { r: Resultado; origem: OrigemResultado }) {
  const [html, setHtml] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [baixando, setBaixando] = useState(false);

  useEffect(() => {
    if (origem.tipo === "precalculado") {
      api.parecerHtmlDeResultado(r).then(setHtml).catch((e) => setErro(e.message));
    }
  }, [r, origem]);

  async function baixar() {
    setBaixando(true);
    try {
      if (origem.tipo === "analise") {
        const resp = await fetch(`/api/analises/${origem.id}/parecer.pdf`);
        baixarBlob(await resp.blob(), `parecer-${origem.id}.pdf`);
      } else {
        baixarBlob(await api.parecerPdfDeResultado(r), `parecer-${origem.caso}.pdf`);
      }
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setBaixando(false);
    }
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <p className="text-[13.5px] text-muted">
          Parecer pronto para o processo: comprovação no formato do art. 28, § 7º, verificações com fundamento, cláusulas
          avaliadas e documentos com hash.
        </p>
        <div className="flex gap-2">
          {origem.tipo === "analise" && (
            <a href={`/api/analises/${origem.id}/parecer.html`} target="_blank" rel="noreferrer"
              className="inline-flex h-9 items-center gap-1.5 rounded-md border border-line-strong bg-surface px-3.5 text-[13.5px] font-medium text-ink hover:bg-surface-2">
              <ExternalLink className="size-4" /> Abrir em nova aba
            </a>
          )}
          <Botao variante="primario" icone={<Download className="size-4" />} carregando={baixando} onClick={baixar}>Baixar PDF</Botao>
        </div>
      </div>
      {erro && <ErroCaixa mensagem={erro} />}
      <Painel className="overflow-hidden bg-white p-0">
        {origem.tipo === "analise" ? (
          <iframe title="Parecer" src={`/api/analises/${origem.id}/parecer.html`} className="h-[78vh] w-full border-0 bg-white" />
        ) : html ? (
          <iframe title="Parecer" srcDoc={html} className="h-[78vh] w-full border-0 bg-white" />
        ) : !erro ? <div className="p-6"><Carregando texto="Gerando o parecer…" /></div> : null}
      </Painel>
    </div>
  );
}
