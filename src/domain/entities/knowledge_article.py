"""KnowledgeArticle Entity - Represents knowledge base content"""

from typing import Optional


class KnowledgeArticle:
    """
    Entity representing a chunk of knowledge from knowledge base.
    - Immutable
    - Encapsulates knowledge retrieval logic
    """
    
    def __init__(
        self,
        title: str,
        content: str,
        source: Optional[str] = None,
        relevance_score: float = 0.0
    ):
        """
        Args:
            title: Article title/section
            content: Article content
            source: Source file/section
            relevance_score: Relevance score for ranking (0-1)
        """
        self._validate_inputs(title, content)
        
        self._title = title
        self._content = content
        self._source = source
        self._relevance_score = min(max(relevance_score, 0.0), 1.0)
    
    @staticmethod
    def _validate_inputs(title: str, content: str) -> None:
        """Validates inputs"""
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title must be non-empty string")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Content must be non-empty string")
    
    @property
    def title(self) -> str:
        """Returns article title"""
        return self._title
    
    @property
    def content(self) -> str:
        """Returns article content"""
        return self._content
    
    @property
    def source(self) -> Optional[str]:
        """Returns article source"""
        return self._source
    
    @property
    def relevance_score(self) -> float:
        """Returns relevance score (0-1)"""
        return self._relevance_score
    
    def is_relevant(self, threshold: float = 0.5) -> bool:
        """Check if article meets relevance threshold"""
        return self._relevance_score >= threshold
    
    def __repr__(self) -> str:
        return (
            f"KnowledgeArticle(title='{self._title}', "
            f"source='{self._source}', score={self._relevance_score:.2f})"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "title": self._title,
            "content": self._content,
            "source": self._source,
            "relevance_score": self._relevance_score
        }
