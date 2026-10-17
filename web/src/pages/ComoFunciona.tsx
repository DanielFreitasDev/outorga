import { useEffect, useState } from "react";
import { ArrowLeftRight, ArrowRight, Bot, Building2, FileStack, FileText, FolderInput, Gavel, Gauge, Lock, ScrollText, SpellCheck2, X, Check } from "lucide-react";
import { api } from "../lib/api";
import type { ResumoAvaliacao } from "../lib/types";
import { pct } from "../lib/format";
import { CabecalhoPagina, Painel, Secao } from "../components/ui";
import { Medidor } from "../components/Medidor";

const ETAPAS = [
  { icone: FileStack, titulo: "ATPV-e e documentos", texto: "A ATPV-e (veículo, vendedor, comprador, assinaturas) e os documentos de cada empresa: contrato social e alterações, estatuto e atas, CCMEI, procurações, substabelecimentos, revogações e CRLV — PDF digital, escaneado (OCR) ou DOCX." },
  { icone: Bot, titulo: "Leitura pela IA local", texto: "Um modelo generativo (Qwen, na própria máquina) lê como advogado e extrai fatos em JSON com a citação literal de cada um." },
  { icone: SpellCheck2, titulo: "Conferência léxica", texto: "Regras determinísticas conferem a leitura: forma de atuação, escopo do bem, poderes, prazos. Se discordam, o texto prevalece." },
  { icone: Gavel, titulo: "Motor de regras jurídicas", texto: "Regime vigente na data da venda, especialidade das cláusulas, alçadas, deliberações e a cadeia de procurações e substabelecimentos." },
  { icone: Gauge, titulo: "Índice e faixa", texto: "Índice de aceitação de 0 a 100 com três faixas: aceite, revisão humana e recusa — limiares calibráveis." },
  { icone: ScrollText, titulo: "Parecer § 7º", texto: "Outorgante, outorgado, poderes, prazo e revogação, com fundamento legal, citações e hash dos documentos." },
];

