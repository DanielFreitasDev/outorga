"""Provedores de LLM para a leitura estruturada (JSON Schema garantido).

- `llamacpp` (padrão): servidor local OpenAI-compatível (Qwen no llama.cpp). Os documentos não saem
  da máquina — relevante para LGPD (contratos têm CPF, RG, endereço). A gramática do llama.cpp
  garante JSON válido no schema.
- `anthropic`: Claude via SDK oficial (ver `llm_claude.py`), por chave de API.
- `openai`, `gemini`, `groq`, `openrouter`, `deepseek`, `mistral`, `together`, `xai`: qualquer serviço com API
  compatível com a da OpenAI, por chave de API; `ollama` e `lmstudio`: servidores locais; `compativel`: qualquer outro
  endereço (`OUTORGA_LLM_URL` + `OUTORGA_LLM_CHAVE`).
- `nenhum`: sem IA (demonstração) — só lê documentos que já estão no cache de leituras.

As chaves podem vir do ambiente ou de um arquivo `.env` na raiz do projeto (nunca versionado).

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

from pathlib import Path

import httpx


class ErroLLM(RuntimeError):
    pass


def carregar_env(caminho: Path | None = None) -> None:
    """Lê `CHAVE=valor` de um `.env` na raiz do projeto, sem sobrescrever o que já está no ambiente."""
    arq = caminho or Path(__file__).resolve().parents[2] / ".env"
    if not arq.exists():
        return
    for linha in arq.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        k, v = linha.split("=", 1)
        k = k.strip().removeprefix("export ").strip()
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))


carregar_env()


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


def temperatura_cpu() -> int | None:
    """Temperatura do processador (°C), lida do sensor do kernel (k10temp na AMD, coretemp na Intel), ou None."""
    for h in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        try:
            if (h / "name").read_text().strip() in ("k10temp", "zenpower", "coretemp"):
                return int((h / "temp1_input").read_text()) // 1000
        except (OSError, ValueError):
            continue
    return None


def guarda_termica() -> float:
    """Protege a máquina em uso contínuo. Se a GPU passar de OUTORGA_TEMP_MAX (padrão 76 °C) ou a CPU passar de
    OUTORGA_TEMP_CPU_MAX (padrão 85 °C; importa quando parte do modelo roda na CPU), espera a GPU voltar a
    OUTORGA_TEMP_RETOMAR (padrão 68 °C) e a CPU a OUTORGA_TEMP_CPU_RETOMAR (padrão 75 °C) antes da próxima leitura.
    Devolve os segundos esperados."""
    gmax, gret = int(os.environ.get("OUTORGA_TEMP_MAX", "76")), int(os.environ.get("OUTORGA_TEMP_RETOMAR", "68"))
    cmax, cret = int(os.environ.get("OUTORGA_TEMP_CPU_MAX", "85")), int(os.environ.get("OUTORGA_TEMP_CPU_RETOMAR", "75"))
    g, c = temperatura_gpu(), temperatura_cpu()
    if (g is None or g < gmax) and (c is None or c < cmax):
        return 0.0
    inicio = time.time()
    while ((g is not None and g > gret) or (c is not None and c > cret)) and time.time() - inicio < 900:
        time.sleep(10)
        g, c = temperatura_gpu(), temperatura_cpu()
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


# serviço → (URL base da API compatível com a da OpenAI, variável de ambiente da chave)
PRESETS: dict[str, tuple[str | None, str | None]] = {
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "deepseek": ("https://api.deepseek.com/v1", "DEEPSEEK_API_KEY"),
    "mistral": ("https://api.mistral.ai/v1", "MISTRAL_API_KEY"),
    "together": ("https://api.together.xyz/v1", "TOGETHER_API_KEY"),
    "xai": ("https://api.x.ai/v1", "XAI_API_KEY"),
    "ollama": ("http://127.0.0.1:11434/v1", None),
    "lmstudio": ("http://127.0.0.1:1234/v1", None),
    "compativel": (None, "OUTORGA_LLM_CHAVE"),
}
NOMES = {"openai": "OpenAI", "gemini": "Google Gemini", "groq": "Groq", "openrouter": "OpenRouter", "deepseek": "DeepSeek",
         "mistral": "Mistral", "together": "Together AI", "xai": "xAI", "ollama": "Ollama (local)",
         "lmstudio": "LM Studio (local)", "compativel": "API compatível", "anthropic": "Anthropic (Claude)",
         "llamacpp": "IA local", "nenhum": "sem IA"}


def _extrair_json(texto: str) -> dict:
    """JSON da resposta, tolerando cercas de código e texto em volta (provedores sem saída estruturada)."""
    texto = texto.strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        i, f = texto.find("{"), texto.rfind("}")
        if i >= 0 and f > i:
            return json.loads(texto[i:f + 1])
        raise


class OpenAICompativel:
    """Qualquer API compatível com a da OpenAI (`/chat/completions`), com ou sem chave.

    Pede saída estruturada (`response_format: json_schema`, strict). Se o serviço recusar um parâmetro, aprende na
    hora: troca `max_tokens` por `max_completion_tokens`, tira `temperature` (modelos de raciocínio) ou cai para
    `json_object` com o schema no prompt. A resposta é sempre validada depois pelos modelos Pydantic.
    """

    def __init__(self, servico: str = "compativel", base_url: str | None = None, chave: str | None = None,
                 modelo: str | None = None, timeout: float = 600):
        url_padrao, var_chave = PRESETS[servico]
        self.nome = servico
        self.base_url = (base_url or os.environ.get("OUTORGA_LLM_URL") or url_padrao or "").rstrip("/")
        if not self.base_url:
            raise ValueError("defina OUTORGA_LLM_URL com o endereço da API (ex.: https://servico/v1)")
        self.chave = chave or os.environ.get("OUTORGA_LLM_CHAVE") or (os.environ.get(var_chave) if var_chave else None)
        self.modelo = modelo or os.environ.get("OUTORGA_LLM_MODELO") or ""
        if not self.modelo:
            raise ValueError(f"defina OUTORGA_LLM_MODELO com o nome do modelo no serviço '{servico}'")
        self.local = self.base_url.startswith(("http://127.0.0.1", "http://localhost"))
        self.cliente = httpx.Client(timeout=timeout)
        self._recusados: set[str] = set()

    def disponivel(self) -> bool:
        if not self.local:
            return bool(self.chave)
        try:
            return self.cliente.get(f"{self.base_url}/models", timeout=3).status_code < 500
        except httpx.HTTPError:
            return False

    def _corpo(self, msgs: list[dict], schema: dict, nome_schema: str, temperatura: float, max_tokens: int) -> dict:
        corpo: dict[str, Any] = {"model": self.modelo, "messages": msgs}
        if "temperature" not in self._recusados:
            corpo["temperature"] = temperatura
        corpo["max_completion_tokens" if "max_tokens" in self._recusados else "max_tokens"] = max_tokens
        if "json_schema" in self._recusados:
            corpo["response_format"] = {"type": "json_object"}
            corpo["messages"] = msgs[:-1] + [{"role": "user", "content": msgs[-1]["content"]
                                              + "\n\nResponda SOMENTE com um objeto JSON que obedeça a este JSON Schema:\n"
                                              + json.dumps(schema, ensure_ascii=False)}]
        else:
            corpo["response_format"] = {"type": "json_schema",
                                        "json_schema": {"name": nome_schema, "schema": schema, "strict": True}}
        return corpo

    def json(self, sistema: str, documento: str, tarefa: str, schema: dict, nome_schema: str,
             temperatura: float = 0.2, max_tokens: int = 8192) -> tuple[dict, dict]:
        cab = {"Authorization": f"Bearer {self.chave}"} if self.chave else {}
        msgs = [{"role": "system", "content": sistema},
                {"role": "user", "content": f"DOCUMENTO:\n<<<\n{documento}\n>>>\n\nTAREFA:\n{tarefa}"}]
        ultimo: Exception | None = None
        for tentativa in range(5):
            t = time.time()
            try:
                r = self.cliente.post(f"{self.base_url}/chat/completions", headers=cab,
                                      json=self._corpo(msgs, schema, nome_schema, temperatura, max_tokens))
                if r.status_code == 400:
                    erro = r.text.lower()
                    for param, marcas in (("max_tokens", ("max_tokens", "max_completion_tokens")),
                                          ("temperature", ("temperature",)),
                                          ("json_schema", ("json_schema", "response_format", "structured", "schema"))):
                        if param not in self._recusados and any(m in erro for m in marcas):
                            self._recusados.add(param)
                            break
                    else:
                        r.raise_for_status()
                    continue
                if r.status_code in (401, 403):
                    raise ErroLLM(f"{NOMES.get(self.nome, self.nome)}: chave de API recusada ({r.status_code})")
                if r.status_code == 429 or r.status_code >= 500:
                    time.sleep(min(30, 4 * (tentativa + 1)))
                    ultimo = httpx.HTTPStatusError(f"HTTP {r.status_code}", request=r.request, response=r)
                    continue
                r.raise_for_status()
                j = r.json()
                dados = _extrair_json(j["choices"][0]["message"].get("content") or "")
                uso = j.get("usage") or {}
                return dados, {"provedor": self.nome, "modelo": self.modelo, "segundos": round(time.time() - t, 2),
                               "tokens_entrada": uso.get("prompt_tokens"), "tokens_saida": uso.get("completion_tokens"),
                               "temperatura": temperatura, "tentativa": tentativa + 1,
                               "finish_reason": j["choices"][0].get("finish_reason")}
            except ErroLLM:
                raise
            except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
                ultimo = e
        raise ErroLLM(f"{NOMES.get(self.nome, self.nome)}: falhou após 5 tentativas: {ultimo}")


class SemIA:
    """Modo demonstração: nenhuma IA ligada. Lê do cache as leituras feitas pela IA indicada em `OUTORGA_CACHE_DE`
    (padrão: a IA local dos testes), então os casos do corpus continuam funcionando; documento novo dá erro claro."""

    def __init__(self) -> None:
        de = os.environ.get("OUTORGA_CACHE_DE", "llamacpp:qwen3.8-27b")
        self.nome, _, self.modelo = de.partition(":")
        self.rotulo = "sem IA (demonstração)"

    def disponivel(self) -> bool:
        return False

    def json(self, *args: Any, **kwargs: Any) -> tuple[dict, dict]:
        raise ErroLLM("IA desligada nesta instalação (demonstração): só documentos do corpus de exemplo podem ser lidos. "
                      "Para ler documentos novos, ligue uma IA local ou uma chave de API (docs/IA.md).")


def provedor_padrao(nome: str | None = None) -> Provedor:
    """`OUTORGA_LLM`: llamacpp (padrão) | anthropic | openai | gemini | groq | openrouter | deepseek | mistral |
    together | xai | ollama | lmstudio | compativel | nenhum."""
    nome = (nome or os.environ.get("OUTORGA_LLM", "llamacpp")).lower()
    if nome in ("anthropic", "claude"):
        from .llm_claude import Claude

        return Claude()
    if nome in ("llamacpp", "qwen", "local"):
        return LlamaCpp()
    if nome in ("nenhum", "demonstracao", "demo", "off"):
        return SemIA()
    if nome in PRESETS:
        return OpenAICompativel(nome)
    raise ValueError(f"provedor desconhecido: {nome} (opções: llamacpp, anthropic, {', '.join(PRESETS)}, nenhum)")


def rotulo_ia(prov: Any) -> str:
    """Texto curto para a interface: 'IA local · qwen3.8-27b', 'OpenAI · <modelo>', 'sem IA (demonstração)'."""
    if isinstance(prov, SemIA):
        return prov.rotulo
    return f"{NOMES.get(prov.nome, prov.nome)} · {prov.modelo}"
