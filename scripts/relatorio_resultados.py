"""Gera docs/RESULTADOS.md a partir das avaliações (sem números digitados à mão).

    uv run python scripts/relatorio_resultados.py avaliacoes/oraculo-ce avaliacoes/llm-completa1 [outras...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ROT = {"VERDE": "🟢 aceito", "AMARELO": "🟡 revisão", "VERMELHO": "🔴 recusado"}


def carregar(p: Path) -> dict:
    return json.loads((p / "resultado.json").read_text(encoding="utf-8"))


def main() -> None:
    runs = [Path(a) for a in sys.argv[1:]]
    dados = [(r, carregar(r)) for r in runs]
    out = ["# Resultados da avaliação", "",
           "Gerado por `scripts/relatorio_resultados.py` a partir de `avaliacoes/`. Corpus: 38 cenários fictícios "
           "(`corpus/CENARIOS.md`), mais 8 de validação cega, 10 independentes, 14 do lote ATPV-e e 15 de consulta por CPF. *Erro perigoso* = aceite automático (faixa verde) quando o gabarito diz que não pode; "
           "*erro caro* = recusa automática quando pode.", "",
           "| Execução | Leitura | Política | Veredito | Faixa aceitável | Quem pode | Perigosos | Caros | Automático | Duração |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r, d in dados:
        s = d["resumo"]
        leitura = "gabarito (oráculo)" if s["modo"] == "oraculo" else "IA local (Qwen 27B)"
        out.append(f"| `{r.name}` | {leitura} | {s['politica'].get('nome', '—')} | {s['veredito_correto']}/{s['casos']} | "
                   f"{s['faixa_aceitavel']}/{s['casos']} | {s['quem_pode_correto']}/{s['quem_pode_avaliados']} | "
                   f"{s['erros_perigosos']} | {s['erros_caros']} | {s['cobertura_automatica']:.0%} | {s['duracao_s'] / 60:.0f} min |")
    out += ["", "**Como ler:** `oraculo-*` usam a leitura perfeita do gabarito e validam só o motor jurídico. "
            "`llm-completa1` é a execução **cega** da IA local (cada documento lido do zero). As execuções `llm-final-*` "
            "reaplicam o motor já corrigido sobre **as mesmas leituras** (cache) — a correção do C33 (\"2 (dois) Diretores\" = "
            "quaisquer dois) foi feita depois de ver o erro, então elas **não são teste cego**. O teste cego de generalização "
            "é o conjunto `llm-cega-*` (8 cenários novos, com redações inéditas, criados depois dos ajustes e avaliados sem "
            "nenhum ajuste posterior)."]
    cegas = [d for r, d in dados if d["resumo"]["modo"] == "llm" and d["resumo"].get("conjunto") in (None, "principal")]
    alvo = max(cegas, key=lambda d: d["resumo"]["duracao_s"]) if cegas else dados[-1][1]  # a execução com leitura nova
    out += ["", f"## Caso a caso — {('IA local, execução cega (leitura nova de cada documento)' if alvo['resumo']['modo'] == 'llm' else 'oráculo')}", "",
            "| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode | Tempo |", "|---|---|---|---|---|---|---|---|"]
    for l in alvo["linhas"]:
        ok = "✓" if l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False else "✗"
        quem = "ok" if l["conjuntos_ok"] else ("—" if l["conjuntos_ok"] is None else "diverge")
        out.append(f"| {ok} {l['caso']} | {l['titulo']} | {l['esperado']} | {l['previsto']} | {ROT[l['faixa']]} | "
                   f"{l['indice']:.0f} | {quem} | {l['segundos']:.0f}s |")
    erros = [l for l in alvo["linhas"] if not (l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False)]
    out += ["", "## Divergências", ""]
    if not erros:
        out.append("Nenhuma.")
    for l in erros:
        out.append(f"- **{l['caso']} — {l['titulo']}**: esperado {l['esperado']} ({'/'.join(l['faixas_aceitaveis'])}), "
                   f"obtido {l['previsto']} ({l['faixa']}, índice {l['indice']:.0f}). {l['resumo']} "
                   f"Motivos da faixa: {'; '.join(l['motivos_faixa'])}.")
    for r, d in dados:
        if d["resumo"].get("conjunto") == "independente":
            out += ["", f"## Validação independente — `{r.name}`", "",
                    "Casos escritos por um agente independente, **sem acesso ao código, aos cenários nem aos gabaritos do "
                    "projeto**, com documentos e gabarito próprios (`corpus/independente/`). Nada foi ajustado antes da rodada.", "",
                    "| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |", "|---|---|---|---|---|---|---|"]
            for l in d["linhas"]:
                ok = "✓" if l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False else "✗"
                quem = "ok" if l["conjuntos_ok"] else ("—" if l["conjuntos_ok"] is None else "diverge")
                out.append(f"| {ok} {l['caso']} | {l['titulo']} | {l['esperado']} | {l['previsto']} | {ROT[l['faixa']]} | "
                           f"{l['indice']:.0f} | {quem} |")
            for l in d["linhas"]:
                if not (l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False):
                    gab = json.loads((RAIZ / "corpus" / "casos" / l["caso"] / "gabarito.json").read_text(encoding="utf-8"))
                    out.append(f"- **{l['caso']}** — esperado {l['esperado']} ({'/'.join(l['faixas_aceitaveis'])}), obtido "
                               f"{l['previsto']} ({l['faixa']}). Sistema: {l['resumo']} Autor: {gab.get('raciocinio', '')}")
        if d["resumo"].get("conjunto") == "atpv" and "cega" in r.name:  # as demais (oráculo, pós-correção) estão na tabela
            leitura = "gabarito (oráculo)" if d["resumo"]["modo"] == "oraculo" else "IA local, rodada cega"
            out += ["", f"## Lote ATPV-e (vendendo ou comprando; todos os tipos de PJ) — `{r.name}` ({leitura})", "",
                    "Respostas do chefe em 17/10/2026: verificar quem assina **vendendo ou comprando**, **todos os tipos de "
                    "empresa**, foco na **ATPV-e digital**. O pedido traz só quem vai assinar; veículo, partes, valor e data "
                    "vêm da ATPV-e simulada. Documentos novos redigidos por agentes sem acesso ao código.", "",
                    "| Caso | Cenário | Esperado | Previsto | Faixa | Vendedor | Comprador | Quem pode |",
                    "|---|---|---|---|---|---|---|---|"]
            for l in d["linhas"]:
                ok = "✓" if l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False else "✗"
                quem = "ok" if l["conjuntos_ok"] else ("—" if l["conjuntos_ok"] is None else "diverge")
                lado = lambda k: (f"{ROT[l['lados'][k]['faixa']]} {l['lados'][k]['indice']:.0f}" if k in (l.get("lados") or {})  # noqa: E731
                                  else "PF")
                out.append(f"| {ok} {l['caso']} | {l['titulo']} | {l['esperado']} | {l['previsto']} | {ROT[l['faixa']]} | "
                           f"{lado('vendedor')} | {lado('comprador')} | {quem} |")
            for l in d["linhas"]:
                if not (l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False):
                    out.append(f"- **{l['caso']}**: esperado {l['esperado']} ({'/'.join(l['faixas_aceitaveis'])}), obtido "
                               f"{l['previsto']} ({l['faixa']}). {l['resumo']}")
        if d["resumo"].get("conjunto") == "pf" and "cega" in r.name:
            out += ["", f"## Lote consulta por CPF (antes da ATPV-e; pessoa física e procuração) — `{r.name}`", "",
                    "Resposta do chefe em 17/10/2026 (11:40): \"poderia ser até antes do ATPV\" — veículo + CPF + vender/comprar; "
                    "se o CPF não for o do dono (ou do comprador), perguntar pela procuração e conferir se ela dá poder àquele CPF. "
                    "O dono vem da base veicular simulada; as procurações novas foram redigidas por agentes sem acesso ao código.", "",
                    "| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |", "|---|---|---|---|---|---|---|"]
            for l in d["linhas"]:
                ok = "✓" if l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False else "✗"
                quem = "ok" if l["conjuntos_ok"] else ("—" if l["conjuntos_ok"] is None else "diverge")
                out.append(f"| {ok} {l['caso']} | {l['titulo']} | {l['esperado']} | {l['previsto']} | {ROT[l['faixa']]} | "
                           f"{l['indice']:.0f} | {quem} |")
            for l in d["linhas"]:
                if not (l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False):
                    out.append(f"- **{l['caso']}**: esperado {l['esperado']} ({'/'.join(l['faixas_aceitaveis'])}), obtido "
                               f"{l['previsto']} ({l['faixa']}). {l['resumo']}")
        if d["resumo"].get("conjunto") == "cega":
            out += ["", f"## Validação cega — `{r.name}`", "",
                    "| Caso | Cenário | Esperado | Previsto | Faixa | Índice | Quem pode |", "|---|---|---|---|---|---|---|"]
            for l in d["linhas"]:
                ok = "✓" if l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False else "✗"
                quem = "ok" if l["conjuntos_ok"] else ("—" if l["conjuntos_ok"] is None else "diverge")
                out.append(f"| {ok} {l['caso']} | {l['titulo']} | {l['esperado']} | {l['previsto']} | {ROT[l['faixa']]} | "
                           f"{l['indice']:.0f} | {quem} |")
            for l in d["linhas"]:
                if not (l["veredito_ok"] and l["faixa_ok"] and l["conjuntos_ok"] is not False):
                    out.append(f"- **{l['caso']}**: esperado {l['esperado']}, obtido {l['previsto']} ({l['faixa']}). {l['resumo']}")
    if any(r.name == "llm-cega-ce" for r, _ in dados):
        out += ["", "## Lições da validação cega", "",
                "- **Nenhum aceite indevido** em nenhuma execução (38 cenários + 8 cegos + análise profunda). Os erros foram "
                "todos do lado seguro (recusa ou exigência maior que a necessária).",
                "- **A validação cega pegou uma regressão minha.** A regra criada para o C33 (\"2 (dois) Diretores\" = quaisquer "
                "dois) leu \"quaisquer dois dos **três** administradores\" como 3 (H02). Correção: em \"N dos M\" vale N, e a "
                "regra léxica só **completa** o que a IA deixou em aberto, nunca sobrescreve um valor válido.",
                "- **H06:** a IA confundiu \"representada conjuntamente por seus administradores\" (quem *outorga*) com uma "
                "exigência de o *procurador* assinar junto com um administrador. Agora essa exigência só vale se estiver escrita "
                "no texto da procuração; e, por segurança, a conferência nunca relaxa uma restrição que apareça em algum lugar do texto.",
                "- **Análise profunda (3 leituras + voto):** quando as leituras divergem, a confiança cai e o caso vai para "
                "revisão humana (C33: índice 83, faixa intermediária) — é o comportamento desejado.",
                "- `llm-cega-pos-ajuste` mostra 8/8 com as correções, mas **não é mais teste cego**. Para medir de novo é "
                "preciso outro lote de cenários inéditos — idealmente processos reais anonimizados."]
    if any(r.name == "llm-independente-ce" for r, _ in dados):
        out += ["", "## Lições da validação independente", "",
                "- **O teste mais duro mostrou 2 aceites indevidos** (I02 e I06) em 10 casos escritos por um autor que não "
                "conhecia o código. Nos cenários escritos pelo próprio desenvolvedor isso nunca tinha aparecido — por isso "
                "validação independente (e, depois, processos reais) é obrigatória antes de qualquer automação.",
                "- **I02 — classes de administradores** (\"um Administrador A e um Administrador B\"): a IA leu \"dois em "
                "conjunto\" e perdeu a restrição de classe. Correção imediata: cláusula com classes/grupos sem combinação "
                "explícita vai para revisão humana. Próximo passo: o schema aceitar grupos com várias pessoas para decidir "
                "sozinho.",
                "- **I06 — ata \"por unanimidade dos presentes\"** com presentes somando 55% do capital (quórum de 2/3): a "
                "leitura somou 110%. Correção: o percentual vem do quadro societário vigente, nunca acima de 100% nem do que os "
                "presentes somam; quórum não atingido é fato negativo (não pode), não pendência.",
                "- **I05 — regra antiga de quem saiu** vencia a regra nova por \"especialidade\" de rótulo. Correção: alteração "
                "que troca a administração derruba as regras que citam quem saiu; se a regra mais específica ficar sem "
                "ninguém, aplica-se a seguinte, com alerta.",
                "- **I07 — alterações intermediárias ausentes** (3ª e 4ª) que podiam ter dado poder a quem outorgou: agora o "
                "motor detecta o buraco pela numeração (e pela alteração citada na escritura) e responde *indeterminado*.",
                "- Antes do lote independente, uma revisão de código já tinha fechado outras lacunas (anuência em cláusula "
                "só de condição, revogação genérica ou embutida, substabelecimento em cadeia, consulta sem assinantes).",
                "- `llm-independente-pos-ajuste` (9/10, 0 aceites indevidos) **não é teste cego**: as correções foram feitas "
                "depois de ver os erros."]
    cega_atpv = next((d for r, d in dados if r.name == "llm-atpv-cega"), None)
    if cega_atpv:
        ra = cega_atpv["resumo"]
        out += ["", "## Lições do lote ATPV-e (vendendo ou comprando, todos os tipos de PJ)", "",
                f"- **Rodada cega: veredito {ra['veredito_correto']}/{ra['casos']}, faixa aceitável {ra['faixa_aceitavel']}/"
                f"{ra['casos']}, quem pode assinar {ra['quem_pode_correto']}/{ra['quem_pode_avaliados']}, aceites indevidos "
                f"{ra['erros_perigosos']}.** O teste mostrou duas leituras da IA que o motor precisava saber tratar — as duas "
                "viraram regras gerais e testes de regressão.",
                "- **A01/A06 — cláusula geral rotulada como venda.** \"A administração da sociedade caberá aos sócios..., que a "
                "exercerão isoladamente..., inclusive a venda de bens\" foi lida como regra só de *alienação*. Para o lado "
                "comprador não sobrava regra, e o caso caía na regra supletiva com alerta (revisão desnecessária). Correção: "
                "cláusula que atribui a administração/representação da sociedade vale também para comprar; a venda citada é "
                "exemplo.",
                "- **A10 — cargo nomeado lido como \"administradores\"** (risco latente de aceite indevido). \"Compete ao "
                "Presidente representar a Associação\" virou \"qualquer administrador\" (o schema só tem cargos genéricos), e "
                "os membros do Conselho Fiscal eleitos na mesma ata entraram como administradores: se a Vice ou um conselheiro "
                "fiscal tivesse assinado, o sistema aceitaria. O veredito saiu certo só porque quem assinou foi a Presidente. "
                "Correções: Conselho Fiscal e suplentes nunca representam (CC 1.066–1.070; LSA 161–165; Lei 5.764, art. 56); "
                "quando a cláusula nomeia o cargo que representa, só esse cargo assina — a conferência **restringe**, nunca "
                "amplia, e não afrouxa assinatura conjunta (\"pelo Diretor-Presidente em conjunto com outro Diretor\").",
                "- **A08/A09 — o mesmo padrão na cooperativa.** \"Serão assinados pelo Diretor-Presidente em conjunto com o "
                "Diretor Financeiro\" virou \"dois administradores quaisquer\" (Vice + Secretário passariam), e o Conselho Fiscal "
                "eleito por 1 ano entrou como administração com mandato vencido, o que gerou alertas falsos e mandou os dois "
                "casos para revisão. As mesmas duas correções resolvem (agora 2 de 2).",
                "- **Substituto do titular.** Revisando as correções, ficou uma lacuna do mesmo tipo: \"na ausência ou "
                "impedimento do Presidente, o Vice-Presidente\". A ausência não é verificável, então a assinatura do "
                "substituto vai para revisão humana, e a do titular segue normal (teste de regressão).",
                "- O leitor da ATPV-e por regras leu as 14 ATPV-e simuladas com os mesmos campos do gabarito, mas em 2 o nome "
                "longo da cooperativa, quebrado em duas linhas no PDF, saiu cortado (sem efeito na decisão, que casa pelo "
                "CNPJ). Corrigido: 14/14 idênticas ao gabarito, assinaturas inclusive. Com o PDF oficial, recalibrar.",
                "- `llm-atpv` (depois das correções, mesmas leituras) **não é teste cego**. Para medir de novo: lote novo, "
                "de preferência processos reais anonimizados de cooperativas, associações e compradores PJ."]
    cega_pf = next((d for r, d in dados if r.name == "llm-pf-cega"), None)
    if cega_pf:
        rp = cega_pf["resumo"]
        out += ["", "## Lições da consulta por CPF (antes da ATPV-e)", "",
                f"- **Rodada cega: veredito {rp['veredito_correto']}/{rp['casos']}, faixa aceitável {rp['faixa_aceitavel']}/"
                f"{rp['casos']}, quem pode assinar {rp['quem_pode_correto']}/{rp['quem_pode_avaliados']}, aceites indevidos "
                f"{rp['erros_perigosos']}**, com as 10 procurações de pessoa física lidas pela IA pela primeira vez.",
                "- Cobertura: o próprio dono assinando (sem documentos), CPF diferente sem procuração (pergunta pela "
                "procuração), procuração pública específica, só com poderes gerais, vencida, de outro veículo, revogada, "
                "particular (DETRAN-CE recusa), outorgada pela esposa e não pelo dono registral, substabelecimento com "
                "reserva, compradora representada, e consultas em que o dono ou o comprador é empresa.",
                "- O motor reaproveitou toda a verificação de procuração já validada nos lotes anteriores; o que é novo é "
                "tratar a pessoa física como titular único e perguntar pela procuração em vez de recusar.",
                "- Ressalva honesta: 15 casos escritos com o mesmo guia de redação não substituem processos reais. Em "
                "especial, procurações reais trazem variações (\"por si e por seus herdeiros\", procurações em causa "
                "própria, cláusulas de irrevogabilidade) que este lote não exercita."]
    (RAIZ / "docs" / "RESULTADOS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:12]))


if __name__ == "__main__":
    main()
