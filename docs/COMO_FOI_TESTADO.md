# Como o protótipo foi construído e testado

Este documento registra **onde** e **como** o Outorga foi desenvolvido e avaliado: a máquina, a IA local, a stack de
software, a metodologia dos testes, a linha do tempo real de cada rodada e como reproduzir tudo. Os números vêm dos
arquivos em `avaliacoes/` e do cache de chamadas à IA em `.cache/leituras/` (cada chamada guarda duração e tokens).

## 1. A máquina

| Item | Valor |
|---|---|
| Sistema operacional | Kubuntu 26.04.1 LTS (Ubuntu com KDE), kernel 7.0.0, glibc 2.43 |
| Processador | AMD Ryzen 5 4600G — Zen 2, 6 núcleos / 12 threads, até 4,3 GHz, AVX2 (sem AVX-512) |
| Memória | 32 GB DDR4 dual-channel (~33 GB/s de leitura medidos) |
| GPU | NVIDIA GeForce RTX 3060, **12 GB** de VRAM, driver 595, CUDA 13.2, PCIe Gen3 x16 |
| Disco | NVMe 1 TB |
| Compartilhamento | a GPU ficou o tempo todo dividida com um serviço de transcrição de áudio (whisper, ~1,3 GB de VRAM) que já rodava na máquina |

É um **desktop comum**, não um servidor de IA. Um computador de escritório com uma GPU de 12 GB roda o protótipo.

## 2. A IA local

| Item | Valor |
|---|---|
| Software | **llama.cpp** (não é o Ollama), versão b11191, servidor `llama-server` com API compatível com a da OpenAI |
| Como foi instalado | compilado a partir do código-fonte, com o **CUDA Toolkit 13.2.2** instalado no espaço do usuário (`~/local-ai`, sem `sudo`, sem tocar no driver nem nos pacotes do sistema). Arquitetura CUDA `86` (RTX 30xx), Flash Attention ligado |
| Modelo | **Qwen3.8-27B** (27 bilhões de parâmetros, pesos abertos), formato GGUF |
| Quantização usada nos testes | **UD-Q2_K_XL** (Unsloth, ~2,7 bits por peso, arquivo de 9,8 GB) — a que cabe na GPU junto com o whisper |
| Contexto | 32 mil tokens; cache de atenção (KV) em q4_0; decodificação especulativa por n-gramas |
| Velocidade medida | ~18 tokens/s gerados; leitura do documento (prefill) na casa de centenas de tokens/s |
| Modo | sem "raciocínio" (thinking desligado) e com **saída estruturada**: o servidor só aceita respostas que obedecem ao JSON Schema de cada tarefa |
| Temperatura | uma trava térmica no próprio Outorga (`OUTORGA_TEMP_MAX=70`, `OUTORGA_TEMP_RETOMAR=62`) pausa a leitura entre chamadas quando a GPU passa de 70 °C e só retoma abaixo de 62 °C. Durante leituras longas a placa chegou a ~78–83 °C, abaixo do limite de proteção dela (~93 °C) |

Qualquer servidor compatível com a API da OpenAI serve no lugar do llama.cpp: Ollama, LM Studio, vLLM. Ver
[`IA.md`](IA.md), que também explica como usar IA por chave de API (Anthropic, OpenAI, Google, Groq, OpenRouter etc.).

### Dá para rodar sem GPU, só no processador?

Dá, mas fica **lento** para uso no balcão. A geração de texto de um modelo de 27B no processador é limitada pela
velocidade da memória RAM. Medido nesta máquina (DDR4, ~33 GB/s):

| Configuração | Leitura do prompt | Geração | Observação |
|---|---|---|---|
| GPU RTX 3060 (configuração dos testes) | centenas de tokens/s | ~18 tokens/s | um caso típico (2–3 documentos) leva ~1–2 min |
| Modelo dividido: parte na GPU, parte na CPU (Q4_K_S) | ~317 tokens/s | ~4,5 tokens/s | 3–5× mais lento |
| **Só CPU**, o mesmo modelo dos testes (UD-Q2_K_XL), 6 threads | **8,5 tokens/s** | ~1–3 tokens/s (estimado) | medido em 17/10/2026 (seção 7): **inviável** neste desktop |

