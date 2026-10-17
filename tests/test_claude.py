"""Provedor Claude: workspace, esforço por modelo, fallback, uso de tokens e variante na chave do cache."""

import json

import pytest

anthropic = pytest.importorskip("anthropic")
httpx = pytest.importorskip("httpx2")  # o SDK da Anthropic usa o httpx2, não o httpx

from outorga.llm_claude import Claude  # noqa: E402


def _sse(texto: str, modelo: str) -> bytes:
    eventos = [
        ("message_start", {"type": "message_start", "message": {
            "id": "msg_1", "type": "message", "role": "assistant", "model": modelo, "content": [], "stop_reason": None,
            "stop_sequence": None, "usage": {"input_tokens": 120, "output_tokens": 1, "cache_read_input_tokens": 900,
                                             "cache_creation_input_tokens": 3000}}}),
        ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
        ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": texto}}),
        ("content_block_stop", {"type": "content_block_stop", "index": 0}),
        ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                           "usage": {"output_tokens": 450}}),
        ("message_stop", {"type": "message_stop"}),
    ]
    return "".join(f"event: {e}\ndata: {json.dumps(d)}\n\n" for e, d in eventos).encode()


@pytest.fixture
def pedidos(monkeypatch):
    vistos = []

    def handler(req: httpx.Request) -> httpx.Response:
        corpo = json.loads(req.content)
        vistos.append((req.headers, corpo))
        return httpx.Response(200, content=_sse('{"ok": true}', corpo["model"]),
                              headers={"content-type": "text/event-stream", "request-id": "req_teste"})

    original = anthropic.Anthropic
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: original(
        api_key="sk-ant-usr-teste", http_client=httpx.Client(transport=httpx.MockTransport(handler)), **kw))
    for v in ("ANTHROPIC_WORKSPACE_ID", "OUTORGA_CLAUDE_FALLBACK", "OUTORGA_CLAUDE_ESFORCO", "OUTORGA_CLAUDE_MODELO"):
        monkeypatch.delenv(v, raising=False)
    return vistos


def test_workspace_esforco_e_uso(pedidos, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_WORKSPACE_ID", "wrkspc_teste")
    p = Claude("claude-sonnet-5-5", "low")
    dados, meta = p.json("sistema", "documento", "tarefa", {"type": "object"}, "teste")
    cab, corpo = pedidos[0]
    assert dados == {"ok": True}
    assert cab["anthropic-workspace-id"] == "wrkspc_teste"
    assert corpo["output_config"]["effort"] == "low" and corpo["output_config"]["format"]["type"] == "json_schema"
    assert corpo["fallbacks"] == "default" and "server-side-fallback" in cab["anthropic-beta"]
    assert corpo["stream"] is True
    assert meta["tokens_entrada"] == 120 and meta["tokens_saida"] == 450
    assert meta["tokens_cache"] == 900 and meta["tokens_cache_escrita"] == 3000
    assert meta["esforco"] == "low" and meta["request_id"] == "req_teste"
    assert p.variante == "esforco=low"


def test_modelo_sem_esforco_e_sem_fallback(pedidos, monkeypatch):
    monkeypatch.setenv("OUTORGA_CLAUDE_FALLBACK", "0")
    p = Claude("claude-haiku-4-5", "high")
    p.json("sistema", "documento", "tarefa", {"type": "object"}, "teste")
    cab, corpo = pedidos[0]
    assert "effort" not in corpo["output_config"] and "fallbacks" not in corpo
    assert "anthropic-workspace-id" not in cab
    assert p.esforco is None and p.variante is None


def test_esforco_alto_tem_mais_espaco_para_pensar(pedidos):
    Claude("claude-opus-5-5", "xhigh").json("s", "d", "t", {"type": "object"}, "teste")
    Claude("claude-opus-5-5", "padrao").json("s", "d", "t", {"type": "object"}, "teste")
    (_, xhigh), (_, padrao) = pedidos
    assert xhigh["max_tokens"] == 64000 and xhigh["output_config"]["effort"] == "xhigh"
    assert padrao["max_tokens"] == 32000 and "effort" not in padrao["output_config"]


def test_esforco_invalido():
    with pytest.raises(Exception, match="esforço desconhecido"):
        Claude("claude-opus-5-5", "altissimo")
