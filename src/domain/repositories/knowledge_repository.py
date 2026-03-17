"""Knowledge Repository - Abstract interface for knowledge base access"""

from abc import ABC, abstractmethod
from typing import List
from ..entities import KnowledgeArticle


class KnowledgeRepository(ABC):
    """
    Repository interface for Knowledge base access.
    - Abstract interface
    - Defines contract for knowledge retrieval
    - Implementation in infrastructure layer (local text search, embeddings, etc.)
    """
    
    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[KnowledgeArticle]:
        """
        Search knowledge base for relevant articles.
        
        Args:
            query: Search query/text
            top_k: Number of top results to return
            
        Returns:
            List of relevant knowledge articles, sorted by relevance
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[KnowledgeArticle]:
        """
        Retrieve all articles from knowledge base.
        
        Returns:
            List of all knowledge articles
        """
        pass
    
    @abstractmethod
    def load(self) -> None:
        """
        Load/initialize knowledge base.
        Called on application startup.
        """
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if knowledge base is loaded in memory"""
        pass
