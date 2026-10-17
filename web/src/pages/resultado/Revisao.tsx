import { useMemo, useState } from "react";
import { Check, ShieldCheck, ThumbsDown, ThumbsUp } from "lucide-react";
import { api } from "../../lib/api";
import { LADOS, type Lado, type Resultado } from "../../lib/types";
import { LADO_TXT, dataHoraBR } from "../../lib/format";
import { Botao, ErroCaixa, Painel, Secao, SevTag, cx } from "../../components/ui";
import type { OrigemResultado } from "./Resultado";

export function AbaRevisao({ r, origem }: { r: Resultado; origem: Extract<OrigemResultado, { tipo: "analise" }> }) {
  const pendencias = useMemo(() => {
    // com PJ dos dois lados, o checklist junta os dois (cada item diz de qual lado é)
    const partes: [Lado, Resultado][] = r.lados
      ? LADOS.filter((l) => r.lados?.[l]).map((l) => [l, r.lados![l]!])
      : [[r.lado ?? "vendedor", r]];
    const dois = partes.length > 1;
    const lista: { titulo: string; detalhe: string; sev: string }[] = [];
    partes.forEach(([lado, rr]) => {
      const pre = dois ? `${LADO_TXT[lado]} — ` : "";
      const itens = [...(rr.caminho_escolhido?.achados ?? []), ...rr.achados].filter((a) => a.severidade === "alerta" || a.severidade === "atencao");
      const vistos = new Set<string>();
      itens.filter((a) => {
        const k = a.codigo + a.detalhe;
        if (vistos.has(k)) return false;
        vistos.add(k);
        return true;
      }).forEach((a) => lista.push({ titulo: pre + a.titulo, detalhe: a.detalhe, sev: a.severidade }));
      (rr.caminho_escolhido?.precondicoes ?? []).filter((p) => p.satisfeita !== true)
        .forEach((p) => lista.push({ titulo: pre + p.descricao, detalhe: p.detalhe, sev: "alerta" }));
      if (rr.empresa.tipo === "PF") {
        lista.push({
          titulo: `${pre}Documento de identidade de quem vai assinar`,
          detalhe: "Conferir o CPF e a identidade do signatário (o próprio titular ou o procurador).", sev: "info",
        });
      } else {
        lista.push({
          titulo: `${pre}Certidão atualizada do registro${dois ? ` (${rr.empresa.razao_social})` : " (Junta Comercial ou cartório de pessoas jurídicas)"}`,
          detalhe: "Confirmar que não há alteração do ato constitutivo posterior aos documentos apresentados.", sev: "info",
        });
      }
      if (rr.caminho_escolhido && rr.caminho_escolhido.via !== "contrato") {
        lista.push({ titulo: `${pre}Certidão atualizada da procuração no cartório de origem`, detalhe: "A revogação fica anotada na serventia que lavrou o ato.", sev: "info" });
      }
    });
    return lista;
  }, [r]);
  const [marcados, setMarcados] = useState<Set<number>>(new Set());
  const [justificativa, setJust] = useState("");
  const [revisor, setRevisor] = useState(() => {
    try { return localStorage.getItem("outorga-revisor") ?? ""; } catch { return ""; }
  });
  const [enviando, setEnviando] = useState<"aprovar" | "recusar" | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);

  async function decidir(decisao: "aprovar" | "recusar") {
    if (!justificativa.trim()) {
      setErro("Escreva a justificativa da decisão — ela entra na trilha de auditoria.");
      return;
    }
    setErro(null);
    setEnviando(decisao);
    try {
      try { localStorage.setItem("outorga-revisor", revisor); } catch { /* sem armazenamento */ }
      const res = await api.revisar(origem.id, { decisao, justificativa, revisor: revisor || "servidor" });
      setOk(`Decisão registrada (auditoria ${res.hash.slice(0, 12)}…).`);
      setJust("");
      origem.recarregar();
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setEnviando(null);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div>
        <Secao titulo="Checklist do revisor" descricao={r.faixa === "AMARELO"
          ? "O caso caiu na faixa intermediária. Confira os pontos abaixo antes de decidir."
          : "Revisão opcional: o sistema já decidiu automaticamente, mas o servidor pode registrar uma decisão."}>
          <Painel>
            {pendencias.map((p, i) => (
              <label key={i} className="flex cursor-pointer items-start gap-3 border-t border-line px-4 py-3 first:border-t-0 hover:bg-surface-2">
                <input type="checkbox" className="mt-1 size-4 accent-[var(--accent)]" checked={marcados.has(i)}
                  onChange={() => setMarcados((m) => { const n = new Set(m); if (n.has(i)) n.delete(i); else n.add(i); return n; })} />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <SevTag sev={p.sev as "alerta"} />
                    <span className={cx("text-[13.5px] font-medium", marcados.has(i) ? "text-muted line-through" : "text-ink")}>{p.titulo}</span>
                  </div>
                  {p.detalhe && <div className="mt-1 text-[13px] text-ink-2">{p.detalhe}</div>}
                </div>
              </label>
            ))}
          </Painel>
          <div className="mt-2 text-[12px] text-muted">{marcados.size} de {pendencias.length} itens conferidos</div>
        </Secao>
        {origem.analise.revisoes.length > 0 && (
          <Secao titulo="Decisões registradas">
            <Painel className="divide-y divide-line">
              {origem.analise.revisoes.map((v) => (
                <div key={v.id} className="flex flex-wrap items-start gap-3 px-4 py-3 text-[13.5px]">
                  <span className={cx("rounded-md px-2 py-0.5 text-[12px] font-medium", v.decisao === "aprovar" ? "bg-ok-soft text-ok" : "bg-bad-soft text-bad")}>
                    {v.decisao === "aprovar" ? "aprovado" : "recusado"}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="text-ink">{v.justificativa}</div>
                    <div className="text-[12px] text-muted">{v.revisor} · {dataHoraBR(v.criado_em)}</div>
                  </div>
                </div>
              ))}
            </Painel>
          </Secao>
        )}
      </div>
      <div>
        <Painel className="sticky top-20 p-4">
          <div className="flex items-center gap-2 font-semibold text-ink"><ShieldCheck className="size-4 text-accent" /> Decisão do servidor</div>
          <p className="mt-1 text-[12.5px] text-muted">Entra na trilha de auditoria encadeada por hash e alimenta a calibração da faixa intermediária.</p>
          <label className="mt-4 block text-[12px] font-medium text-ink-2" htmlFor="revisor">Servidor responsável</label>
          <input id="revisor" value={revisor} onChange={(e) => setRevisor(e.target.value)} placeholder="Nome ou matrícula"
            className="mt-1 h-9 w-full rounded-md border border-line-strong bg-surface px-3 text-[13.5px] text-ink" />
          <label className="mt-3 block text-[12px] font-medium text-ink-2" htmlFor="just">Justificativa</label>
          <textarea id="just" value={justificativa} onChange={(e) => setJust(e.target.value)} rows={5}
            placeholder="Ex.: certidão simplificada conferida; procuração pública confirmada no cartório de origem."
            className="mt-1 w-full rounded-md border border-line-strong bg-surface px-3 py-2 text-[13.5px] text-ink" />
          {erro && <div className="mt-2"><ErroCaixa mensagem={erro} /></div>}
          {ok && <div className="mt-2 flex items-center gap-1.5 text-[13px] text-ok"><Check className="size-4" />{ok}</div>}
          <div className="mt-3 grid grid-cols-2 gap-2">
            <Botao variante="sucesso" icone={<ThumbsUp className="size-4" />} carregando={enviando === "aprovar"} disabled={!!enviando}
              onClick={() => decidir("aprovar")}>Aprovar</Botao>
            <Botao variante="perigo" icone={<ThumbsDown className="size-4" />} carregando={enviando === "recusar"} disabled={!!enviando}
              onClick={() => decidir("recusar")}>Recusar</Botao>
          </div>
        </Painel>
      </div>
    </div>
  );
}
