"""Knowledge Service - Manages knowledge base operations"""

from typing import List
from ...domain.entities import KnowledgeArticle
from ...domain.repositories import KnowledgeRepository


class KnowledgeService:
    """
    Application service for knowledge base operations.
    - Manages knowledge base loading
    - Searches and retrieves knowledge
    """
    
    def __init__(self, knowledge_repo: KnowledgeRepository):
        self.knowledge_repo = knowledge_repo
    
    def initialize(self) -> None:
        """Initialize and load knowledge base"""
        self.knowledge_repo.load()
    
    def search(self, query: str, top_k: int = 3) -> List[KnowledgeArticle]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant articles
        """
        if not self.knowledge_repo.is_loaded():
            self.initialize()
        
        return self.knowledge_repo.search(query, top_k=top_k)
    
    def get_all(self) -> List[KnowledgeArticle]:
        """Get all knowledge articles"""
        if not self.knowledge_repo.is_loaded():
            self.initialize()
        
        return self.knowledge_repo.get_all()
    
    def is_available(self) -> bool:
        """Check if knowledge base is available"""
        return self.knowledge_repo.is_loaded()
