import { CheckCircle2, CircleSlash, FileCheck2, Landmark, UserRound, Users } from "lucide-react";
import type { Achado, Alternativa, Resultado } from "../../lib/types";
import { SEV_ORDEM, VIA_TXT, cpfFmt, nomeInformado } from "../../lib/format";
import { Painel, Secao, SevTag, cx } from "../../components/ui";
import { Citacao, useNav } from "./comum";

function StatusComprovacao({ s }: { s: string }) {
  const cls = s === "comprovada" ? "bg-ok-soft text-ok border-ok/30" : s === "pendente" ? "bg-warn-soft text-warn border-warn/30"
    : "bg-bad-soft text-bad border-bad/30";
  return <span className={cx("rounded-md border px-2 py-0.5 text-[12px] font-medium", cls)}>{s}</span>;
}

function LinhaQuadro({ rotulo, children }: { rotulo: string; children: React.ReactNode }) {
  return (
    <div className="grid gap-1 border-t border-line px-5 py-3 first:border-t-0 md:grid-cols-[210px_1fr] md:gap-4">
      <div className="text-[12px] font-medium uppercase tracking-wide text-muted">{rotulo}</div>
      <div className="text-[13.5px] text-ink">{children}</div>
    </div>
  );
}

function QuadroSetimo({ r }: { r: Resultado }) {
  const c = r.comprovacao_poderes;
  if (!c) return null;
  const lista = (itens: string[]) => (
    <ul className="space-y-1">{itens.map((t, i) => <li key={i} className="leading-snug">{t}</li>)}</ul>
  );
  return (
    <Secao titulo={<span className="inline-flex items-center gap-2"><FileCheck2 className="size-4 text-accent" />Comprovação de poderes do signatário</span>}
      descricao={<>Elementos exigidos pela {c.norma}: outorgante, outorgado, poderes, prazo e revogação.</>}
      acoes={<StatusComprovacao s={c.status} />}>
      <Painel>
        {c.outorgante.tipo === "PF" ? (
          <LinhaQuadro rotulo="Titular">
            <div className="font-medium">{c.outorgante.nome}</div>
            <div className="font-mono text-[12px] text-muted">CPF {c.outorgante.cpf ? cpfFmt(c.outorgante.cpf) : "—"} · pessoa física</div>
            <div className="mt-1 text-[12.5px] text-muted">Titularidade conferida em: {c.outorgante.titularidade ?? "—"}</div>
          </LinhaQuadro>
        ) : (
          <LinhaQuadro rotulo="Outorgante">
            <div className="font-medium">{c.outorgante.nome}</div>
            <div className="font-mono text-[12px] text-muted">CNPJ {c.outorgante.cnpj ?? "—"} · {c.outorgante.tipo}</div>
            <div className="mt-1 text-[12.5px] text-muted">
              Atos vigentes na data da venda: {c.outorgante.atos_vigentes.map((a) => a.titulo).join("; ") || "—"}
            </div>
          </LinhaQuadro>
        )}
        <LinhaQuadro rotulo="Outorgado(s) / signatário(s)">
          <ul className="space-y-1">
            {c.outorgado.map((o, i) => (
              <li key={i}>
                <span className="font-medium">{nomeInformado(o.nome) || "nome não informado"}</span>
                {o.cpf && <span className="ml-1.5 font-mono text-[12px] text-muted">{cpfFmt(o.cpf)}</span>}
                <span className="ml-1.5 text-ink-2">· {o.qualidade}</span>
                <span className="ml-1.5 text-[12px] text-muted">(identificado por {o.identificacao})</span>
              </li>
            ))}
          </ul>
        </LinhaQuadro>
        <LinhaQuadro rotulo="Poderes conferidos">{lista(c.poderes_conferidos)}</LinhaQuadro>
        <LinhaQuadro rotulo="Prazo de validade">{lista(c.prazo_validade)}</LinhaQuadro>
        <LinhaQuadro rotulo="Revogação">{lista(c.revogacao)}</LinhaQuadro>
        <LinhaQuadro rotulo="Documentos verificáveis">
          <ul className="space-y-0.5">
            {r.documentos.map((d) => (
              <li key={d.id} className="flex flex-wrap items-baseline gap-x-2">
                <span>{d.titulo}</span>
                <span className="font-mono text-[11.5px] text-muted" title={d.sha256}>SHA-256 {d.sha256.slice(0, 16)}…</span>
              </li>
            ))}
          </ul>
        </LinhaQuadro>
      </Painel>
    </Secao>
  );
}

