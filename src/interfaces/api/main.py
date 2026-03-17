"""API Interface - FastAPI endpoints for LangChain assistant"""

from typing import Optional, List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from openai import RateLimitError

from ...infrastructure.config import Settings
from ...infrastructure.persistence import SQLMessageRepository, LocalTextKnowledgeRepository
from ...infrastructure.external import ResponseCache, SemanticCache
from ...application.services import ChatService, KnowledgeService, SecurityService
from ...domain.value_objects import SessionId, MessageContent
from ...domain.entities import Message


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Pergunta do usuário")
    session_id: Optional[str] = Field(None, description="ID de sessão (se não fornecido, um novo será criado)")
    use_context: Optional[bool] = Field(True, description="Se deve usar contexto RAG")


class ChatResponse(BaseModel):
    content: str
    session_id: str
    is_from_cache: bool
    context_used: List[str]
    metadata: dict


class HistoryItem(BaseModel):
    id: Optional[int]
    session_id: str
    message_type: str
    content: str
    created_at: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[HistoryItem]


def _create_cache():
    if Settings.USE_SEMANTIC_CACHE:
        cache = SemanticCache(
            persist_dir=Settings.SEMANTIC_CACHE_DIR,
            threshold=Settings.SEMANTIC_CACHE_THRESHOLD
        )
        if cache.is_ready():
            return cache
    return ResponseCache(Settings.CACHE_FILE)


def _create_services():
    Settings.validate()

    message_repo = SQLMessageRepository(Settings.DB_PATH)
    knowledge_repo = LocalTextKnowledgeRepository(Settings.KNOWLEDGE_BASE_FILE)

    chat_service = ChatService(
        message_repo=message_repo,
        knowledge_repo=knowledge_repo,
        model=Settings.OPENAI_MODEL,
        temperature=Settings.OPENAI_TEMPERATURE,
        db_path=Settings.DB_PATH
    )

    knowledge_service = KnowledgeService(knowledge_repo)
    security_service = SecurityService()
    cache = _create_cache()

    return message_repo, chat_service, knowledge_service, security_service, cache


message_repo, chat_service, knowledge_service, security_service, response_cache = _create_services()

app = FastAPI(
    title="LangChain DDD Assistant API",
    version="0.1.0",
    description="API RESTful para o assistente com persistência SQLite + RAG"
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "api"}


@app.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session():
    session = SessionId()
    return {"session_id": session.value}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query não pode estar vazia")

    is_valid, error_message = security_service.validate_input(query)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    session_id = request.session_id or SessionId().value

    # Check semantic/MD5 cache before calling LLM
    if Settings.ENABLE_RESPONSE_CACHE:
        cached = response_cache.get(query)
        if cached:
            return {
                "content": cached,
                "session_id": session_id,
                "is_from_cache": True,
                "context_used": [],
                "metadata": {"cache": "hit"}
            }

    # Persist user message
    human_message = Message(
        session_id=SessionId(session_id),
        content=MessageContent(query),
        message_type="human"
    )
    message_repo.add(human_message)

    try:
        response_dto = await chat_service.ask(
            query=query,
            session_id=session_id,
            use_context=request.use_context if request.use_context is not None else True
        )

    except RateLimitError as e:
        raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded") from e

    # Store in cache
    if Settings.ENABLE_RESPONSE_CACHE:
        response_cache.set(query, response_dto.content)

    # Persist assistant response
    assistant_message = Message(
        session_id=SessionId(session_id),
        content=MessageContent(response_dto.content),
        message_type="assistant"
    )
    message_repo.add(assistant_message)

    # Limpar histórico antigo se configurado
    message_repo.delete_old(SessionId(session_id), keep_count=Settings.MAX_HISTORY_MESSAGES)

    return response_dto.to_dict()


@app.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str, limit: int = 20):
    try:
        sid = SessionId(session_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    messages = message_repo.get_by_session(sid, limit=limit)
    return {
        "session_id": sid.value,
        "messages": [Message(
            session_id=msg.session_id,
            content=msg.content,
            message_type=msg.message_type,
            message_id=msg.id,
            created_at=msg.created_at
        ).to_dict() for msg in messages]
    }