Na prática, só no processador um único documento levaria de 20 a 30 minutos nesta máquina, e a CPU chegou a 93 °C.
As saídas são:

1. **Servidor com CPU forte e memória rápida**, como um Xeon/EPYC com DDR5 em vários canais (200–400 GB/s), que acelera
   5–10×. Ou uma GPU dedicada de 16–24 GB.
2. **Modelo menor** (7–14B) no processador: mais rápido, mas **precisa ser revalidado** com os mesmos lotes de teste
   antes de ser usado.
3. **IA por chave de API** (Anthropic, OpenAI etc.): rápido e sem hardware. Os documentos, porém, saem da máquina, o que
   exige avaliação de LGPD; o chefe pediu execução local.

Uma medição de ponta a ponta só em CPU, com o mesmo modelo dos testes, está na seção 7.

## 3. A stack de software

| Camada | Tecnologia |
|---|---|
| Linguagem e pacotes | Python 3.14 (compatível com 3.12+), gerenciado com **uv** |
| API e servidor web | FastAPI + Uvicorn; progresso das análises por SSE |
| Leitura de documentos | PyMuPDF (PDF), python-docx (DOCX), **Tesseract 5.5** (OCR em português para documentos escaneados) |
| IA | cliente próprio para servidores compatíveis com a OpenAI (llama.cpp) e SDK oficial da Anthropic (opcional); saídas validadas com **Pydantic** |
| Conferência | léxico jurídico próprio + RapidFuzz (ancoragem das citações no texto original) |
| Decisão | motor de regras jurídicas em Python puro (determinístico) |
| Parecer | Jinja2 + **WeasyPrint** (HTML → PDF) |
| Persistência e auditoria | SQLite, com trilha de auditoria encadeada por hash SHA-256 |
| Interface | **React 19** + TypeScript + Vite + Tailwind CSS 4; ícones Lucide |
| Testes | pytest (253 testes), avaliação contra gabarito (`outorga avaliar`), testes de interface no navegador com Playwright |
| Ferramenta de desenvolvimento | o protótipo foi escrito com o **Claude Code** (Anthropic) operando na própria máquina; a IA que **lê os documentos** dentro do protótipo é a IA local acima |

## 4. Metodologia dos testes

A avaliação mede o sistema contra um **gabarito**: para cada cenário, um especialista fictício define quem pode assinar
e o resultado esperado. Todos os documentos são **fictícios**, com CPFs, CNPJs e placas de dígitos verificadores válidos
só para exercitar os validadores.

- **Corpus:** 85 cenários. São 38 principais (os exemplos do áudio do chefe e as regras do Código Civil), 8 de validação
  cega, 10 de um autor independente, 14 de ATPV-e com empresa dos dois lados e novos tipos de empresa, e 15 de
  consulta por CPF antes da ATPV-e. Os documentos viram PDFs com aparência real; um cenário usa PDF escaneado (OCR).
- **Dois modos de execução:**
  - **Oráculo:** o motor recebe a leitura perfeita do gabarito. Mede só as regras jurídicas.
  - **IA local:** cada documento é lido do zero pelo Qwen. Mede o sistema inteiro: leitura, conferência e decisão.
- **Teste cego:** cenários criados **depois** dos ajustes e avaliados sem nenhum ajuste posterior. Os documentos dos três
  últimos lotes foram redigidos por **agentes independentes que não tinham acesso ao código**, só ao guia de redação e aos
  fatos de cada cenário.
- **Métricas:**
  - veredito certo (pode / não pode / pendente);
  - faixa aceitável (aceito / revisão / recusado);
  - "quem pode assinar" igual ao gabarito;
  - **erro perigoso**: aceite automático quando não podia (o pior erro);
  - **erro caro**: recusa automática quando podia;
  - cobertura automática: casos decididos sem revisão humana.
- **Honestidade:** quando um teste cego revela um erro, a correção é feita como regra geral e vira teste de regressão,
  mas a rodada corrigida é marcada como **"não é teste cego"**. Os números cegos ficam registrados como saíram.

## 5. Linha do tempo real (16 e 17/10/2026)