function CartaoAlternativa({ a, assinantes, escolhida }: { a: Alternativa; assinantes: Set<string>; escolhida: boolean }) {
  const Icone = a.via === "contrato" ? Landmark : UserRound;
  const { simulacao } = useNav();
  return (
    <div className={cx("rounded-xl border bg-surface p-4", escolhida ? "border-ok/60 ring-1 ring-ok/30" : "border-line")}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap gap-1.5">
          {a.pessoas.map((p) => {
            const cls = cx("inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[13px]",
              assinantes.has(p.chave) ? "border-accent bg-accent-soft font-medium text-accent" : "border-line bg-surface-2 text-ink",
              simulacao && "transition hover:border-accent hover:ring-2 hover:ring-accent/25",
              simulacao?.selecionados.has(p.chave) && !assinantes.has(p.chave) && "border-dashed border-accent");
            return simulacao ? (
              <button key={p.chave} className={cls} onClick={() => simulacao.alternar(p.chave)}
                title="Incluir/tirar esta pessoa na simulação “E se…?”">
                <UserRound className="size-3.5" aria-hidden />
                {p.nome}
              </button>
            ) : (
              <span key={p.chave} className={cls}>
                <UserRound className="size-3.5" aria-hidden />
                {p.nome}
              </span>
            );
          })}
        </div>
        {a.severidade !== "ok" && <SevTag sev={a.severidade} />}
      </div>
      <div className="mt-2.5 flex items-start gap-2 text-[12.5px] text-muted">
        <Icone className="mt-0.5 size-3.5 shrink-0" aria-hidden />
        <span><b className="font-medium text-ink-2">{VIA_TXT[a.via]}</b> · {a.descricao}</span>
      </div>
      {a.pessoas.length > 1 && <div className="mt-1 text-[12px] text-muted">assinatura conjunta das {a.pessoas.length} pessoas</div>}
      <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2">
        {escolhida ? (
          <span className="inline-flex items-center gap-1.5 text-[12.5px] font-medium text-ok">
            <CheckCircle2 className="size-4" /> atendida pelos assinantes informados
          </span>
        ) : <span />}
        {simulacao && (
          <button className="text-[12px] font-medium text-accent hover:underline" onClick={() => simulacao.definir(a.pessoas.map((p) => p.chave))}>
            E se assinarem estes? →
          </button>
        )}
      </div>
    </div>
  );
}

function ItemAchado({ a }: { a: Achado }) {
  const fonte = a.fontes.find((f) => f && f.trecho);
  return (
    <div className="flex items-start gap-3 border-t border-line px-4 py-3 first:border-t-0">
      <div className="w-[84px] shrink-0 pt-0.5"><SevTag sev={a.severidade} /></div>
      <div className="min-w-0 flex-1">
        <div className="text-[13.5px] font-medium text-ink">{a.titulo}</div>
        <div className="mt-0.5 text-[13px] leading-relaxed text-ink-2">{a.detalhe}</div>
        {a.fundamento.length > 0 && (
          <div className="mt-1.5 flex flex-wrap gap-1">
            {a.fundamento.map((f) => (
              <span key={f} className="rounded border border-line bg-surface-2 px-1.5 py-0.5 text-[11.5px] text-muted">{f}</span>
            ))}
          </div>
        )}
        <Citacao fonte={fonte} />
      </div>
    </div>
  );
}

