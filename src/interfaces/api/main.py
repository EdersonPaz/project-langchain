"""API Interface - FastAPI endpoints for LangChain assistant"""

from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from openai import RateLimitError

from ...infrastructure.config import Settings
from ...infrastructure.persistence import SQLMessageRepository, LocalTextKnowledgeRepository
from ...infrastructure.external import ResponseCache, SemanticCache
from ...application.services import ChatService, KnowledgeService, SecurityService
from ...domain.value_objects import SessionId, MessageContent
from ...domain.entities import Message


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Pergunta ou mensagem do usuário",
        examples=["O que é LangChain?"]
    )
    session_id: Optional[str] = Field(
        None,
        description="ID de sessão existente. Se omitido, uma nova sessão é criada automaticamente.",
        examples=["user_20260319_120000_abc123"]
    )
    use_context: Optional[bool] = Field(
        True,
        description="Se verdadeiro, busca contexto relevante na base de conhecimento (RAG) antes de responder."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Pergunta simples",
                    "value": {
                        "query": "O que é LangChain?",
                        "use_context": True
                    }
                },
                {
                    "summary": "Pergunta com sessão existente",
                    "value": {
                        "query": "Como uso LCEL?",
                        "session_id": "user_20260319_120000_abc123",
                        "use_context": True
                    }
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    content: str = Field(description="Resposta gerada pelo assistente")
    session_id: str = Field(description="ID da sessão utilizada ou criada")
    is_from_cache: bool = Field(description="Indica se a resposta foi retornada do cache (sem chamar o LLM)")
    context_used: List[str] = Field(description="Títulos das seções da base de conhecimento utilizadas como contexto")
    metadata: dict = Field(description="Metadados da resposta (modelo usado, cache hit, etc.)")
    source: str = Field(default="openai", description="Origem da resposta: 'cache', 'knowledge_base' ou 'openai'")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "LangChain é um framework para desenvolver aplicações com LLMs...",
                    "session_id": "user_20260319_120000_abc123",
                    "is_from_cache": False,
                    "context_used": ["O que é LangChain", "Componentes principais"],
                    "metadata": {"model": "gpt-3.5-turbo"}
                }
            ]
        }
    }


class SessionResponse(BaseModel):
    session_id: str = Field(description="ID único da sessão criada")

    model_config = {
        "json_schema_extra": {
            "examples": [{"session_id": "user_20260319_120000_abc123"}]
        }
    }


class HealthResponse(BaseModel):
    status: str = Field(description="Estado da API")
    mode: str = Field(description="Modo de execução")

    model_config = {
        "json_schema_extra": {
            "examples": [{"status": "ok", "mode": "api"}]
        }
    }


class HistoryItem(BaseModel):
    id: Optional[int] = Field(None, description="ID único da mensagem no banco")
    session_id: str = Field(description="ID da sessão")
    message_type: str = Field(description="Tipo da mensagem: 'human' ou 'assistant'")
    content: str = Field(description="Conteúdo da mensagem")
    created_at: str = Field(description="Timestamp de criação (ISO 8601)")


class HistoryResponse(BaseModel):
    session_id: str = Field(description="ID da sessão")
    messages: List[HistoryItem] = Field(description="Lista de mensagens em ordem cronológica")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "user_20260319_120000_abc123",
                    "messages": [
                        {
                            "id": 1,
                            "session_id": "user_20260319_120000_abc123",
                            "message_type": "human",
                            "content": "O que é LangChain?",
                            "created_at": "2026-03-19T12:00:00"
                        },
                        {
                            "id": 2,
                            "session_id": "user_20260319_120000_abc123",
                            "message_type": "assistant",
                            "content": "LangChain é um framework...",
                            "created_at": "2026-03-19T12:00:05"
                        }
                    ]
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    detail: str = Field(description="Descrição do erro")


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

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

_DESCRIPTION = """
## LangChain DDD Assistant API

Assistente inteligente com **persistência de histórico**, **RAG local** e **cache semântico**.

### Funcionalidades
- **Chat com IA** — envia perguntas e recebe respostas do GPT via LangChain
- **Sessões persistentes** — histórico salvo em SQLite, não apaga ao reiniciar
- **RAG por palavras-chave** — contexto relevante da base de conhecimento injetado automaticamente (sem custo de embeddings)
- **Cache semântico** — respostas similares retornadas do cache ChromaDB (~50-70% de hit rate)
- **Validação de segurança** — detecta API keys expostas e código perigoso

### Fluxo de uso
1. `POST /sessions` — crie uma sessão (opcional, o chat cria automaticamente)
2. `POST /chat` — envie perguntas usando o `session_id` retornado
3. `GET /history/{session_id}` — consulte o histórico da conversa
"""

app = FastAPI(
    title="LangChain DDD Assistant API",
    version="1.0.0",
    description=_DESCRIPTION,
    contact={
        "name": "LangChain DDD Project",
        "url": "https://github.com/EdersonPaz/project-langchain",
    },
    license_info={"name": "MIT"},
    openapi_tags=[
        {
            "name": "health",
            "description": "Verificação de disponibilidade da API."
        },
        {
            "name": "sessions",
            "description": "Gerenciamento de sessões de conversa."
        },
        {
            "name": "chat",
            "description": "Envio de perguntas e recebimento de respostas do assistente."
        },
        {
            "name": "history",
            "description": "Consulta ao histórico de mensagens de uma sessão."
        },
    ]
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Verifica se a API está operacional.",
)
async def health_check():
    return {"status": "ok", "mode": "api"}


@app.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["sessions"],
    summary="Criar nova sessão",
    description=(
        "Cria um novo ID de sessão único. "
        "Cada sessão mantém seu próprio histórico de conversa no SQLite. "
        "O `session_id` também é criado automaticamente pelo endpoint `/chat` se não for fornecido."
    ),
    responses={201: {"description": "Sessão criada com sucesso"}},
)
async def create_session():
    session = SessionId()
    return {"session_id": session.value}


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["chat"],
    summary="Enviar mensagem ao assistente",
    description=(
        "Envia uma pergunta ao assistente e retorna a resposta gerada pelo LLM.\n\n"
        "**Fluxo interno:**\n"
        "1. Valida a entrada (detecta API keys, código perigoso)\n"
        "2. Verifica o cache semântico (ChromaDB) ou MD5 — se hit, retorna sem chamar o LLM\n"
        "3. Busca contexto relevante na base de conhecimento (RAG por palavras-chave)\n"
        "4. Chama o LLM com histórico + contexto\n"
        "5. Armazena a resposta no cache e no SQLite\n\n"
        "Se `session_id` não for fornecido, uma nova sessão é criada automaticamente."
    ),
    responses={
        200: {"description": "Resposta gerada com sucesso"},
        400: {"model": ErrorResponse, "description": "Query inválida ou vazia"},
        429: {"model": ErrorResponse, "description": "Limite de requisições da OpenAI atingido"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"},
    },
)
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
                "metadata": {"cache": "hit"},
                "source": "cache"
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


@app.get(
    "/history/{session_id}",
    response_model=HistoryResponse,
    tags=["history"],
    summary="Consultar histórico da sessão",
    description=(
        "Retorna as mensagens de uma sessão em ordem cronológica.\n\n"
        "Use o parâmetro `limit` para controlar quantas mensagens retornar (padrão: 20)."
    ),
    responses={
        200: {"description": "Histórico retornado com sucesso"},
        400: {"model": ErrorResponse, "description": "session_id inválido"},
    },
)
async def get_history(
    session_id: str,
    limit: int = Query(default=20, ge=1, le=200, description="Número máximo de mensagens a retornar")
):
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
