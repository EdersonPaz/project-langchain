"""Semantic Cache - ChromaDB + local embeddings for similarity-based caching"""

import hashlib
from pathlib import Path
from typing import Optional

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    _SEMANTIC_DEPS_AVAILABLE = True
except ImportError:
    _SEMANTIC_DEPS_AVAILABLE = False


class SemanticCache:
    """
    Semantic response cache using ChromaDB + sentence-transformers.

    Unlike the MD5 cache (exact match only), this cache matches semantically
    similar queries — e.g. "Como criar uma chain?" and "Como faço uma chain?"
    both hit the same cached response.

    - Embeddings are generated locally (no API cost)
    - Model: paraphrase-multilingual-MiniLM-L12-v2 (supports Portuguese)
    - Persisted to disk via ChromaDB
    - Falls back gracefully if dependencies are missing
    """

    _MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    _COLLECTION_NAME = "semantic_cache"

    def __init__(self, persist_dir: str, threshold: float = 0.90):
        """
        Args:
            persist_dir: Directory to persist ChromaDB data
            threshold: Cosine similarity threshold (0-1). Higher = stricter matching.
                       0.90 recommended; lower values increase hit rate but risk false matches.
        """
        self.threshold = threshold
        self._ready = False

        if not _SEMANTIC_DEPS_AVAILABLE:
            print("[WARNING] SemanticCache: chromadb or sentence-transformers not installed. "
                  "Run: pip install chromadb sentence-transformers")
            return

        try:
            Path(persist_dir).mkdir(parents=True, exist_ok=True)
            self._model = SentenceTransformer(self._MODEL_NAME)
            self._client = chromadb.PersistentClient(path=persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self._COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            self._ready = True
        except Exception as e:
            print(f"[SemanticCache] WARNING: failed to initialize - {e}")

    def get(self, query: str) -> Optional[str]:
        """
        Return cached response if a semantically similar query was seen before.

        Args:
            query: The user's current query

        Returns:
            Cached response string, or None if no match above threshold
        """
        if not self._ready or self._collection.count() == 0:
            return None

        try:
            embedding = self._model.encode([query]).tolist()
            results = self._collection.query(
                query_embeddings=embedding,
                n_results=1,
                include=["metadatas", "distances"]
            )
            distances = results.get("distances", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            if distances and metadatas:
                # ChromaDB cosine space: distance = 1 - cosine_similarity
                similarity = 1.0 - distances[0]
                if similarity >= self.threshold:
                    return metadatas[0].get("response")
        except Exception as e:
            print(f"[WARNING] SemanticCache.get error: {e}")

        return None

    def set(self, query: str, response: str) -> None:
        """
        Store a query-response pair in the semantic cache.

        Args:
            query: The user's query
            response: The LLM response to cache
        """
        if not self._ready:
            return

        try:
            embedding = self._model.encode([query]).tolist()
            doc_id = hashlib.md5(query.encode()).hexdigest()
            self._collection.upsert(
                ids=[doc_id],
                embeddings=embedding,
                documents=[query],
                metadatas=[{"response": response}]
            )
        except Exception as e:
            print(f"[WARNING] SemanticCache.set error: {e}")

    def clear(self) -> None:
        """Delete all cached entries."""
        if not self._ready:
            return
        try:
            self._client.delete_collection(self._COLLECTION_NAME)
            self._collection = self._client.get_or_create_collection(
                name=self._COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"[WARNING] SemanticCache.clear error: {e}")

    def size(self) -> int:
        """Return number of cached entries."""
        if not self._ready:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def is_ready(self) -> bool:
        """Return True if semantic cache is operational."""
        return self._ready

    def __contains__(self, query: str) -> bool:
        return self.get(query) is not None
