import { useEffect, useState } from "react";
import { Inbox, Loader2 } from "lucide-react";
import { api } from "../lib/api";
import { Link } from "../lib/router";
import type { AnaliseResumo } from "../lib/types";
import { VEREDITO_TXT, dataHoraBR } from "../lib/format";
import { CabecalhoPagina, Carregando, ErroCaixa, Painel, SeloFaixa, Vazio } from "../components/ui";
import { BarraIndice } from "../components/Medidor";

export function Historico() {
  const [lista, setLista] = useState<AnaliseResumo[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  useEffect(() => {
    const f = () => api.analises().then(setLista).catch((e) => setErro(e.message));
    f();
    const t = setInterval(f, 5000);
    return () => clearInterval(t);
  }, []);
  return (
    <div>
      <CabecalhoPagina titulo="Histórico" sub="Todas as análises feitas nesta máquina, com a faixa, o índice e a decisão do revisor quando houver." />
      {erro && <ErroCaixa mensagem={erro} />}
      {!lista && !erro && <Carregando />}
      {lista && !lista.length && (
        <Vazio titulo="Nenhuma análise ainda" icone={<Inbox className="size-8" />}>
          Rode um cenário da demonstração com a IA local, faça uma “Consulta por CPF” ou envie a ATPV-e e os documentos em “Análise com ATPV-e”.
        </Vazio>
      )}
      {lista && lista.length > 0 && (
        <Painel className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-[13.5px]">
            <thead>
              <tr className="border-b border-line text-[11.5px] uppercase tracking-wide text-muted">
                <th className="px-4 py-2.5 font-medium">Quando</th>
                <th className="px-4 py-2.5 font-medium">Empresa · placa</th>
                <th className="px-4 py-2.5 font-medium">Faixa</th>
                <th className="px-4 py-2.5 font-medium">Índice</th>
                <th className="px-4 py-2.5 font-medium">Veredito</th>
                <th className="px-4 py-2.5 font-medium">Revisão</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {lista.map((a) => (
                <tr key={a.id} className="hover:bg-surface-2">
                  <td className="px-4 py-2.5">
                    <Link href={`/analise/${a.id}`} className="font-mono text-[12.5px] text-accent hover:underline">{dataHoraBR(a.criado_em)}</Link>
                    <div className="text-[11.5px] text-muted">{a.caso_demo ? `cenário ${a.caso_demo}` : a.origem}{a.duracao_s ? ` · ${a.duracao_s.toFixed(0)} s` : ""}</div>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="max-w-[300px] truncate text-ink">{a.empresa ?? "—"}</div>
                    <div className="font-mono text-[12px] text-muted">{a.placa ?? "—"}</div>
                  </td>
                  <td className="px-4 py-2.5">
                    {a.status === "processando" ? <span className="inline-flex items-center gap-1.5 text-accent"><Loader2 className="size-3.5 animate-spin" />lendo…</span>
                      : a.status === "erro" ? <span className="text-bad">erro</span> : a.faixa ? <SeloFaixa faixa={a.faixa} /> : "—"}
                  </td>
                  <td className="px-4 py-2.5"><BarraIndice indice={a.indice} faixa={a.faixa} /></td>
                  <td className="px-4 py-2.5 text-ink-2">{a.veredito ? VEREDITO_TXT[a.veredito] : "—"}</td>
                  <td className="px-4 py-2.5">
                    {a.revisao ? <span className={a.revisao === "aprovar" ? "text-ok" : "text-bad"}>{a.revisao === "aprovar" ? "aprovada" : "recusada"}</span>
                      : <span className="text-muted">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Painel>
      )}
    </div>
  );
}