O trabalho começou na noite de 16/10, com a pesquisa jurídica, a especificação dos cenários, o motor e a interface.
A GPU **não ficou ocupada a noite toda**. As chamadas à IA local somam **1,98 hora de processamento** em quatro janelas,
mais **23 minutos de pausas térmicas**. Entre as janelas o servidor da IA ficou desligado ou ocioso enquanto o código
era escrito. Foram **170 leituras**, com 507 mil tokens de entrada e 142 mil gerados.

| Rodada (17/10) | Início → fim | Duração | Casos | Veredito | Aceites indevidos |
|---|---|---|---|---|---|
| Leitura completa dos 38 cenários principais (cega) | 00:35 → 01:07 | 32 min | 38 | 37/38 | 0 |
| Análise profunda (3 leituras + voto) em 4 casos difíceis | 01:11 → 01:35 | 24 min | 4 | 4/4 | 0 |
| Validação cega — 8 cenários com redação inédita | 01:14 → 01:34 | 20 min | 8 | 7/8 | 0 |
| Validação independente — 10 casos de outro autor | 06:56 → 07:18 | 22 min | 10 | 7/10 | **2** (corrigidos depois) |
| Lote ATPV-e — 14 casos (vendendo ou comprando, todos os tipos de empresa) | 09:43 → 10:00 | 15 min | 14 | 14/14 | 0 |
| Consulta por CPF — 15 casos (pessoa física e procuração) | 12:00 → 12:10 | 10 min | 15 | 15/15 | 0 |

A análise profunda e a validação cega rodaram ao mesmo tempo, dividindo o servidor da IA. Houve também uma primeira
tentativa da validação independente às 06:34, interrompida para ligar a trava térmica depois que a GPU chegou a 85 °C.

Um caso leva, com a IA local, de 45 s a 2 min por documento novo (cada documento passa por 1–2 tarefas de leitura).
Documentos já lidos saem do cache na hora: reprocessar com outra política ou simular outros assinantes é instantâneo.

Resultados completos, caso a caso e com as lições de cada rodada: [`RESULTADOS.md`](RESULTADOS.md).

## 6. Como reproduzir

```bash
uv sync                                   # dependências Python
uv run pytest -q                          # 253 testes (sem IA, segundos)
uv run outorga avaliar oraculo            # motor com leitura perfeita (38 cenários)
uv run python -m outorga.avaliacao oraculo --conjunto pf     # consulta por CPF
uv run python -m outorga.avaliacao llm --conjunto todos      # com a IA configurada (usa o cache .cache/leituras)
```

Com o cache versionado, a rodada `llm` reproduz as leituras do Qwen sem GPU. Para medir a IA do zero, aponte
`OUTORGA_CACHE` para uma pasta vazia e ligue o servidor de IA (veja [`IA.md`](IA.md)).

## 7. Medição só em CPU (sem GPU)

Em 17/10/2026, às 12:36, o mesmo modelo dos testes (Qwen3.8-27B, UD-Q2_K_XL) foi iniciado no llama.cpp **só no
processador**: GPU escondida com `CUDA_VISIBLE_DEVICES=""`, `-ngl 0`, 6 threads, contexto de 8K. Ele leu o contrato
social do cenário C01 (1.073 palavras) com o mesmo pipeline dos testes.

| Medida | Resultado |
|---|---|
| Leitura do prompt (documento + instruções, 3.432 tokens) | **405 s** (6min45s), a **8,5 tokens/s** |
| Temperatura da CPU (Ryzen 5 4600G, cooler original) | subiu de 57 °C para **93 °C** (o limite do processador é 95 °C) |
| Resultado | medição **interrompida** antes da geração da resposta, para não esquentar a máquina |

Na GPU, a mesma leitura do prompt leva poucos segundos. Só a etapa de leitura já mostra que, neste desktop, a CPU é
cerca de 50 vezes mais lenta que a GPU para esse modelo; um documento completo levaria de 20 a 30 minutos.

Conclusão:

- **Sem GPU, num desktop comum, não é viável para atendimento.** A quantização de 2 bits usada na GPU é especialmente
  lenta na CPU.
- Para rodar sem GPU, use um **servidor com CPU de muitos núcleos e memória rápida** (DDR5 em vários canais), uma
  quantização própria para CPU (Q4_K_M ou Q4_0) e, de preferência, um **modelo menor revalidado** com os lotes de teste
  ([`MODELOS.md`](MODELOS.md)).
