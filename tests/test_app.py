import pytest

from app import app
from llm import LLMClient


def make_client():
    return app.test_client()


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_index_renders():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI Assistant" in response.data


def test_chat_returns_reply_in_mock_mode():
    client = app.test_client()
    res = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Hello"}]})
    assert res.status_code == 200
    assert "Hello" in res.get_json()["reply"]


def test_chat_rejects_empty_messages():
    res = app.test_client().post("/api/chat", json={"messages": []})
    assert res.status_code == 400


def test_chat_rejects_bad_role():
    res = app.test_client().post(
        "/api/chat", json={"messages": [{"role": "wizard", "content": "hi"}]}
    )
    assert res.status_code == 400


def test_llm_client_mock_mode_without_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LLMClient(api_key=None)
    assert client.mock_mode is True
    assert "mock mode" in client.chat([{"role": "user", "content": "ping"}])


def test_llm_client_not_mock_with_key():
    client = LLMClient(api_key="test-key")
    assert client.mock_mode is False