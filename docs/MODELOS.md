# Comparação de modelos de IA

17/10/2026. Parte 1 (Claude) concluída; parte 2 (modelos locais) em andamento. A IA do Outorga só **lê** os documentos e devolve os fatos com o trecho literal. Quem decide
é o motor de regras, que é o mesmo em todos os testes. Então a pergunta aqui é: **qual IA lê melhor, mais rápido e mais
barato?**

Duas frentes:

1. **IA por chave de API (Claude, da Anthropic):** os modelos atuais em todos os níveis de esforço, com custo real em dólares.
2. **IA local (GPU de 12 GB):** modelos abertos que cabem na RTX 3060, comparados com o Qwen3.8-27B usado no desenvolvimento.

## 1. Modelos Claude (API da Anthropic)

### Como foi testado

- **Quando e com o quê:** 17/10/2026, com uma chave da conta do Daniel (workspace `outorga`), SDK oficial `anthropic` 1.15.
- **Modelos:** os três modelos atuais (**Opus 5.5**, **Sonnet 5.5** e **Haiku 5.5**) em **todos os níveis de esforço**
  (`low`, `medium`, `high`, `xhigh`, `max`), e a geração anterior de cada linha (**Opus 5**, **Sonnet 5** e
  **Haiku 4.5**) no esforço padrão, como referência. O Fable 5.1 ficou de fora, como foi pedido (é o mais caro: US$ 10 de
  entrada e US$ 50 de saída por milhão de tokens). A geração 4.x também ficou de fora: é mais antiga e mais cara que
  as substitutas.
- **O que é o esforço:** é o quanto o modelo "pensa" antes de responder. Mais esforço significa mais tokens de
  raciocínio, que são cobrados como saída, e mais tempo.
- **Mesmos casos e mesmas regras:** os **85 casos** de todos os lotes (principal, cego, independente, ATPV-e e consulta
  por CPF), com a mesma política (DETRAN-CE) e o mesmo motor, e um cache de leituras separado para cada configuração.
