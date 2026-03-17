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

from langchain_openai import ChatOpenAI
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


def criar_prompt(retriever=None):
    repository = SQLMessageRepository(Settings.DB_PATH)
    knowledge_repo = LocalTextKnowledgeRepository(Settings.KNOWLEDGE_BASE_FILE)
    chat_service = ChatService(repository, knowledge_repo, model=Settings.OPENAI_MODEL, temperature=Settings.OPENAI_TEMPERATURE, db_path=Settings.DB_PATH)
    return chat_service._create_prompt(use_context=bool(retriever), context="")


def criar_chain(retriever=None):
    prompt = criar_prompt(retriever)
    chat_service = ChatService(SQLMessageRepository(Settings.DB_PATH), LocalTextKnowledgeRepository(Settings.KNOWLEDGE_BASE_FILE), model=Settings.OPENAI_MODEL, temperature=Settings.OPENAI_TEMPERATURE, db_path=Settings.DB_PATH)
    return prompt | chat_service._llm


def criar_chain_com_historico(retriever=None):
    chain = criar_chain(retriever)
    chat_service = ChatService(SQLMessageRepository(Settings.DB_PATH), LocalTextKnowledgeRepository(Settings.KNOWLEDGE_BASE_FILE), model=Settings.OPENAI_MODEL, temperature=Settings.OPENAI_TEMPERATURE, db_path=Settings.DB_PATH)
    from langchain_core.runnables.history import RunnableWithMessageHistory
    chain_with_history = RunnableWithMessageHistory(chain, chat_service._get_session_history, input_messages_key="input", history_messages_key="history")
    return chain_with_history


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

