"""Squad 3 tests. Do not edit."""
import pytest
from fastapi.testclient import TestClient

from hsi_rag import api, query

TOKEN = "test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
GOOD = {"answer": "A", "sources": [{"source": "faq.md", "chunk_id": "faq.md-0"}]}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("HSI_API_TOKEN", TOKEN)
    return TestClient(api.app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ask_without_token_is_401(client):
    assert client.post("/ask", json={"question": "hi"}).status_code == 401


def test_ask_with_wrong_token_is_401(client):
    r = client.post("/ask", json={"question": "hi"}, headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401


def test_ask_returns_the_answer(client, monkeypatch):
    monkeypatch.setattr(query, "answer", lambda q: GOOD)
    r = client.post("/ask", json={"question": "hi"}, headers=AUTH)
    assert r.status_code == 200
    assert r.json() == GOOD


def test_ask_passes_the_question_through(client, monkeypatch):
    seen = []
    monkeypatch.setattr(query, "answer", lambda q: seen.append(q) or GOOD)
    client.post("/ask", json={"question": "What is HSI?"}, headers=AUTH)
    assert seen == ["What is HSI?"]


def test_ask_rejects_missing_or_empty_question(client):
    assert client.post("/ask", json={}, headers=AUTH).status_code == 422
    assert client.post("/ask", json={"question": ""}, headers=AUTH).status_code == 422


def test_ask_returns_503_when_the_model_server_is_down(client, monkeypatch):
    def boom(q):
        raise ConnectionError("Ollama is down")

    monkeypatch.setattr(query, "answer", boom)
    r = client.post("/ask", json={"question": "hi"}, headers=AUTH)
    assert r.status_code == 503
