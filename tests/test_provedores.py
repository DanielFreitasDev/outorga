"""Provedores de IA: chave de API (OpenAI e compatíveis), adaptação a parâmetros recusados, .env e modo sem IA."""

import json

import httpx
import pytest

from outorga import llm


def _resposta(conteudo: str) -> dict:
    return {"choices": [{"message": {"content": conteudo}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}}


def _provedor(handler, monkeypatch, servico="openai"):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-teste")
    monkeypatch.setenv("OUTORGA_LLM_MODELO", "modelo-x")
    monkeypatch.delenv("OUTORGA_LLM_URL", raising=False)
    p = llm.OpenAICompativel(servico)
    p.cliente = httpx.Client(transport=httpx.MockTransport(handler))
    return p


def test_envia_chave_e_pede_json_schema(monkeypatch):
    vistos = []

    def handler(req: httpx.Request) -> httpx.Response:
        vistos.append((req.url.host, req.headers.get("authorization"), json.loads(req.content)))
        return httpx.Response(200, json=_resposta('{"ok": true}'))

    p = _provedor(handler, monkeypatch)
    dados, meta = p.json("sistema", "documento", "tarefa", {"type": "object"}, "teste")
    host, auth, corpo = vistos[0]
    assert dados == {"ok": True} and host == "api.openai.com" and auth == "Bearer sk-teste"
    assert corpo["response_format"]["type"] == "json_schema" and corpo["model"] == "modelo-x"
    assert meta["provedor"] == "openai" and meta["tokens_saida"] == 5


def test_aprende_parametros_recusados(monkeypatch):
    """Modelo de raciocínio: recusa max_tokens e temperature; outro serviço recusa json_schema."""
    pedidos = []

    def handler(req: httpx.Request) -> httpx.Response:
        corpo = json.loads(req.content)
        pedidos.append(corpo)
        if "max_tokens" in corpo:
            return httpx.Response(400, json={"error": {"message": "Unsupported parameter: 'max_tokens'. Use 'max_completion_tokens'."}})
        if "temperature" in corpo:
            return httpx.Response(400, json={"error": {"message": "Unsupported value: 'temperature'"}})
        if corpo["response_format"]["type"] == "json_schema":
            return httpx.Response(400, json={"error": {"message": "response_format json_schema is not supported"}})
        return httpx.Response(200, json=_resposta('Aqui está:\n```json\n{"ok": 1}\n```'))

    p = _provedor(handler, monkeypatch)
    dados, _ = p.json("s", "d", "t", {"type": "object"}, "teste")
    assert dados == {"ok": 1}
    final = pedidos[-1]
    assert "max_completion_tokens" in final and "temperature" not in final and final["response_format"] == {"type": "json_object"}
    assert "JSON Schema" in final["messages"][-1]["content"]


def test_chave_recusada_da_erro_claro(monkeypatch):
    p = _provedor(lambda req: httpx.Response(401, json={"error": "bad key"}), monkeypatch)
    with pytest.raises(llm.ErroLLM, match="chave de API recusada"):
        p.json("s", "d", "t", {"type": "object"}, "teste")


def test_servicos_conhecidos_e_modelo_obrigatorio(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g-teste")
    monkeypatch.setenv("OUTORGA_LLM_MODELO", "gemini-x")
    monkeypatch.delenv("OUTORGA_LLM_URL", raising=False)
    g = llm.provedor_padrao("gemini")
    assert g.base_url.startswith("https://generativelanguage.googleapis.com") and g.chave == "g-teste" and g.disponivel()
    assert llm.rotulo_ia(g) == "Google Gemini · gemini-x"
    monkeypatch.delenv("OUTORGA_LLM_MODELO")
    with pytest.raises(ValueError, match="OUTORGA_LLM_MODELO"):
        llm.provedor_padrao("groq")
    with pytest.raises(ValueError, match="desconhecido"):
        llm.provedor_padrao("inexistente")


def test_env_nao_sobrescreve_o_ambiente(tmp_path, monkeypatch):
    arq = tmp_path / ".env"
    arq.write_text('# comentário\nexport OUTORGA_X_TESTE="do arquivo"\nOUTORGA_Y_TESTE=2\n', encoding="utf-8")
    monkeypatch.setenv("OUTORGA_Y_TESTE", "do ambiente")
    monkeypatch.delenv("OUTORGA_X_TESTE", raising=False)
    llm.carregar_env(arq)
    import os
    assert os.environ["OUTORGA_X_TESTE"] == "do arquivo" and os.environ["OUTORGA_Y_TESTE"] == "do ambiente"
    monkeypatch.delenv("OUTORGA_X_TESTE")


def test_sem_ia_le_o_cache_da_ia_local_e_recusa_documento_novo(monkeypatch):
    monkeypatch.delenv("OUTORGA_CACHE_DE", raising=False)
    p = llm.provedor_padrao("nenhum")
    assert (p.nome, p.modelo) == ("llamacpp", "qwen3.8-27b") and not p.disponivel()
    assert llm.rotulo_ia(p) == "sem IA (demonstração)"
    with pytest.raises(llm.ErroLLM, match="demonstração"):
        p.json("s", "d", "t", {}, "x")
