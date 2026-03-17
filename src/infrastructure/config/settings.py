"""Settings - Application configuration"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Settings:
    """Application configuration settings"""
    
    # Load environment variables
    load_dotenv()
    
    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("LANGCHAIN_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.5"))
    
    # Database Configuration
    DB_PATH: str = os.getenv("DB_PATH", "chat_history.db")
    DB_URL: str = f"sqlite:///{DB_PATH}"
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_FILE: str = os.getenv("KNOWLEDGE_BASE_FILE", "knowledge_base.md")
    USE_RAG: bool = os.getenv("USE_RAG", "true").lower() == "true"
    
    # Cache Configuration
    CACHE_DIR: str = os.getenv("CACHE_DIR", "cache")
    CACHE_FILE: str = os.getenv("CACHE_FILE", f"{CACHE_DIR}/response_cache.json")
    ENABLE_RESPONSE_CACHE: bool = os.getenv("ENABLE_RESPONSE_CACHE", "true").lower() == "true"

    # Semantic Cache Configuration (ChromaDB + local embeddings)
    USE_SEMANTIC_CACHE: bool = os.getenv("USE_SEMANTIC_CACHE", "true").lower() == "true"
    SEMANTIC_CACHE_DIR: str = os.getenv("SEMANTIC_CACHE_DIR", f"{CACHE_DIR}/semantic_cache")
    SEMANTIC_CACHE_THRESHOLD: float = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.90"))
    
    # History Configuration
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    
    # Session Configuration
    SESSION_TIMEOUT_HOURS: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY is not configured in .env")
        
        # Create cache directory if needed
        Path(cls.CACHE_DIR).mkdir(exist_ok=True)
        
        return True
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert settings to dictionary"""
        return {
            "openai_model": cls.OPENAI_MODEL,
            "openai_temperature": cls.OPENAI_TEMPERATURE,
            "db_path": cls.DB_PATH,
            "knowledge_base_file": cls.KNOWLEDGE_BASE_FILE,
            "use_rag": cls.USE_RAG,
            "max_history_messages": cls.MAX_HISTORY_MESSAGES,
            "enable_response_cache": cls.ENABLE_RESPONSE_CACHE
        }

