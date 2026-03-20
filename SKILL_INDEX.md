# SKILL INDEX — LangChain DDD Assistant
<!-- AUTO-GENERATED — run scripts/update_skill_index.py to refresh -->
<!-- Last updated: 2026-03-19 -->

## PURPOSE
This file is the single entry point for any LLM working on this project.
Read ONLY this file first. Read other files only when you need implementation details for a specific task.

---

## 1. ARCHITECTURE (DDD — 4 layers)

```
app.py                          ← entry point (CLI + API modes)
src/
  domain/                       ← entities, value objects, abstract repos (no deps)
  application/services/         ← ChatService, KnowledgeService, SecurityService
  infrastructure/
    config/settings.py          ← ALL configuration (reads .env)
    persistence/                ← SQLite + keyword-based knowledge repo
    external/                   ← OpenAI LLM, ResponseCache (MD5), SemanticCache
  interfaces/
    cli/main.py                 ← CLI async loop
    api/main.py                 ← FastAPI app (4 endpoints)
tests/                          ← 88 tests across 5 files
```

**Dependency direction:** domain ← application ← infrastructure ← interfaces

---

## 2. KEY FILES & WHAT THEY DO

| File | Purpose | Key exports |
|------|---------|-------------|
| `app.py` | Entry point + test-compat helpers | `inicializar_banco_de_dados`, `_build_chat_service`, `criar_prompt`, `criar_chain`, `criar_chain_com_historico`, `validar_codigo_python` |
| `src/infrastructure/config/settings.py` | All config via `@dataclass Settings` | `Settings.validate()`, `Settings.to_dict()` |
| `src/application/services/chat_service.py` | Orchestrates LLM + RAG + history | `ChatService.ask(query, session_id, use_context)` |
| `src/application/services/knowledge_service.py` | RAG operations | `KnowledgeService.search(query, top_k)` |
| `src/application/services/security_service.py` | Input validation + code analysis | `SecurityService.validate_input(text)`, `SecurityService.analyze_code(code)` |
| `src/infrastructure/persistence/sql_message_repository.py` | SQLite history | `SQLMessageRepository.add(msg)`, `.get_by_session(sid, limit)`, `.delete_old(sid, keep_count)` |
| `src/infrastructure/persistence/local_text_knowledge_repository.py` | Keyword RAG (zero cost) | `LocalTextKnowledgeRepository.search(query, top_k)`, `.is_loaded()` |
| `src/infrastructure/external/semantic_cache.py` | ChromaDB semantic cache | `SemanticCache(persist_dir, threshold)`, `.get(query)`, `.set(query, response)`, `.is_ready()`, `.clear()`, `.size()` |
| `src/infrastructure/external/response_cache.py` | MD5 JSON cache (fallback) | `ResponseCache(cache_file)`, `.get(query)`, `.set(query, response)` |
| `src/infrastructure/external/openai_llm_service.py` | OpenAI wrapper | `OpenAILLMService` |
| `src/interfaces/api/main.py` | FastAPI app + service wiring | `app`, `_create_cache()`, `_create_services()` |
| `src/interfaces/cli/main.py` | CLI async loop | `main()` async |
| `knowledge_base.md` | RAG knowledge source | Loaded on startup, ~180 lines |

---

## 3. CONFIGURATION (settings.py — all vars)

| Setting | .env Key | Default | Notes |
|---------|---------|---------|-------|
| `OPENAI_API_KEY` | `OPENAI_API_KEY` | `""` | Required — raises ValueError if empty |
| `OPENAI_MODEL` | `LANGCHAIN_MODEL` | `gpt-3.5-turbo` | Any OpenAI model string |
| `OPENAI_TEMPERATURE` | `OPENAI_TEMPERATURE` | `0.5` | float 0-2 |
| `DB_PATH` | `DB_PATH` | `chat_history.db` | SQLite file path |
| `KNOWLEDGE_BASE_FILE` | `KNOWLEDGE_BASE_FILE` | `knowledge_base.md` | RAG source |
| `USE_RAG` | `USE_RAG` | `true` | Enable/disable keyword RAG |
| `CACHE_DIR` | `CACHE_DIR` | `cache` | Base dir for cache files |
| `CACHE_FILE` | `CACHE_FILE` | `cache/response_cache.json` | MD5 cache |
| `ENABLE_RESPONSE_CACHE` | `ENABLE_RESPONSE_CACHE` | `true` | Master cache toggle |
| `USE_SEMANTIC_CACHE` | `USE_SEMANTIC_CACHE` | `true` | ChromaDB semantic cache |
| `SEMANTIC_CACHE_DIR` | `SEMANTIC_CACHE_DIR` | `cache/semantic_cache` | ChromaDB persist dir |
| `SEMANTIC_CACHE_THRESHOLD` | `SEMANTIC_CACHE_THRESHOLD` | `0.90` | Cosine similarity 0-1 |
| `MAX_HISTORY_MESSAGES` | `MAX_HISTORY_MESSAGES` | `20` | Auto-prune older messages |
| `SESSION_TIMEOUT_HOURS` | `SESSION_TIMEOUT_HOURS` | `24` | Session expiry |

---

## 4. API ENDPOINTS (FastAPI — src/interfaces/api/main.py)

| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| GET | `/health` | — | `{"status": "ok", "mode": "api"}` | Health check |
| POST | `/sessions` | — | `{"session_id": str}` | Creates new session UUID |
| POST | `/chat` | `ChatRequest` | `ChatResponse` | Main chat endpoint |
| GET | `/history/{session_id}` | — | — |  |
