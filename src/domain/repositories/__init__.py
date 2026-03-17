"""Domain Repositories (Abstract Base Classes)"""

from .message_repository import MessageRepository
from .knowledge_repository import KnowledgeRepository

__all__ = ["MessageRepository", "KnowledgeRepository"]
