"""
Fixtures compartilhadas para testes.
"""

import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest


# =========================================================
# FIXTURES DE AMBIENTE
# =========================================================

@pytest.fixture
def temp_db():
    """Cria um banco SQLite temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def temp_env(monkeypatch):
    """Configura variáveis de ambiente para testes."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345")
    return {
        "OPENAI_API_KEY": "sk-test-key-12345"
    }


@pytest.fixture
def mock_llm():
    """Mock do ChatOpenAI."""
    mock = MagicMock()
    mock.invoke = Mock(return_value=Mock(content="Resposta teste"))
    mock.stream = Mock(return_value=iter([Mock(content="Resp")]))
    return mock


@pytest.fixture
def mock_embeddings():
    """Mock de embeddings."""
    mock = MagicMock()
    mock.embed_query = Mock(return_value=[0.1, 0.2, 0.3])
    mock.embed_documents = Mock(return_value=[[0.1, 0.2], [0.3, 0.4]])
    return mock


@pytest.fixture(scope="session")
def mock_embeddings_cached():
    """
    🚀 OTIMIZAÇÃO: Mock de embeddings com escopo session.
    Reutiliza entre todos os testes (-600 tokens).
    """
    mock = MagicMock()
    mock.embed_query = Mock(return_value=[0.1] * 1536)  # Dimensão OpenAI padrão
    mock.embed_documents = Mock(return_value=[[0.1] * 1536 for _ in range(10)])
    return mock


@pytest.fixture
def mock_retriever():
    """Mock do retriever RAG."""
    mock = MagicMock()
    mock.invoke = Mock(return_value=[
        Mock(page_content="Documento 1 sobre LangChain"),
        Mock(page_content="Documento 2 sobre Python"),
    ])
    return mock


@pytest.fixture(scope="session")
def mock_faiss_optimized():
    """
    🚀 OTIMIZAÇÃO: Mock FAISS com escopo session (-1000 tokens).
    Evita carregar FAISS real e dividir documentos.
    Retorna uma função mock que simula FAISS.from_texts()
    """
    mock_instance = MagicMock()
    mock_instance.as_retriever = Mock(
        return_value=Mock(invoke=Mock(return_value=[
            Mock(page_content="KB chunk 1"),
            Mock(page_content="KB chunk 2"),
            Mock(page_content="KB chunk 3"),
        ]))
    )
    # Retorna a instância que será usada com patch
    def mock_faiss_from_texts(*args, **kwargs):
        return mock_instance
    return mock_faiss_from_texts


# =========================================================
# FIXTURES DE BANCO DE DADOS
# =========================================================

@pytest.fixture
def db_connection(temp_db):
    """Cria conexão com banco de dados de teste."""
    conn = sqlite3.connect(temp_db)
    
    # Criar tabela
    conn.execute("""
        CREATE TABLE IF NOT EXISTS message_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            message_type TEXT NOT NULL,
            message_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    yield conn
    
    conn.close()


@pytest.fixture
def db_with_data(db_connection):
    """Banco com dados de teste."""
    cursor = db_connection.cursor()
    
    test_data = [
        ("user_20260316", "human", "O que é LangChain?"),
        ("user_20260316", "ai", "LangChain é um framework..."),
        ("user_20260316", "human", "Como usar FAISS?"),
        ("user_20260316", "ai", "FAISS é uma biblioteca..."),
    ]
    
    cursor.executemany(
        "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
        test_data
    )
    db_connection.commit()
    
    return db_connection


# =========================================================
# FIXTURES DE DADOS
# =========================================================

@pytest.fixture
def sample_conversation():
    """Conversa de exemplo para testes."""
    return [
        {"role": "user", "content": "Qual é a diferença entre eval() e exec()?"},
        {"role": "assistant", "content": "eval() avalia uma expressão e retorna o resultado..."},
        {"role": "user", "content": "E sobre segurança?"},
        {"role": "assistant", "content": "Ambas são perigosas e devem ser evitadas..."},
    ]


@pytest.fixture
def knowledge_base_content():
    """Conteúdo da base de conhecimento para testes."""
    return """
# Base de Conhecimento - LangChain

## O que é LangChain?
LangChain é um framework para desenvolvimento com LLMs.

## Componentes Principais
- Models: ChatOpenAI, Ollama
- Prompts: ChatPromptTemplate
- Chains: Conexão de componentes
- Memory: Histórico de conversas
- Tools: Funções que o LLM pode usar

## Boas Práticas
- Nunca hardcodear API keys
- Sempre validar inputs
- Usar environment variables
"""


@pytest.fixture
def security_test_cases():
    """Casos de teste para segurança."""
    return {
        "api_key_patterns": [
            "sk-abc123def456",
            "OPENAI_API_KEY=sk-test",
            "my-key-is-sk-12345",
        ],
        "dangerous_code": [
            "eval('1+1')",
            "exec('print(x)')",
            "os.system('ls')",
        ],
        "safe_code": [
            "print('hello')",
            "x = 1 + 1",
            "def foo(): pass",
        ],
    }


# =========================================================
# FIXTURES DE PERFORMANCE
# =========================================================

@pytest.fixture
def performance_config():
    """Configurações para testes de performance."""
    return {
        "max_response_time": 5.0,  # segundos
        "max_memory": 500,  # MB
        "max_db_query_time": 0.1,  # segundos
    }


# =========================================================
# 🚀 FIXTURES DE OTIMIZAÇÃO DE CUSTOS
# =========================================================

@pytest.fixture
def mock_app_file_content():
    """
    🚀 OTIMIZAÇÃO: Conteúdo mockado de app.py (-100 tokens).
    Evita leitura do arquivo real durante testes.
    """
    return """
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("❌ OPENAI_API_KEY não configurada no .env")

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
"""
