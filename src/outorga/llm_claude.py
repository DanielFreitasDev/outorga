"""Provedor Claude (SDK oficial `anthropic`) — opcional.

Ativar:  uv sync --extra claude   e   OUTORGA_LLM=anthropic  (credencial: ANTHROPIC_API_KEY ou `ant auth login`)

- modelo padrão `claude-sonnet-5-5` com esforço `medium`, o melhor equilíbrio na comparação de docs/MODELOS.md
  (OUTORGA_CLAUDE_MODELO e OUTORGA_CLAUDE_ESFORCO: low | medium | high | xhigh | max, ou `padrao` para o padrão de cada
  modelo). O esforço entra na chave do cache de leituras, então trocar o esforço não reaproveita leituras feitas com outro;
- chave ligada ao usuário (`sk-ant-usr-…`) precisa do workspace: ANTHROPIC_WORKSPACE_ID=wrkspc_… vira o cabeçalho
  `anthropic-workspace-id` (o workspace "Default" antigo não tem ID: crie um workspace com nome);
- saída estruturada por `output_config.format` (JSON Schema) — o primeiro bloco de texto é JSON válido;
- prompt caching: instruções (system) e o texto do documento ficam em cache; só a tarefa muda;
- streaming com `get_final_message()`: em esforço alto o pensamento é longo, e sem streaming o SDK recusa pedidos que
  podem passar de 10 minutos;
- recusa do classificador de segurança: `stop_reason == "refusal"` é tratado antes de ler o conteúdo, e o fallback no
  servidor (`fallbacks: "default"`) fica ligado por padrão. OUTORGA_CLAUDE_FALLBACK=0 desliga (a comparação de modelos
  desliga, para medir só o modelo pedido).
"""

from __future__ import annotations

import json
import os
import time

from .llm import ErroLLM

ESFORCOS = ("low", "medium", "high", "xhigh", "max")
SEM_ESFORCO = ("claude-haiku-4-5",)  # modelos sem o parâmetro `effort`


class Claude:
    def __init__(self, modelo: str | None = None, esforco: str | None = None):
        import anthropic  # dependência opcional (extra "claude")

        self._anthropic = anthropic
        ws = os.environ.get("ANTHROPIC_WORKSPACE_ID")
        self.cliente = anthropic.Anthropic(max_retries=int(os.environ.get("OUTORGA_CLAUDE_TENTATIVAS", "4")),
                                           default_headers={"anthropic-workspace-id": ws} if ws else None)
        self.modelo = modelo or os.environ.get("OUTORGA_CLAUDE_MODELO", "claude-sonnet-5-5")
        esf = (esforco or os.environ.get("OUTORGA_CLAUDE_ESFORCO", "medium")).strip().lower()
        if esf not in ESFORCOS and esf not in ("padrao", "padrão", "default", ""):
            raise ErroLLM(f"esforço desconhecido: {esf!r} (use {', '.join(ESFORCOS)} ou padrao)")
        self.esforco = esf if esf in ESFORCOS and not self.modelo.startswith(SEM_ESFORCO) else None
        self.variante = f"esforco={self.esforco}" if self.esforco else None  # entra na chave do cache de leituras
        self.fallback = os.environ.get("OUTORGA_CLAUDE_FALLBACK", "1") != "0"
        self.nome = "anthropic"

    def json(self, sistema: str, documento: str, tarefa: str, schema: dict, nome_schema: str,
             temperatura: float = 0.2, max_tokens: int = 32000) -> tuple[dict, dict]:
        a = self._anthropic
        t = time.time()
        saida = {"format": {"type": "json_schema", "schema": schema}}
        if self.esforco:
            saida["effort"] = self.esforco
        params = dict(
            model=self.modelo,
            # o pensamento conta no max_tokens; em xhigh/max ele pode ser longo
            max_tokens=max(max_tokens, 64000) if self.esforco in ("xhigh", "max") else max_tokens,
            system=[{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": [
                {"type": "text", "text": f"DOCUMENTO:\n<<<\n{documento}\n>>>", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": f"TAREFA:\n{tarefa}"},
            ]}],
            output_config=saida,
        )
        if self.fallback:
            params.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        try:
            with self.cliente.beta.messages.stream(**params) as fluxo:
                resp = fluxo.get_final_message()
                request_id = fluxo.request_id
        except a.RateLimitError as e:
            raise ErroLLM(f"Claude: limite de taxa (retry-after={e.response.headers.get('retry-after')})") from e
        except a.AuthenticationError as e:
            raise ErroLLM(f"Claude: chave de API recusada: {e.message}") from e
        except a.BadRequestError as e:
            raise ErroLLM(f"Claude: requisição inválida: {e.message}") from e
        except a.APIStatusError as e:
            raise ErroLLM(f"Claude: erro {e.status_code}: {e.message}") from e
        except a.APIConnectionError as e:
            raise ErroLLM("Claude: sem conexão com a API") from e
        if resp.stop_reason == "refusal":
            cat = getattr(resp.stop_details, "category", None) if resp.stop_details else None
            raise ErroLLM(f"Claude recusou a leitura (categoria: {cat}); use o provedor local para este documento")
        if resp.stop_reason == "max_tokens":
            raise ErroLLM("Claude: resposta cortada por max_tokens")
        texto = next((b.text for b in resp.content if b.type == "text"), None)
        if not texto:
            raise ErroLLM("Claude: resposta sem bloco de texto")
        u = resp.usage
        return json.loads(texto), {
            "provedor": self.nome, "modelo": resp.model, "modelo_pedido": self.modelo, "esforco": self.esforco,
            "segundos": round(time.time() - t, 2), "tokens_entrada": u.input_tokens, "tokens_saida": u.output_tokens,
            "tokens_cache": u.cache_read_input_tokens, "tokens_cache_escrita": u.cache_creation_input_tokens,
            "request_id": request_id,
        }
