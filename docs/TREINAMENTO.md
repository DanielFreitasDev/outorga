# Dá para treinar um modelo só para o Outorga?

Estudo de viabilidade (17/10/2026). Resposta curta: **dá, nesta própria máquina, mas hoje não compensa**. O treino só vale a
pena se surgir uma exigência que os modelos atuais não atendem, como rodar num computador sem placa de vídeo forte.

## O que o treino resolveria (e o que não resolveria)

No Outorga, a IA **não decide** nada: ela só lê o documento e devolve os fatos em JSON, com o trecho literal. A decisão
jurídica é do motor de regras, que é testado e não muda com o modelo. Treinar (fazer *fine-tuning* de) um modelo melhora
só essa leitura.

Os modelos que já existem leem bem:

- os Claude atuais acertam 83 a 85 dos 85 casos de teste, sem nenhum aceite indevido, a partir de ~US$ 0,0025 por
  caso (Haiku 5.5) ([`MODELOS.md`](MODELOS.md));
- o Qwen3.8-27B local também acerta quase tudo, mas precisa de uma GPU de 12 GB e leva 1 a 2 minutos por caso.

Então o ganho possível de um treino não é acertar mais. É **fazer um modelo pequeno (4 a 8 bilhões de parâmetros) ler tão
bem quanto os grandes**. Um modelo pequeno roda mais rápido, cabe em GPUs mais baratas e, num servidor com memória rápida,
até sem GPU.

## O que seria preciso

### 1. Dados (a parte mais difícil)

| Item | Quanto | Observação |
|---|---|---|
| Exemplos revisados (documento → JSON de cada tarefa) | **300 a 1.000** | Estudos com esquema fixo mostram que algumas centenas de exemplos bem revisados bastam: ~500 pares para extração complexa em textos científicos ([Dagdelen et al.](https://arxiv.org/abs/2212.05238)); um modelo de 4B treinado com 432 exemplos subiu de 75% para 94% de acerto (relato no r/LocalLLaMA) |
| Exemplos para cláusulas raras | até 2 a 5 mil | só para cobrir variações incomuns |
| Conjunto de teste separado | os 85 casos atuais, mais documentos reais novos | **nunca** treinar com os casos de teste |

De onde viriam os dados:

- **documentos reais do DETRAN-CE, anonimizados** (contratos, alterações, estatutos, atas, procurações). Sem eles, o
  modelo aprende só o estilo dos documentos sintéticos. É o item mais importante e o que mais depende da LGPD;
- o **gerador de documentos sintéticos** do projeto ([`corpus/spec.py`](../corpus/spec.py)), com variações de redação e
  ruído de OCR;
- **rótulos feitos por um modelo grande** (destilação). O Claude Sonnet 5.5, por exemplo, lê cada documento, a conferência
  de trechos do Outorga confere se cada evidência existe no texto, e uma pessoa revisa uma amostra.

### 2. Máquina

A RTX 3060 de 12 GB dá conta com a técnica **QLoRA** (o modelo base fica em 4 bits e só um adaptador pequeno é treinado):

| Tamanho do modelo | Cabe na RTX 3060? | Observação |
|---|---|---|
| 8B | sim, com folga | o QLoRA de um 8B precisa de ~6 GB |
| 12–14B | provavelmente, com lote de 1 | ~7,5–8,5 GB no mínimo; não testado |
| 27B (o atual) | não | precisa de ~24 GB |

Fontes: [requisitos do Unsloth](https://unsloth.ai/docs/get-started/beginner-start-here/unsloth-requirements),
[benchmarks do Unsloth](https://unsloth.ai/docs/basics/unsloth-benchmarks). Para treinar, o serviço de transcrição (whisper)
teria de ser parado para liberar a GPU inteira.

### 3. Tempo e temperatura

Estimativa por cálculo, sem medição: 2.000 exemplos de ~3.500 tokens, em 3 passadas, levariam **9 a 14 horas** num modelo de
8B e 5 a 7 horas num de 4B. Com 5.000 exemplos, o tempo é 2,5 vezes maior.

A GPU passa de 80 °C sob carga contínua. Há dois caminhos:

- **limitar a potência da placa** (`nvidia-smi -pl`, precisa de administrador), o que deixa o treino mais lento e frio;
- **alugar uma GPU na nuvem** por algumas horas (poucos dólares). Isso só pode ser feito com dados sintéticos ou
  anonimizados, por causa da LGPD.

### 4. Ferramentas

- treino: [Unsloth](https://unsloth.ai) (ou Axolotl / LLaMA-Factory), com QLoRA;
- exportação: o modelo treinado vira um arquivo **GGUF** (`save_pretrained_gguf`, ou `convert_hf_to_gguf.py` +
  `llama-quantize` do llama.cpp);
- uso: o GGUF roda no mesmo `llama-server` de hoje. **O Outorga não muda nada**: só se troca `OUTORGA_LLM_MODELO`.

### 5. Cuidados conhecidos

- usar no treino **o mesmo modelo de conversa (chat template)** e o mesmo modo "sem raciocínio" usados em produção. Esse é
  o erro mais comum: o modelo vai bem no treino e mal no llama.cpp;
- calcular o erro só sobre a resposta, e misturar 10–20% de instruções gerais para o modelo não esquecer o resto;
- variar redação e simular OCR, para o modelo não decorar os documentos sintéticos;
- avaliar o modelo **na quantização em que ele vai rodar** (por exemplo, Q6), e não na precisão cheia;
- depois do treino, dá para encurtar o prompt de ~3 mil tokens, o que acelera todas as leituras.

## Plano, se um dia for necessário

1. **Escolher o modelo base:** o melhor modelo pequeno da comparação local ([`MODELOS.md`](MODELOS.md), parte 2), entre 4B
   e 8B.
2. **Juntar os dados:** 300 a 500 documentos reais anonimizados e mais 1.000 a 2.000 sintéticos, rotulados por um modelo
   grande e revisados por amostragem.
3. **Treinar** com QLoRA numa noite, com a placa limitada em potência ou numa GPU alugada.
4. **Avaliar** nos 85 casos e num lote novo de documentos reais. O modelo treinado só substitui o atual se não tiver nenhum
   aceite indevido e acertar pelo menos o mesmo que ele.

O maior custo é o tempo das pessoas para reunir e revisar os documentos, não a máquina.

## Recomendação

Hoje, **não treinar**. As opções prontas já cobrem os dois cenários:

- **com internet e sem restrição de dados:** um modelo Claude por chave de API, com custo de centavos por caso;
- **tudo local:** o Qwen3.8-27B na RTX 3060, ou o melhor modelo da comparação local.

O treino passa a valer a pena se o DETRAN-CE precisar rodar o Outorga em máquinas sem GPU de 12 GB, ou com volume tão alto
que a velocidade de um modelo pequeno faça diferença.
