# Como ligar a IA

A IA só **lê** os documentos (extrai fatos com o trecho literal). Quem decide é o motor de regras. Por isso dá para
trocar de IA sem mudar as regras, e a demonstração, a consulta por CPF sem documentos, a simulação "e se…?" e o parecer
funcionam **sem IA nenhuma**.

A escolha é feita por variáveis de ambiente (no terminal ou num arquivo `.env` na raiz do projeto).

## 1. IA local (padrão), com servidor compatível com a API da OpenAI

```bash
export OUTORGA_LLM=llamacpp                          # padrão
export OUTORGA_LLM_URL=http://127.0.0.1:8089/v1      # endereço do servidor
export OUTORGA_LLM_MODELO=qwen3.8-27b                # nome do modelo no servidor
```

Testado com **llama.cpp** (`llama-server`) e o **Qwen3.8-27B** (GGUF UD-Q2_K_XL) numa RTX 3060 de 12 GB. Detalhes da
instalação e da máquina em [`COMO_FOI_TESTADO.md`](COMO_FOI_TESTADO.md). Exemplo de servidor:

```bash
llama-server -m Qwen3.8-27B-UD-Q2_K_XL.gguf -c 32768 -ngl 99 -fa on --host 127.0.0.1 --port 8089
```

O Outorga pede saída estruturada (`response_format` com JSON Schema) e desliga o "raciocínio" do modelo
(`enable_thinking: false`), o que deixa a leitura rápida e previsível.

## 2. Claude (Anthropic) por chave de API

```bash
uv sync --extra claude
export OUTORGA_LLM=anthropic
export ANTHROPIC_API_KEY=sk-ant-...                   # a chave fica só na sua máquina
```

Usa o SDK oficial da Anthropic, com saída estruturada e cache de prompt. Os documentos são enviados para a API da
Anthropic: avalie a LGPD antes de usar com documentos reais (o pedido do DETRAN-CE foi execução local).

## 3. Sem GPU

Ver a seção "Dá para rodar sem GPU" em [`COMO_FOI_TESTADO.md`](COMO_FOI_TESTADO.md).