- Ou use uma **IA por chave de API** ([`IA.md`](IA.md)).

## 8. Comparação de modelos (17/10/2026, à tarde)

Depois de pronto o protótipo, a mesma avaliação foi repetida com outras IAs, para responder qual lê melhor, mais rápido e
mais barato. Os resultados e a recomendação estão em [`MODELOS.md`](MODELOS.md). Aqui fica o registro de como e quando.

### Modelos Claude, pela API da Anthropic

- **Chave:** da conta do Daniel, com os créditos mensais do plano Max 20x (US$ 200 por mês, válidos para a API).
- **Script:** [`scripts/comparar_claude.py`](../scripts/comparar_claude.py). Cada configuração (modelo e esforço) roda
  num processo próprio, com cache de leituras próprio, 8 leituras ao mesmo tempo e o fallback do servidor desligado.
- **Custo:** calculado pelos tokens que a API informa em cada resposta e pela tabela oficial de preços.
- **Reavaliação sem custo:** `scripts/comparar_claude.py --reavaliar` roda de novo a avaliação com as leituras guardadas,
  sem chamar a API, para medir o efeito de uma mudança no motor.

| Rodada (17/10) | Início → fim | Configurações | Custo |
|---|---|---|---|
| 1ª: todas as configurações (3 modelos atuais × 5 esforços + 3 da geração anterior) | 13:23 → 14:20 | 18 | US$ 85,71 |
| 2ª: segunda rodada das candidatas (Haiku e Sonnet 5.5 em low/medium/high, Opus 5.5 em low/medium, Sonnet 5.5 xhigh) | 13:57 → 14:15 | 9 | US$ 17,97 |
| 3ª: terceira rodada de Haiku 5.5 medium, Sonnet 5.5 medium e high | 14:08 → 14:18 | 3 | US$ 4,39 |

Antes, às 13:20, um piloto de 4 casos em três modelos (US$ 0,88) conferiu o caminho completo e o custo por chamada.
Com 8 leituras ao mesmo tempo, cada configuração leu os 85 casos em 2 a 5 minutos; em `max`, de 22 a 27 minutos (o
Haiku 5.5 em `max` levou 44 minutos, porque algumas leituras estouraram o limite de 64 mil tokens e foram repetidas).
**Gasto total: US$ 108,94**, todo coberto pelo crédito mensal do plano Max 20x.

### Modelos locais, na RTX 3060

- **Script:** [`scripts/comparar_modelos.py`](../scripts/comparar_modelos.py). Ele sobe um `llama-server` só para o teste
  (porta 8092, `--reasoning off`), roda os 33 casos da triagem (cegos, independentes e consulta por CPF) e apaga o modelo
  baixado no fim.
- **Trava térmica:** GPU em 70/62 °C e CPU em 85/75 °C (pausa / retoma). A trava de CPU foi criada nesta tarde, depois
  que um modelo MoE com metade dos especialistas na RAM levou o processador a 87 °C.
- **Vigia extra:** desligaria o servidor do teste se a GPU passasse de 88 °C ou a CPU de 90 °C por duas leituras
  seguidas. Não chegou a disparar, mas a GPU chegou a 87 °C dentro de leituras longas (detalhes em
  [`MODELOS.md`](MODELOS.md#temperatura)).

| Modelo | Início → fim | Duração | Leitura / pausas térmicas | Resultado |
|---|---|---|---|---|
| Qwen3.6-35B-A3B (MoE, metade na CPU) | 13:35 → 13:47 | 12 min | — | interrompido no 1º caso: CPU a 87 °C |
| Gemma 4 12B | 13:55 → 15:25 | 90 min | 35 / 55 min | 24 de 33 vereditos (29 com o motor corrigido) |
| Qwen3.5-9B | 15:26 → 17:01 | 95 min | 40 / 50 min | 24 de 33 vereditos; reiniciado às 16:22 com a trava mais fria |
| Ministral 3 14B e Granite 4.2 8B | — | — | — | não testados, para não esquentar mais a GPU |

Ao terminar, os modelos baixados foram apagados e a GPU voltou ao repouso (1,7 GB de VRAM ocupados pelo serviço de
transcrição e pelo desktop). Os modelos Qwen3.8-27B que já estavam na máquina ficaram onde estavam.

