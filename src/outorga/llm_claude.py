"""Provedor Claude (SDK oficial `anthropic`) — opcional.

Ativar:  uv sync --extra claude   e   OUTORGA_LLM=anthropic  (credencial: ANTHROPIC_API_KEY ou `ant auth login`)

- modelo padrão `claude-opus-5` (OUTORGA_CLAUDE_MODELO para trocar), pensamento adaptativo (padrão do modelo)
  e esforço `high` (OUTORGA_CLAUDE_ESFORCO) — leitura jurídica é tarefa sensível a inteligência;
- saída estruturada por `output_config.format` (JSON Schema) — o primeiro bloco de texto é JSON válido;
- prompt caching: instruções (system) e o texto do documento ficam em cache; só a tarefa muda;
- recusa do classificador de segurança: `stop_reason == "refusal"` é tratado antes de ler o conteúdo, e
  o fallback no servidor (`fallbacks: "default"`) fica ligado por padrão.
"""

from __future__ import annotations

import json
import os
import time

from .llm import ErroLLM


class Claude:
    def __init__(self, modelo: str | None = None, esforco: str | None = None):
        import anthropic  # dependência opcional (extra "claude")

        self._anthropic = anthropic
        self.cliente = anthropic.Anthropic()
        self.modelo = modelo or os.environ.get("OUTORGA_CLAUDE_MODELO", "claude-opus-5")
        self.esforco = esforco or os.environ.get("OUTORGA_CLAUDE_ESFORCO", "high")
        self.nome = "anthropic"

    def json(self, sistema: str, documento: str, tarefa: str, schema: dict, nome_schema: str,
             temperatura: float = 0.2, max_tokens: int = 16000) -> tuple[dict, dict]:
        a = self._anthropic
        t = time.time()
        params = dict(
            model=self.modelo,
            max_tokens=max_tokens,
            betas=["server-side-fallback-2026-07-01"],
            system=[{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": [
                {"type": "text", "text": f"DOCUMENTO:\n<<<\n{documento}\n>>>", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": f"TAREFA:\n{tarefa}"},
            ]}],
            output_config={"effort": self.esforco, "format": {"type": "json_schema", "schema": schema}},
        )
        try:
            try:
                resp = self.cliente.beta.messages.create(**params, fallbacks="default")
            except TypeError:  # SDK sem o parâmetro tipado: envia no corpo
                resp = self.cliente.beta.messages.create(**params, extra_body={"fallbacks": "default"})
        except a.RateLimitError as e:
            raise ErroLLM(f"Claude: limite de taxa (retry-after={e.response.headers.get('retry-after')})") from e
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
            "provedor": self.nome, "modelo": resp.model, "segundos": round(time.time() - t, 2),
            "tokens_entrada": u.input_tokens, "tokens_saida": u.output_tokens,
            "tokens_cache": getattr(u, "cache_read_input_tokens", None), "request_id": resp._request_id,
        }