- **Só o modelo pedido:** o fallback do servidor, que repassa a outro modelo um pedido recusado, ficou desligado.
- **Custo:** calculado a partir dos tokens que a própria API informa em cada resposta (entrada, escrita e leitura do
  cache de prompt, saída), multiplicados pela
  [tabela oficial de preços](https://platform.claude.com/docs/en/about-claude/pricing) de 17/10/2026.
- **Tempo por caso:** é a soma do tempo das leituras dos documentos do caso, como no uso normal, em que os documentos são
  lidos um depois do outro. Durante o teste, cada configuração fazia 8 leituras ao mesmo tempo.

Preços usados (US$ por milhão de tokens):

| Modelo | Entrada | Escrita no cache | Leitura do cache | Saída (inclui o raciocínio) |
|---|---|---|---|---|
| Opus 5.5 | 4,00 | 5,00 | 0,20 | 20,00 |
| Sonnet 5.5 | 2,00 | 2,50 | 0,10 | 10,00 |
| Haiku 5.5 (prompts de até 100 mil tokens) | 0,10 | 0,125 | 0,01 | 0,50 |
| Opus 5 | 5,00 | 6,25 | 0,50 | 25,00 |
| Sonnet 5 | 2,00 | 2,50 | 0,20 | 10,00 |
| Haiku 4.5 | 1,00 | 1,25 | 0,10 | 5,00 |

O script é o [`scripts/comparar_claude.py`](../scripts/comparar_claude.py), e os resultados de cada configuração ficam
em `avaliacoes/claude/<modelo>-<esforço>/`.

### Resultados

**Resumo:**

- **Os três modelos atuais leem bem.** Opus 5.5, Sonnet 5.5 e Haiku 5.5, do esforço `medium` para cima, acertaram de 83 a
  85 dos 85 casos em todas as rodadas, **sem nenhum aceite indevido**. Todos os erros deles foram casos mandados para
  revisão humana (faixa amarela), nunca uma aprovação automática errada.
- **Esforço acima de `medium` quase não melhorou a leitura.** A exceção é o Sonnet 5.5 em `xhigh`, que acertou o caso
  mais difícil nas duas rodadas, por 50% a mais de custo e o dobro do tempo. No `max`, o custo foi de 7 a 10 vezes maior
  e o tempo de 7 a 12 vezes maior, sem acertar nada a mais.
- **Entre 84 e 85, quase sempre é sorte.** O único caso que separa 84 de 85 (I02, administradores de classes A e B) às
  vezes sai certo e às vezes não, no mesmo modelo e no mesmo esforço. Por isso as configurações candidatas rodaram 2 ou 3
  vezes. Errar o I02 não é perigoso: o caso vai para revisão humana.
- **A geração anterior não compensa.** O Opus 5 e o Sonnet 5 acertaram o mesmo ou menos, mais devagar e mais caro. O Haiku
  4.5 aprovou um caso que devia recusar (leu poderes de **venda** numa procuração só de **compra**) e custou 4 vezes mais
  que o Haiku 5.5.
- **O Haiku 5.5 em `low` recusou automaticamente um caso válido** nas duas rodadas (erro caro). Do `medium` para cima, não.

**A tabela** junta as rodadas de cada configuração. O custo padronizado aplica a todas a mesma divisão entre cache frio
e quente (veja a nota abaixo da tabela). "Decididos sem revisão" é a parte dos casos em faixa verde ou vermelha.

| Modelo | Esforço | Rodadas | Acertos em cada rodada (de 85) | Aceites indevidos | Recusas indevidas | Decididos sem revisão | Segundos por caso | US$ por caso | US$ por 1.000 casos |
|---|---|---|---|---|---|---|---|---|---|
| Opus 5.5 | low | 2 | 84 · 84 | 0 | 0 | 78% | 21 | 0,0574 | 57,41 |
| Opus 5.5 | medium | 2 | 84 · 85 | 0 | 0 | 82% | 23 | 0,0618 | 61,76 |
| Opus 5.5 | high | 1 | 84 | 0 | 0 | 84% | 27 | 0,0670 | 67,02 |
| Opus 5.5 | xhigh | 1 | 84 | 0 | 0 | 82% | 38 | 0,0833 | 83,26 |
| Opus 5.5 | max | 1 | 84 | 0 | 0 | 85% | 171 | 0,2991 | 299,15 |
| Sonnet 5.5 | low | 2 | 84 · 84 | 0 | 0 | 85% | 15 | 0,0284 | 28,45 |
| Sonnet 5.5 | medium | 3 | 84 · 84 · 84 | 0 | 0 | 85% | 14 | 0,0289 | 28,90 |
| Sonnet 5.5 | high | 3 | 84 · 85 · 84 | 0 | 0 | 86% | 16 | 0,0297 | 29,72 |
| Sonnet 5.5 | xhigh | 2 | 85 · 85 | 0 | 0 | 87% | 29 | 0,0445 | 44,47 |
| Sonnet 5.5 | max | 1 | 84 | 0 | 0 | 86% | 187 | 0,2191 | 219,07 |
| Haiku 5.5 | low | 2 | 82 · 83 | 0 | 2 | 86% | 19 | 0,0017 | 1,72 |
| Haiku 5.5 | medium | 3 | 84 · 83 · 85 | 0 | 0 | 86% | 25 | 0,0025 | 2,51 |
| Haiku 5.5 | high | 2 | 83 · 83 | 0 | 0 | 85% | 34 | 0,0032 | 3,17 |
| Haiku 5.5 | xhigh | 1 | 84 | 0 | 0 | 86% | 58 | 0,0052 | 5,16 |
| Haiku 5.5 | max | 1 | 81 | 0 | 1 | 84% | 230 | 0,0197 | 19,71 |
| Opus 5 (anterior) | high | 1 | 84 | 0 | 0 | 85% | 31 | 0,0812 | 81,16 |
| Sonnet 5 (anterior) | high | 1 | 83 | 0 | 0 | 81% | 38 | 0,0407 | 40,75 |
| Haiku 4.5 (anterior) | padrão do modelo | 1 | 81 | 1 | 0 | 84% | 25 | 0,0115 | 11,54 |

**Nota sobre o custo.** O cache de prompt da Anthropic fica no servidor e é compartilhado entre os níveis de esforço do
mesmo modelo. Por isso a primeira configuração de cada modelo pagou a escrita do cache, e as seguintes leram de graça
(foi assim que o Sonnet 5.5 `low` saiu mais caro que o `medium` na conta real). O custo padronizado usa, para todas, a
divisão medida na primeira rodada de cada modelo (cache frio): 11% da entrada sem cache, 35% escrita no cache e 54%
lida do cache. É o que se espera no uso normal, em que cada documento é lido uma vez.

**O que a comparação ensinou ao motor (três correções):**

1. **Limite de valor de outro inciso.** O Haiku 5.5 `high` citou a cláusula de aprovação inteira, com os incisos I a IV.
   Uma heurística do motor pegou o "superior a R$ 300 mil" do inciso de **empréstimos** e o aplicou à **venda de
   veículos**. Como o veículo custava R$ 186 mil, o motor achou que a aprovação de 2/3 do capital não valia e aprovou
   sozinho. O defeito era do motor, e podia acontecer com qualquer modelo que citasse a cláusula inteira. Agora o limite
   só vale para o inciso em que está escrito (ou para todos, se estiver no cabeçalho). Com isso, o aceite indevido
   sumiu. As rodadas acima já usam o motor corrigido; o número da rodada cega aparece entre parênteses quando muda.
2. **Sentinela de leitura.** Se o texto do contrato tem uma cláusula de aprovação prévia que alcança veículos ou bens, e a
   leitura da IA não trouxe nenhuma regra de aprovação aplicável, o caso vai para revisão com o trecho da cláusula. Uma
   omissão da IA nunca vira aceite automático. Nenhuma leitura destas rodadas disparou a sentinela, e o gabarito
   continua 100%.
3. **Nomes que não são de pessoa.** O Gemma 4 12B (parte 2) escreveu `"null"` no lugar de nomes, e o motor criou a pessoa
   fantasma "null" nas combinações de quem pode assinar. Agora "null", "N/A", "administradores" e parecidos contam como
   nome vazio.

### Qual escolher

| Uso | Configuração | Por quê |
|---|---|---|
| **Padrão do Outorga** | **Sonnet 5.5, esforço `medium`** | 84, 84 e 84 de 85 nas 3 rodadas; nenhum aceite ou recusa indevida; o mais rápido (~14 s por caso); US$ 0,029 por caso |
| **Mais barato** | **Haiku 5.5, esforço `medium`** | 84, 83 e 85 de 85 nas 3 rodadas; nenhum aceite ou recusa indevida; ~25 s por caso; **US$ 0,0025 por caso** (12 vezes menos) |
| Qualidade máxima | Sonnet 5.5, esforço `xhigh` | 85 e 85 de 85: o único que acertou o caso mais difícil (I02) nas duas rodadas; ~29 s e US$ 0,045 por caso |
| Não vale a pena | Opus 5.5 (qualquer esforço) | mesmo acerto do Sonnet 5.5, pelo dobro do preço |
| Não vale a pena | qualquer modelo em `max` | 7 a 10 vezes mais caro e 7 a 12 vezes mais lento, sem acertar mais; no Haiku, o raciocínio passou de 64 mil tokens e algumas leituras falharam |
| Evitar | Haiku 5.5 `low`, Haiku 4.5 | recusas indevidas (`low`) e um aceite indevido (4.5) |

Com o crédito mensal de **US$ 200** do plano Max 20x, dá para ler cerca de **6.900 casos por mês** com o Sonnet 5.5
`medium`, ou cerca de **80.000** com o Haiku 5.5 `medium`. O gasto total desta comparação, com todas as rodadas,
foi de **US$ 108,94**.

## 2. Modelos locais (GPU)

Objetivo: descobrir se outro modelo aberto, que caiba numa GPU de 12 GB, lê os documentos melhor ou mais rápido que o
modelo usado no desenvolvimento, o **Qwen3.8-27B** (UD-Q2_K_XL, 9,8 GB, ~18 tokens/s).

### Como os modelos são escolhidos

Por pesquisa em rankings de modelos em português, trabalhos de PLN jurídico brasileiro, cartões dos modelos no Hugging
Face e relatos da comunidade (fóruns como o r/LocalLLaMA). Entram:

- modelos gerais fortes em português;
- modelos brasileiros e jurídicos, quando houver versão que rode no llama.cpp;
- modelos menores e mais rápidos, que poderiam rodar até sem GPU num servidor.

### Como cada modelo é testado

O script [`scripts/comparar_modelos.py`](../scripts/comparar_modelos.py) faz, para cada modelo:

1. baixa o GGUF e sobe um `llama-server` só para o teste (tudo na GPU, contexto de 12K, porta 8092);
2. roda a mesma avaliação dos outros testes, com um **cache de leituras próprio do modelo** (as leituras não se misturam);
3. mede a velocidade de geração, as chamadas, a temperatura máxima e a memória máxima da GPU;
4. desliga o servidor e apaga o arquivo do modelo (os resultados ficam em `avaliacoes/modelos/<modelo>/`).

A trava térmica fica em 70 °C (pausa) / 62 °C (retoma), e as mesmas regras e a mesma política valem para todos.

### Cuidado para a comparação ser justa

O motor de regras foi desenvolvido olhando as leituras do Qwen3.8-27B, e várias correções vieram de erros dele. Por isso:

- os resultados "depois das correções" do 27B são **otimistas** (o motor aprendeu com os erros dele);
- a referência justa do 27B são as **primeiras rodadas cegas** de cada lote ([`RESULTADOS.md`](RESULTADOS.md));
- o lote de **consulta por CPF (P01–P15)** não recebeu nenhuma correção depois da rodada cega, então é o terreno mais
  neutro para comparar modelos.

Os modelos Claude não têm esse problema: o motor nunca foi ajustado olhando leituras deles, então todas as rodadas do
Claude são cegas.

### Os candidatos

A pesquisa (17/10/2026) conferiu cada repositório e arquivo na API do Hugging Face e leu os relatos do r/LocalLLaMA de 2026.
Os candidatos, na ordem em que foram testados:

| Modelo | Arquivo GGUF (tamanho) | Por que entrou |
|---|---|---|
| Qwen3.6-35B-A3B (MoE) | `unsloth/Qwen3.6-35B-A3B-GGUF` → `UD-IQ4_XS` (17,7 GB) | 4 bits em vez de 2; relatos de 43–47 tokens/s numa RTX 3060 com os especialistas na RAM |
| Gemma 4 12B | `unsloth/gemma-4-12B-it-qat-GGUF` → `UD-Q4_K_XL` (6,7 GB) | treinado já pensando na quantização (QAT); bom em idiomas europeus |
| Qwen3.5-9B | `unsloth/Qwen3.5-9B-GGUF` → `UD-Q6_K_XL` (8,8 GB) | quase sem perda em 6 bits; forte em seguir instruções |
| Ministral 3 14B | `mistralai/Ministral-3-14B-Instruct-2512-GGUF` → `Q4_K_M` (7,7 GB) | português entre os idiomas oficiais; saída JSON nativa |
| Granite 4.2 8B | `ibm-granite/granite-4.2-8b-GGUF` → `Q6_K` (6,8 GB) | português testado pela IBM; saída estruturada no treino |

Ficaram de fora, com o motivo:
- **modelos brasileiros e jurídicos** (Tucano2, AMALIA, Gaia, Jurema, Juru, Rio, Bode): bases antigas, contexto curto, sem
  ajuste a instruções ou sem licença;
- **Sabiá-4**: só por API;
- **gpt-oss-20b**: o raciocínio não desliga, e o arquivo não cabe na VRAM livre;
- **Phi-4**: último lugar num teste de alucinação.

### Resultados

**Qwen3.6-35B-A3B (MoE, 17,7 GB): interrompido pela temperatura da CPU.** O arquivo não cabe nos ~10,5 GB livres da GPU.
Por isso metade dos "especialistas" do modelo ficou na RAM (`--n-cpu-moe 24`), e quem os calcula é o processador. Na
prática, o Ryzen 5 4600G ficou com os 6 núcleos ocupados (~550%) e chegou a **87 °C** em poucos minutos. O teste foi
interrompido no primeiro caso (que ele acertou), seguindo a regra de não esquentar a máquina. A velocidade medida foi de
**~20 tokens/s**, contando a leitura do prompt, contra ~18 do Qwen3.8-27B atual: nada que compense o calor. Os 43–47
tokens/s relatados no Reddit vieram de máquinas com CPU mais forte e mais VRAM livre.
