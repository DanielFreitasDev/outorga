# Como ligar a IA

A IA só **lê** os documentos e extrai os fatos, sempre com o trecho literal. Quem decide é o motor de regras jurídicas.
Por isso dá para trocar de IA sem mudar nenhuma regra.

Funcionam **sem IA nenhuma**: a demonstração, a consulta por CPF sem documentos, a simulação "e se…?", o reprocessamento
com outra política e o parecer. A IA só é necessária para **ler documentos novos**.

A escolha é feita por variáveis de ambiente, no terminal ou num arquivo `.env` na raiz do projeto. Copie
[`.env.example`](../.env.example) para `.env`. O `.env` **não é versionado**, então a chave fica só na sua máquina.

| `OUTORGA_LLM` | O que é | Precisa de |
|---|---|---|
| `llamacpp` (padrão) | IA **local** num servidor llama.cpp (ou qualquer servidor compatível com a API da OpenAI) | `OUTORGA_LLM_URL`, `OUTORGA_LLM_MODELO` |
| `ollama` · `lmstudio` | IA **local** no Ollama (`:11434`) ou no LM Studio (`:1234`) | `OUTORGA_LLM_MODELO` |
| `anthropic` | **Claude** (Anthropic), pelo SDK oficial | `ANTHROPIC_API_KEY` e `uv sync --extra claude` |
| `openai` | **OpenAI** | `OPENAI_API_KEY`, `OUTORGA_LLM_MODELO` |
| `gemini` | **Google Gemini** (endpoint compatível com a OpenAI) | `GEMINI_API_KEY`, `OUTORGA_LLM_MODELO` |
| `groq` · `openrouter` · `deepseek` · `mistral` · `together` · `xai` | serviços com API compatível com a da OpenAI | a chave do serviço (`GROQ_API_KEY`, `OPENROUTER_API_KEY`…) e `OUTORGA_LLM_MODELO` |
| `compativel` | **qualquer outro** endereço compatível com a OpenAI (Azure, servidor da empresa, vLLM remoto…) | `OUTORGA_LLM_URL`, `OUTORGA_LLM_CHAVE`, `OUTORGA_LLM_MODELO` |
| `nenhum` | sem IA (demonstração): só lê documentos que já estão no cache de leituras | — |

A tela mostra no canto superior qual IA está ativa (por exemplo, "IA local · qwen3.8-27b" ou "OpenAI · …").

## 1. IA local com GPU (o que foi testado)

```bash
# servidor (llama.cpp): modelo GGUF, contexto de 32K, tudo na GPU
llama-server -m Qwen3.8-27B-UD-Q2_K_XL.gguf -c 32768 -ngl 99 -fa on --jinja --host 127.0.0.1 --port 8089

# Outorga
OUTORGA_LLM=llamacpp OUTORGA_LLM_URL=http://127.0.0.1:8089/v1 OUTORGA_LLM_MODELO=qwen3.8-27b ./scripts/iniciar.sh
```

Nos testes foi usado o **llama.cpp** b11191 com o **Qwen3.8-27B** (GGUF UD-Q2_K_XL, 9,8 GB) numa RTX 3060 de 12 GB, a
~18 tokens/s. Detalhes da instalação em [`COMO_FOI_TESTADO.md`](COMO_FOI_TESTADO.md). O Outorga pede saída estruturada
(`response_format` com JSON Schema, que o llama.cpp transforma em gramática: a resposta é sempre um JSON válido) e
desliga o "raciocínio" do modelo (`enable_thinking: false`), o que deixa a leitura rápida e previsível.

Trava térmica: com a IA local, `OUTORGA_TEMP_MAX` e `OUTORGA_TEMP_RETOMAR` (padrão 76 °C e 68 °C) pausam a leitura entre
chamadas quando a GPU esquenta.

## 2. IA local sem GPU

Funciona: o llama.cpp roda no processador (`-ngl 0`). Fica lento num desktop comum porque a geração é limitada pela
velocidade da RAM. A medição nesta máquina e as alternativas (servidor com memória rápida, modelo menor revalidado, IA
por chave) estão em [`COMO_FOI_TESTADO.md`](COMO_FOI_TESTADO.md#dá-para-rodar-sem-gpu-só-no-processador).

## 3. IA por chave de API

### Claude (Anthropic)

```bash
uv sync --extra claude
# no .env:
OUTORGA_LLM=anthropic
ANTHROPIC_API_KEY=sk-ant-...
# opcionais: OUTORGA_CLAUDE_MODELO=claude-opus-5   OUTORGA_CLAUDE_ESFORCO=high
```

Usa o SDK oficial da Anthropic, com saída estruturada, cache de prompt (o documento entra uma vez e é reaproveitado nas
tarefas seguintes) e tratamento de recusa do classificador de segurança.

### OpenAI, Google Gemini, Groq, OpenRouter, DeepSeek, Mistral, Together, xAI

```bash
# no .env (exemplo com a OpenAI; troque pelo serviço e pela chave correspondentes):
OUTORGA_LLM=openai
OPENAI_API_KEY=sk-...
OUTORGA_LLM_MODELO=<nome do modelo, como aparece no painel do serviço>
```

O Outorga pede saída estruturada com JSON Schema e se adapta sozinho quando o serviço recusa um parâmetro:

- troca `max_tokens` por `max_completion_tokens`;
- tira a `temperature` (modelos de "raciocínio");
- usa `json_object` com o schema no prompt quando o serviço não aceita `json_schema`.

A resposta é sempre validada pelos modelos Pydantic antes de chegar ao motor.

### Qualquer outro serviço compatível

```bash
OUTORGA_LLM=compativel
OUTORGA_LLM_URL=https://meu-servidor.exemplo/v1
OUTORGA_LLM_CHAVE=...
OUTORGA_LLM_MODELO=...
```

## 4. Privacidade (LGPD)

Contratos sociais e procurações têm nome, CPF, RG e endereço. Com IA **local**, nada sai da máquina. Com IA **por chave
de API**, os documentos vão para o provedor escolhido: confira o contrato e a política de retenção do provedor e o
enquadramento na LGPD antes de usar documentos reais. O pedido do DETRAN-CE foi execução local.

## 5. Trocar de modelo exige revalidar

As regras não mudam, mas a **qualidade da leitura** muda de um modelo para outro. Antes de usar um modelo novo em
produção, rode a avaliação com ele e compare com os resultados de referência:

```bash
OUTORGA_CACHE=/tmp/cache-novo-modelo uv run python -m outorga.avaliacao llm --conjunto todos --saida avaliacoes/llm-<modelo>
```

O cache é separado por provedor e por modelo, então as leituras de modelos diferentes não se misturam. A comparação
dos modelos testados nesta máquina está em [`MODELOS.md`](MODELOS.md).