export function ComoFunciona() {
  const [runs, setRuns] = useState<ResumoAvaliacao[]>([]);
  useEffect(() => { api.avaliacoes().then(setRuns).catch(() => undefined); }, []);
  const oraculo = runs.find((r) => r.modo === "oraculo");
  const llm = runs.find((r) => r.modo === "llm" && r.casos >= 30);

  return (
    <div className="max-w-[1080px]">
      <CabecalhoPagina titulo="Como funciona"
        sub="Leitura semântica por IA generativa, conferida por regras jurídicas e com uma faixa intermediária para o que não for certeza." />

      <Painel className="mb-8 border-l-4 border-l-accent p-5">
        <div className="text-[12px] font-medium uppercase tracking-wide text-muted">Resolução CONTRAN nº 1.027/2026 — art. 28, § 7º</div>
        <blockquote className="mt-2 text-[15px] leading-relaxed text-ink">
          “Quando o antigo ou o novo proprietário for pessoa jurídica, a assinatura será admitida mediante comprovação eletrônica
          dos poderes do signatário, por consulta a bases oficiais ou por instrumento de outorga verificável, com identificação do
          outorgante, do outorgado, dos poderes conferidos, do prazo de validade e de eventual revogação […]”
        </blockquote>
        <p className="mt-2 text-[13px] text-muted">O Outorga produz exatamente esses cinco elementos para cada lado pessoa jurídica da ATPV-e — o antigo e o novo proprietário —, com a trilha de evidências.</p>
      </Painel>

      <Secao titulo="O caminho de um pedido">
        <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {ETAPAS.map((e, i) => {
            const I = e.icone;
            return (
              <div key={e.titulo} className="relative rounded-xl border border-line bg-surface p-4 shadow-card">
                <div className="mb-2 flex items-center gap-2">
                  <span className="grid size-8 place-items-center rounded-lg bg-accent-soft text-accent"><I className="size-4" /></span>
                  <span className="num text-[12px] text-muted">{i + 1}</span>
                </div>
                <div className="text-[13.5px] font-semibold text-ink">{e.titulo}</div>
                <div className="mt-1 text-[12.5px] leading-snug text-muted">{e.texto}</div>
                {i < ETAPAS.length - 1 && <ArrowRight className="absolute -right-3 top-1/2 z-10 hidden size-5 -translate-y-1/2 rounded-full bg-bg text-muted xl:block" />}
              </div>
            );
          })}
        </div>
      </Secao>

      <Secao titulo="Vendendo ou comprando, qualquer tipo de empresa" descricao="A verificação é feita antes de assinar a ATPV-e, para cada lado que for pessoa jurídica.">
        <div className="grid gap-3 md:grid-cols-2">
          <Painel className="p-5 text-[13.5px] text-ink-2">
            <div className="mb-2 flex items-center gap-2 font-semibold text-ink"><ArrowLeftRight className="size-4 text-accent" />Os dois lados da ATPV-e</div>
            <ul className="list-disc space-y-1 pl-5">
              <li>Empresa <b className="text-ink">vendedora</b>: quem assina precisa de poder para <b className="text-ink">alienar</b> o veículo.</li>
              <li>Empresa <b className="text-ink">compradora</b>: quem assina precisa de poder para <b className="text-ink">adquirir</b> — procuração só de venda não serve para comprar, e uma restrição de compra não alcança a venda.</li>
              <li>Os documentos são separados por CNPJ; com PJ dos dois lados, o resultado da ATPV-e é o do lado mais fraco.</li>
              <li>Pessoa física assinando em nome próprio não tem poderes a comprovar. Se outro CPF assina por ela, o sistema pede a
                procuração e confere se foi dada pelo próprio dono (ou comprador), com poderes para o ato, para aquele veículo, no prazo e
                sem revogação.</li>
            </ul>
          </Painel>
          <Painel className="p-5 text-[13.5px] text-ink-2">
            <div className="mb-2 flex items-center gap-2 font-semibold text-ink"><Building2 className="size-4 text-accent" />Todos os tipos de empresa</div>
            <p>Ltda, SLU, S.A., empresário individual e MEI (CCMEI), EIRELI (hoje SLU), sociedade simples, cooperativa e associação.</p>
            <p className="mt-2">Nos estatutos, os cargos (“o Presidente em conjunto com o Diretor Financeiro”) são ligados às pessoas eleitas na ata de
              eleição vigente na data da operação — e uma restrição só para imóveis não alcança veículos.</p>
          </Painel>
        </div>
      </Secao>

      <Secao titulo="Antes da ATPV-e: consulta por CPF" descricao="A verificação pode rodar antes de existir a ATPV-e, só com o veículo e o CPF de quem vai assinar.">
        <Painel className="grid gap-4 p-5 md:grid-cols-3">
          {[
            { t: "1. Veículo", d: "Pela placa ou RENAVAM, o dono vem da base veicular (no protótipo, simulada): empresa ou pessoa física." },
            { t: "2. Vender ou comprar", d: "Quem vai assinar representa o proprietário (venda) ou o comprador (compra); só esse lado é verificado." },
            { t: "3. CPF de quem assina", d: "Empresa: o CPF tem poder pelo contrato/estatuto ou por procuração? Pessoa física: é o próprio dono? Se não for, o sistema pergunta pela procuração antes de recusar." },
          ].map((x) => (
            <div key={x.t} className="text-[13.5px] text-ink-2">
              <div className="mb-1 font-semibold text-ink">{x.t}</div>
              <p>{x.d}</p>
            </div>
          ))}
        </Painel>
      </Secao>

      <Secao titulo="Modo agente (local)" descricao="Para rodar sozinho, sem ninguém clicar: tudo na própria máquina.">
        <Painel className="grid gap-4 p-5 md:grid-cols-[1fr_1fr]">
          <div className="text-[13.5px] text-ink-2">
            <div className="mb-2 flex items-center gap-2 font-semibold text-ink"><FolderInput className="size-4 text-accent" />Pasta vigiada</div>
            <p>Cada pedido é uma subpasta (ou um .zip) com a ATPV-e e os documentos das empresas; um <span className="font-mono text-[12.5px]">pedido.json</span> com
              quem vai assinar é opcional. O agente processa quando a pasta para de mudar (ou tem o arquivo <span className="font-mono text-[12.5px]">PRONTO</span>),
              grava o parecer em PDF/HTML, o <span className="font-mono text-[12.5px]">resultado.json</span> e um resumo, registra na auditoria e move a
              entrada para <span className="font-mono text-[12.5px]">processados/</span>. Se a IA local estiver fora do ar, o pedido espera na fila.</p>
          </div>
          <pre className="scroll-thin overflow-x-auto rounded-lg border border-line bg-surface-2 p-3 font-mono text-[12px] leading-relaxed text-ink">{`outorga agente \\
  --entrada /dados/atpv/entrada \\
  --saida   /dados/atpv/saida

# cada pedido:
entrada/pedido-123/
  ATPV-e.pdf
  contrato_social.pdf
  procuracao.pdf
  pedido.json   (opcional)`}</pre>
        </Painel>
      </Secao>

      <Secao titulo="Por que a IA sozinha não basta" descricao="Teste real com o modelo local, sem a camada de conferência.">
        <Painel className="grid gap-0 overflow-hidden md:grid-cols-3">
          <div className="border-b border-line p-5 md:border-b-0 md:border-r">
            <div className="mb-2 flex items-center gap-2 text-[12px] font-medium uppercase tracking-wide text-muted"><FileText className="size-4" />Cláusula do contrato</div>
            <p className="text-[13.5px] leading-relaxed text-ink">
              “A administração da sociedade caberá aos sócios João e Maria, que a exercerão <mark className="fonte">indistintamente</mark>…”
            </p>
          </div>
          <div className="border-b border-line bg-bad-soft/50 p-5 md:border-b-0 md:border-r">
            <div className="mb-2 flex items-center gap-2 text-[12px] font-medium uppercase tracking-wide text-bad"><X className="size-4" />IA sozinha</div>
            <p className="text-[13.5px] leading-relaxed text-ink">Classificou como <b>assinatura conjunta</b> — mesmo “pensando” mais. Recusaria uma venda válida assinada só pelo João.</p>
          </div>
          <div className="bg-ok-soft/50 p-5">
            <div className="mb-2 flex items-center gap-2 text-[12px] font-medium uppercase tracking-wide text-ok"><Check className="size-4" />Com conferência léxica</div>
            <p className="text-[13.5px] leading-relaxed text-ink">“Indistintamente” = <b>cada um assina sozinho</b>. A correção fica registrada na análise e reduz a confiança, empurrando dúvidas para a revisão.</p>
          </div>
        </Painel>
      </Secao>

      <Secao titulo="As três faixas" descricao="índice = 50 + 50 × direção × confiança — direção +1 (pode), −1 (não pode), 0 (indeterminado).">
        <Painel className="grid items-center gap-6 p-5 md:grid-cols-[auto_1fr]">
          <Medidor indice={64} aceite={85} recusa={15} faixa="AMARELO" tamanho={240} />
          <div className="space-y-3 text-[13.5px]">
            <div><b className="text-ok">Aceito</b> — índice ≥ limiar de aceite e nenhum alerta: o sistema aceita sozinho.</div>
            <div><b className="text-warn">Faixa intermediária</b> — dúvida, alerta jurídico ou documento faltando: vai para o servidor, já com a lista do que conferir.</div>
            <div><b className="text-bad">Recusado</b> — índice ≤ limiar de recusa: procuração vencida, revogada, sócio sem poder etc.</div>
            <div className="text-muted">Os limiares são ajustados na tela “Faixa intermediária”, com casos rotulados e revisões humanas.</div>
          </div>
        </Painel>
      </Secao>

      <div className="grid gap-5 md:grid-cols-2">
        <Secao titulo="Privacidade" className="mt-7">
          <Painel className="flex gap-3 p-5 text-[13.5px] text-ink-2">
            <Lock className="mt-0.5 size-5 shrink-0 text-accent" />
            <div>O modelo de IA roda <b className="text-ink">na própria máquina</b> (llama.cpp, GPU local). Contratos, CPFs e endereços não
              saem do computador — nada é enviado a serviços externos. Um provedor em nuvem é opcional e precisa ser ligado explicitamente.</div>
          </Painel>
        </Secao>
        <Secao titulo="Validação" className="mt-7">
          <Painel className="p-5 text-[13.5px] text-ink-2">
            {oraculo && <div>Motor jurídico com leitura de gabarito: <b className="text-ink">{oraculo.veredito_correto}/{oraculo.casos}</b> vereditos,{" "}
              {oraculo.erros_perigosos} erro(s) perigoso(s).</div>}
            {llm ? <div className="mt-1">Com a IA local lendo os documentos: <b className="text-ink">{llm.veredito_correto}/{llm.casos}</b> vereditos,{" "}
              <b className={llm.erros_perigosos ? "text-bad" : "text-ok"}>{llm.erros_perigosos} erro(s) perigoso(s)</b>, {pct(llm.cobertura_automatica)} decidido automaticamente.</div>
              : <div className="mt-1 text-muted">A avaliação completa com a IA local aparece aqui quando concluída.</div>}
            <div className="mt-2 text-[12.5px] text-muted">Cenários fictícios com gabarito, redigidos como peças reais (JUCEC, cartórios), incluindo o lote ATPV-e: comprador PJ, PJ dos dois lados e os demais tipos de empresa.</div>
          </Painel>
        </Secao>
      </div>
    </div>
  );
}
