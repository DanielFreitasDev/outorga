import { useEffect, useState } from "react";
import { Link2, ShieldAlert, ShieldCheck } from "lucide-react";
import { api } from "../lib/api";
import { Link } from "../lib/router";
import type { Auditoria as TAud } from "../lib/types";
import { dataHoraBR } from "../lib/format";
import { CabecalhoPagina, Carregando, ErroCaixa, HashCopiavel, Painel, Vazio } from "../components/ui";

const TIPO_TXT: Record<string, string> = {
  analise: "Análise concluída", revisao_humana: "Revisão humana", politica: "Mudança de política", reprocessamento: "Reprocessamento",
};

export function Auditoria() {
  const [d, setD] = useState<TAud | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  useEffect(() => { api.auditoria().then(setD).catch((e) => setErro(e.message)); }, []);
  return (
    <div>
      <CabecalhoPagina titulo="Trilha de auditoria"
        sub="Cada análise, revisão e mudança de política entra numa cadeia de hashes (SHA-256): alterar qualquer registro antigo quebra todos os seguintes." />
      {erro && <ErroCaixa mensagem={erro} />}
      {!d && !erro && <Carregando />}
      {d && (
        <>
          <Painel className={`mb-5 flex flex-wrap items-center gap-4 px-5 py-4 ${d.cadeia.integra ? "border-ok/40" : "border-bad/50"}`}>
            {d.cadeia.integra ? <ShieldCheck className="size-8 text-ok" /> : <ShieldAlert className="size-8 text-bad" />}
            <div>
              <div className={`text-[16px] font-semibold ${d.cadeia.integra ? "text-ok" : "text-bad"}`}>
                {d.cadeia.integra ? "Cadeia íntegra" : `Cadeia quebrada no registro ${d.cadeia.quebra_em}`}
              </div>
              <div className="text-[13px] text-muted">{d.cadeia.registros} registro(s) verificados</div>
            </div>
            <div className="ml-auto text-right">
              <div className="text-[11.5px] uppercase tracking-wide text-muted">Último hash</div>
              <HashCopiavel valor={d.cadeia.ultimo_hash} n={16} />
            </div>
          </Painel>
          {!d.registros.length ? (
            <Vazio titulo="Nenhum registro ainda" icone={<Link2 className="size-8" />}>Os registros aparecem quando análises são concluídas ou revisadas.</Vazio>
          ) : (
            <Painel className="overflow-x-auto">
              <table className="w-full min-w-[860px] text-left text-[13.5px]">
                <thead>
                  <tr className="border-b border-line text-[11.5px] uppercase tracking-wide text-muted">
                    <th className="px-4 py-2.5 font-medium">#</th>
                    <th className="px-4 py-2.5 font-medium">Quando</th>
                    <th className="px-4 py-2.5 font-medium">Evento</th>
                    <th className="px-4 py-2.5 font-medium">Resumo</th>
                    <th className="px-4 py-2.5 font-medium">Hash</th>
                    <th className="px-4 py-2.5 font-medium">Anterior</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {d.registros.map((r) => (
                    <tr key={r.seq} className="hover:bg-surface-2">
                      <td className="num px-4 py-2.5 text-muted">{r.seq}</td>
                      <td className="px-4 py-2.5 text-ink-2">{dataHoraBR(r.criado_em)}</td>
                      <td className="px-4 py-2.5">
                        <div className="text-ink">{TIPO_TXT[r.tipo] ?? r.tipo}</div>
                        {r.analise_id && <Link href={`/analise/${r.analise_id}`} className="font-mono text-[11.5px] text-accent hover:underline">{r.analise_id}</Link>}
                      </td>
                      <td className="max-w-[320px] px-4 py-2.5 text-ink-2">{r.resumo}</td>
                      <td className="px-4 py-2.5"><HashCopiavel valor={r.hash} /></td>
                      <td className="px-4 py-2.5"><HashCopiavel valor={r.hash_anterior} n={6} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Painel>
          )}
        </>
      )}
    </div>
  );
}
