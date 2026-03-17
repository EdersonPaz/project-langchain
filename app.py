#!/usr/bin/env python3
"""
LangChain Assistant - DDD Architecture Edition

This is the main entry point for the application.
Supports both CLI (`--mode cli`) and FastAPI (`--mode api`).

Architecture:
  - Domain Layer: Core business logic and entities (src/domain/)
  - Application Layer: Use cases and services (src/application/)
  - Infrastructure Layer: Persistence and external services (src/infrastructure/)
  - Interfaces Layer: CLI, API, etc. (src/interfaces/)

Usage:
    python app.py --mode api
    python app.py --mode cli

For more information, see ARCHITECTURE_DDD.md
"""

import sys
import asyncio
import argparse

# ChatOpenAI must remain importable from this module — tests patch 'app.ChatOpenAI'
from langchain_openai import ChatOpenAI  # noqa: F401
from src.infrastructure.config import Settings
from src.infrastructure.persistence import SQLMessageRepository, LocalTextKnowledgeRepository
from src.application.services import ChatService, KnowledgeService, SecurityService
from src.domain.value_objects import SessionId
from src.domain.value_objects import MessageContent
from src.domain.entities import Message
from src.interfaces.cli import main as cli_main
from src.interfaces.api.main import app as fastapi_app

# Compatibilidade com testes antigos
DB_PATH = Settings.DB_PATH


def inicializar_banco_de_dados():
    """Cria a estrutura de database se não existir."""
    Settings.validate()
    db_path = globals().get("DB_PATH", Settings.DB_PATH)
    return SQLMessageRepository(db_path)


def validar_codigo_python(code: str):
    analysis = SecurityService.analyze_code(code)
    if analysis["has_issues"]:
        return f"Alertas encontrados: {analysis['issues']}"
    return "Nenhum problema crítico ✅"


def _build_chat_service() -> ChatService:
    """Builds a ChatService with default settings. Used by helper functions below."""
    return ChatService(
        SQLMessageRepository(Settings.DB_PATH),
        LocalTextKnowledgeRepository(Settings.KNOWLEDGE_BASE_FILE),
        model=Settings.OPENAI_MODEL,
        temperature=Settings.OPENAI_TEMPERATURE,
        db_path=Settings.DB_PATH
    )


def criar_prompt(retriever=None):
    chat_service = _build_chat_service()
    return chat_service._create_prompt(use_context=bool(retriever), context="")


def criar_chain(retriever=None):
    from langchain_core.runnables.history import RunnableWithMessageHistory
    chat_service = _build_chat_service()
    prompt = chat_service._create_prompt(use_context=bool(retriever), context="")
    return prompt | chat_service._llm


def criar_chain_com_historico(retriever=None):
    from langchain_core.runnables.history import RunnableWithMessageHistory
    chat_service = _build_chat_service()
    prompt = chat_service._create_prompt(use_context=bool(retriever), context="")
    chain = prompt | chat_service._llm
    return RunnableWithMessageHistory(
        chain,
        chat_service._get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangChain app runner")
    parser.add_argument("--mode", choices=["cli", "api"], default="api", help="Modo de execução")
    parser.add_argument("--host", default="0.0.0.0", help="Host para API")
    parser.add_argument("--port", type=int, default=8000, help="Porta para API")

    args = parser.parse_args()

    if args.mode == "cli":
        try:
            asyncio.run(cli_main())
        except Exception as e:
            print(f"❌ Fatal Error: {e}")
            sys.exit(1)
    else:
        import uvicorn
        uvicorn.run(fastapi_app, host=args.host, port=args.port)

