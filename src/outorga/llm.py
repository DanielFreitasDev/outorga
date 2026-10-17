"""Provedores de LLM para a leitura estruturada (JSON Schema garantido).

- `llamacpp` (padrão): servidor local OpenAI-compatível (Qwen no llama.cpp). Os documentos não saem
  da máquina — relevante para LGPD (contratos têm CPF, RG, endereço). A gramática do llama.cpp
  garante JSON válido no schema.
- `anthropic`: Claude via SDK oficial (ver `llm_claude.py`), opcional, para quem quiser a nuvem.

Interface única: `provedor.json(sistema, documento, tarefa, schema, nome) -> (dict, meta)`.
O texto do documento vem ANTES da tarefa, para que várias extrações do mesmo documento reaproveitem
o prefixo em cache (llama.cpp: cache de prompt; Claude: prompt caching).
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Any, Protocol

import httpx


class ErroLLM(RuntimeError):
    pass


class Provedor(Protocol):
    nome: str
    modelo: str

    def json(self, sistema: str, documento: str, tarefa: str, schema: dict, nome_schema: str,
             temperatura: float = 0.2, max_tokens: int = 8192) -> tuple[dict, dict]: ...


def temperatura_gpu() -> int | None:
    """Temperatura da GPU NVIDIA (°C) ou None se não houver nvidia-smi."""
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=5)
        return int(r.stdout.strip().splitlines()[0])
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return None


def guarda_termica() -> float:
    """Protege a máquina em uso contínuo: se a GPU estiver acima de OUTORGA_TEMP_MAX (padrão 76 °C), espera esfriar
    até OUTORGA_TEMP_RETOMAR (padrão 68 °C) antes da próxima leitura. Devolve os segundos esperados."""
    tmax = int(os.environ.get("OUTORGA_TEMP_MAX", "76"))
    tret = int(os.environ.get("OUTORGA_TEMP_RETOMAR", "68"))
    t = temperatura_gpu()
    if t is None or t < tmax:
        return 0.0
    inicio = time.time()
    while t is not None and t > tret and time.time() - inicio < 900:
        time.sleep(10)
        t = temperatura_gpu()
    return round(time.time() - inicio, 1)


class LlamaCpp:
    """Servidor OpenAI-compatível (llama.cpp, vLLM, LM Studio...)."""

    def __init__(self, base_url: str | None = None, modelo: str | None = None, pensar: bool = False, timeout: float = 900):
        self.base_url = (base_url or os.environ.get("OUTORGA_LLM_URL", "http://127.0.0.1:8089/v1")).rstrip("/")
        self.modelo = modelo or os.environ.get("OUTORGA_LLM_MODELO", "qwen3.8-27b")
        self.nome = "llamacpp"
        self.pensar = pensar
        self.cliente = httpx.Client(timeout=timeout)

    def disponivel(self) -> bool:
        try:
            return self.cliente.get(self.base_url.rsplit("/v1", 1)[0] + "/health", timeout=3).status_code == 200
        except httpx.HTTPError:
            return False

    def json(self, sistema: str, documento: str, tarefa: str, schema: dict, nome_schema: str,
             temperatura: float = 0.2, max_tokens: int = 8192) -> tuple[dict, dict]:
        corpo: dict[str, Any] = {
            "model": self.modelo,
            "messages": [{"role": "system", "content": sistema},
                         {"role": "user", "content": f"DOCUMENTO:\n<<<\n{documento}\n>>>\n\nTAREFA:\n{tarefa}"}],
            "temperature": temperatura,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_schema", "json_schema": {"name": nome_schema, "schema": schema, "strict": True}},
            "cache_prompt": True,
        }
        if not self.pensar:
            corpo["chat_template_kwargs"] = {"enable_thinking": False}
        ultimo_erro = None
        espera = guarda_termica() if self.base_url.startswith(("http://127.0.0.1", "http://localhost")) else 0.0
        for tentativa in range(3):
            t = time.time()
            try:
                r = self.cliente.post(f"{self.base_url}/chat/completions", json=corpo)
                r.raise_for_status()
                j = r.json()
                msg = j["choices"][0]["message"]
                conteudo = msg.get("content") or ""
                dados = json.loads(conteudo)
                uso = j.get("usage", {})
                return dados, {"provedor": self.nome, "modelo": self.modelo, "segundos": round(time.time() - t, 2),
                               "tokens_entrada": uso.get("prompt_tokens"), "tokens_saida": uso.get("completion_tokens"),
                               "tokens_cache": (uso.get("prompt_tokens_details") or {}).get("cached_tokens"),
                               "temperatura": temperatura, "tentativa": tentativa + 1, "espera_termica_s": espera,
                               "finish_reason": j["choices"][0].get("finish_reason")}
            except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
                ultimo_erro = e
                corpo["temperature"] = 0.0
                corpo["max_tokens"] = int(max_tokens * 1.5)
        raise ErroLLM(f"{self.nome}: falhou após 3 tentativas: {ultimo_erro}")


def provedor_padrao(nome: str | None = None) -> Provedor:
    nome = (nome or os.environ.get("OUTORGA_LLM", "llamacpp")).lower()
    if nome in ("anthropic", "claude"):
        from .llm_claude import Claude

        return Claude()
    if nome in ("llamacpp", "qwen", "local", "openai"):
        return LlamaCpp()
    raise ValueError(f"provedor desconhecido: {nome}")