export function AbaDecisao({ r }: { r: Resultado }) {
  const compra = (r.lado ?? r.pedido.lado) === "comprador";
  const assinantes = new Set(r.assinantes.map((a) => a.chave));
  const brutos = [...(r.caminho_escolhido?.achados ?? []), ...r.achados];
  const vistos = new Set<string>();
  const achados = brutos.filter((a) => {
    const k = `${a.codigo}|${a.detalhe}`;
    if (vistos.has(k)) return false;
    vistos.add(k);
    return true;
  }).sort((a, b) => SEV_ORDEM[a.severidade] - SEV_ORDEM[b.severidade]);
  const pend = r.precondicoes.length ? (r.caminho_escolhido?.precondicoes ?? r.precondicoes) : [];

  return (
    <div>
      <QuadroSetimo r={r} />

      <Secao titulo={<span className="inline-flex items-center gap-2"><Users className="size-4 text-accent" />
        Quem pode assinar a ATPV-e pela {compra ? "compradora" : "vendedora"}</span>}
        descricao={`Combinações mínimas de assinatura que obrigam a empresa ${compra ? "na compra" : "na venda"}, na data da operação (ato constitutivo e delegações válidas).`}>
        {r.quem_pode.length ? (
          <div className="grid gap-3 md:grid-cols-2">
            {r.quem_pode.map((a) => (
              <CartaoAlternativa key={a.id} a={a} assinantes={assinantes} escolhida={r.caminho_escolhido?.id === a.id} />
            ))}
          </div>
        ) : (
          <Painel className="flex items-center gap-3 px-4 py-4 text-[13.5px] text-ink-2">
            <CircleSlash className="size-5 text-bad" /> Ninguém tem poder de representação em vigor com os documentos apresentados.
          </Painel>
        )}
        {r.faltantes.length > 0 && r.veredito !== "PODE" && (
          <div className="mt-3 rounded-lg border border-line bg-surface-2 px-4 py-3 text-[13px] text-ink-2">
            <b className="text-ink">Para valer, faltaria:</b>
            <ul className="mt-1 list-disc space-y-0.5 pl-5">
              {r.faltantes.slice(0, 3).map((f) => (
                <li key={f.alternativa}>
                  {f.faltam_nomes.length ? <>a assinatura de <b className="text-ink">{f.faltam_nomes.join(" e ")}</b></> : "nada a mais de assinatura"}
                  <span className="text-muted"> ({f.descricao})</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </Secao>

      {r.caminhos_invalidos.length > 0 && (
        <Secao titulo="Caminhos que não valem" descricao={`Delegações apresentadas que não conferem poder para esta ${compra ? "compra" : "venda"} — e por quê.`}>
          <div className="space-y-3">
            {r.caminhos_invalidos.map((b) => (
              <Painel key={b.id} className="overflow-hidden">
                <div className="flex flex-wrap items-center gap-2 border-b border-line bg-bad-soft/60 px-4 py-2.5 text-[13.5px]">
                  <SevTag sev="bloqueio" />
                  <b className="text-ink">{b.pessoas.map((p) => p.nome).join(", ")}</b>
                  <span className="text-muted">por {b.descricao}</span>
                </div>
                {b.achados.filter((a) => a.severidade === "bloqueio").map((a, i) => <ItemAchado key={i} a={a} />)}
              </Painel>
            ))}
          </div>
        </Secao>
      )}

      {pend.filter((p) => p.satisfeita !== true).length > 0 && (
        <Secao titulo="Pendências" descricao="Condições do contrato que precisam ser comprovadas.">
          <Painel>
            {pend.filter((p) => p.satisfeita !== true).map((p, i) => (
              <div key={i} className="flex items-start gap-3 border-t border-line px-4 py-3 first:border-t-0">
                <div className="w-[84px] shrink-0 pt-0.5"><SevTag sev={p.satisfeita === false ? "bloqueio" : "alerta"} /></div>
                <div className="min-w-0 flex-1">
                  <div className="text-[13.5px] font-medium text-ink">{p.descricao}</div>
                  {p.detalhe && <div className="text-[13px] text-ink-2">{p.detalhe}</div>}
                  <Citacao fonte={p.fontes[0]} />
                </div>
              </div>
            ))}
          </Painel>
        </Secao>
      )}

      <Secao titulo="Verificações" descricao="Tudo o que foi conferido, do mais grave ao que passou — com fundamento legal e a citação do documento.">
        <Painel>{achados.length ? achados.map((a, i) => <ItemAchado key={i} a={a} />) : (
          <div className="px-4 py-3 text-[13px] text-muted">Sem verificações registradas.</div>
        )}</Painel>
      </Secao>
    </div>
  );
}
