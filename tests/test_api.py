import os
from unittest.mock import patch, MagicMock

# Garantir chave de API para inicialização do módulo
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-12345")

from fastapi.testclient import TestClient
from src.application.dtos.response_dto import ResponseDTO
from src.interfaces.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_session_endpoint():
    response = client.post("/sessions")
    assert response.status_code == 201
    assert "session_id" in response.json()


def test_chat_endpoint_persists_messages_and_responds():
    fixed_response = ResponseDTO(
        content="Resposta de teste",
        session_id="session_test",
        is_from_cache=False,
        context_used=[],
        metadata={"model": "gpt-3.5-turbo"}
    )

    with patch("src.interfaces.api.main.chat_service.ask", return_value=fixed_response), \
         patch("src.interfaces.api.main.message_repo.add") as mocked_add, \
         patch("src.interfaces.api.main.message_repo.delete_old") as mocked_delete_old, \
         patch("src.interfaces.api.main.response_cache.get", return_value=None), \
         patch("src.interfaces.api.main.response_cache.set"):

        response = client.post("/chat", json={"query": "Olá mundo", "session_id": "session_test"})

        assert response.status_code == 200
        body = response.json()
        assert body["content"] == "Resposta de teste"
        assert body["session_id"] == "session_test"
        assert body["is_from_cache"] is False

        assert mocked_add.call_count == 2
        mocked_delete_old.assert_called_once()


def test_chat_endpoint_returns_cached_response():
    """When cache hits, the LLM is not called and messages are not persisted."""
    with patch("src.interfaces.api.main.response_cache.get", return_value="Resposta em cache"), \
         patch("src.interfaces.api.main.chat_service.ask") as mocked_ask, \
         patch("src.interfaces.api.main.message_repo.add") as mocked_add:

        response = client.post("/chat", json={"query": "Olá mundo", "session_id": "session_test"})

        assert response.status_code == 200
        body = response.json()
        assert body["content"] == "Resposta em cache"
        assert body["is_from_cache"] is True

        mocked_ask.assert_not_called()
        mocked_add.assert_not_called()


def test_chat_endpoint_rejects_empty_query():
    response = client.post("/chat", json={"query": "   "})
    assert response.status_code == 400
    assert "query não pode estar vazia" in response.json()["detail"]
