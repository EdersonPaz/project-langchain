"""
Tests for SemanticCache.

ChromaDB's Rust bindings may be blocked by system policy (Windows Application Control),
so all tests use mocks to test the logic of SemanticCache in isolation.
"""

import os
import hashlib
from unittest.mock import MagicMock, patch, call

import pytest

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-12345")


def _make_mock_model():
    """Returns a mock SentenceTransformer that returns deterministic embeddings."""
    mock = MagicMock()
    # encode returns a list-like that has .tolist() returning a fixed vector
    encode_result = MagicMock()
    encode_result.tolist.return_value = [[0.1, 0.2, 0.3]]
    mock.encode.return_value = encode_result
    return mock


def _make_mock_collection(distance=0.05):
    """Returns a mock ChromaDB collection with configurable similarity distance."""
    mock_col = MagicMock()
    mock_col.count.return_value = 1
    mock_col.query.return_value = {
        "distances": [[distance]],
        "metadatas": [[{"response": "Resposta mockada"}]],
    }
    return mock_col


def _make_mock_client(collection):
    """Returns a mock ChromaDB PersistentClient."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = collection
    mock_client.delete_collection = MagicMock()
    return mock_client


# ---------------------------------------------------------------------------
# Patch targets
# ---------------------------------------------------------------------------
PATCH_CHROMA = "src.infrastructure.external.semantic_cache.chromadb"
PATCH_ST = "src.infrastructure.external.semantic_cache.SentenceTransformer"
PATCH_DEPS = "src.infrastructure.external.semantic_cache._SEMANTIC_DEPS_AVAILABLE"


class TestSemanticCacheInit:
    def test_is_ready_when_deps_installed(self):
        mock_col = _make_mock_collection()
        mock_client = _make_mock_client(mock_col)
        mock_model = _make_mock_model()

        with patch(PATCH_DEPS, True), \
             patch(PATCH_CHROMA + ".PersistentClient", return_value=mock_client), \
             patch(PATCH_ST, return_value=mock_model):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake", threshold=0.90)

        assert cache.is_ready() is True

    def test_not_ready_when_deps_missing(self):
        with patch(PATCH_DEPS, False):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        assert cache.is_ready() is False

    def test_not_ready_when_init_raises(self):
        with patch(PATCH_DEPS, True), \
             patch(PATCH_CHROMA + ".PersistentClient", side_effect=OSError("DLL blocked")):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        assert cache.is_ready() is False

    def test_size_zero_when_not_ready(self):
        with patch(PATCH_DEPS, False):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        assert cache.size() == 0

    def test_get_returns_none_when_not_ready(self):
        with patch(PATCH_DEPS, False):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        assert cache.get("qualquer pergunta") is None


class TestSemanticCacheGet:
    def _build_ready_cache(self, distance=0.05):
        mock_col = _make_mock_collection(distance=distance)
        mock_col.count.return_value = 1
        mock_client = _make_mock_client(mock_col)
        mock_model = _make_mock_model()

        with patch(PATCH_DEPS, True), \
             patch(PATCH_CHROMA + ".PersistentClient", return_value=mock_client), \
             patch(PATCH_ST, return_value=mock_model):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake", threshold=0.90)

        # Inject mock references so they can be manipulated per-test
        cache._model = mock_model
        cache._collection = mock_col
        return cache

    def test_returns_cached_response_above_threshold(self):
        # distance=0.05 → similarity=0.95 ≥ 0.90 → hit
        cache = self._build_ready_cache(distance=0.05)
        result = cache.get("O que é LangChain?")
        assert result == "Resposta mockada"

    def test_returns_none_below_threshold(self):
        # distance=0.20 → similarity=0.80 < 0.90 → miss
        cache = self._build_ready_cache(distance=0.20)
        result = cache.get("O que é LangChain?")
        assert result is None

    def test_returns_none_on_empty_collection(self):
        cache = self._build_ready_cache()
        cache._collection.count.return_value = 0
        result = cache.get("qualquer coisa")
        assert result is None

    def test_returns_none_on_query_exception(self):
        cache = self._build_ready_cache()
        cache._collection.query.side_effect = Exception("DB error")
        result = cache.get("qualquer coisa")
        assert result is None


class TestSemanticCacheSet:
    def _build_ready_cache(self):
        mock_col = _make_mock_collection()
        mock_client = _make_mock_client(mock_col)
        mock_model = _make_mock_model()

        with patch(PATCH_DEPS, True), \
             patch(PATCH_CHROMA + ".PersistentClient", return_value=mock_client), \
             patch(PATCH_ST, return_value=mock_model):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake", threshold=0.90)

        cache._model = mock_model
        cache._collection = mock_col
        return cache

    def test_set_calls_upsert_with_correct_id(self):
        cache = self._build_ready_cache()
        query = "O que é RAG?"
        expected_id = hashlib.md5(query.encode()).hexdigest()

        cache.set(query, "Retrieval Augmented Generation.")

        cache._collection.upsert.assert_called_once()
        _, kwargs = cache._collection.upsert.call_args
        assert kwargs["ids"] == [expected_id]
        assert kwargs["metadatas"] == [{"response": "Retrieval Augmented Generation."}]

    def test_set_does_nothing_when_not_ready(self):
        with patch(PATCH_DEPS, False):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        # Should not raise
        cache.set("pergunta", "resposta")

    def test_set_silently_handles_upsert_error(self):
        cache = self._build_ready_cache()
        cache._collection.upsert.side_effect = Exception("upsert failed")
        # Should not raise
        cache.set("pergunta", "resposta")


class TestSemanticCacheSize:
    def test_size_delegates_to_collection_count(self):
        mock_col = _make_mock_collection()
        mock_col.count.return_value = 42
        mock_client = _make_mock_client(mock_col)
        mock_model = _make_mock_model()

        with patch(PATCH_DEPS, True), \
             patch(PATCH_CHROMA + ".PersistentClient", return_value=mock_client), \
             patch(PATCH_ST, return_value=mock_model):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        cache._collection = mock_col
        assert cache.size() == 42


class TestSemanticCacheClear:
    def test_clear_deletes_and_recreates_collection(self):
        mock_col = _make_mock_collection()
        mock_client = _make_mock_client(mock_col)
        mock_model = _make_mock_model()

        with patch(PATCH_DEPS, True), \
             patch(PATCH_CHROMA + ".PersistentClient", return_value=mock_client), \
             patch(PATCH_ST, return_value=mock_model):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        cache._client = mock_client
        cache.clear()

        mock_client.delete_collection.assert_called_once_with("semantic_cache")
        mock_client.get_or_create_collection.assert_called()

    def test_clear_does_nothing_when_not_ready(self):
        with patch(PATCH_DEPS, False):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        # Should not raise
        cache.clear()


class TestSemanticCacheContains:
    def test_contains_true_when_get_returns_response(self):
        mock_col = _make_mock_collection(distance=0.02)  # similarity=0.98 → hit
        mock_client = _make_mock_client(mock_col)
        mock_model = _make_mock_model()

        with patch(PATCH_DEPS, True), \
             patch(PATCH_CHROMA + ".PersistentClient", return_value=mock_client), \
             patch(PATCH_ST, return_value=mock_model):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake", threshold=0.90)

        cache._model = mock_model
        cache._collection = mock_col
        assert ("O que é RAG?" in cache) is True

    def test_contains_false_when_get_returns_none(self):
        with patch(PATCH_DEPS, False):
            from src.infrastructure.external.semantic_cache import SemanticCache
            cache = SemanticCache(persist_dir="/tmp/fake")

        assert ("pergunta inexistente" in cache) is False
