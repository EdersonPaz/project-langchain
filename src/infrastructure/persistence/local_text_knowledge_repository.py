"""Local Text Knowledge Repository - Text search implementation"""

from pathlib import Path
from typing import List
from ...domain.entities import KnowledgeArticle
from ...domain.repositories import KnowledgeRepository


class LocalTextKnowledgeRepository(KnowledgeRepository):
    """
    Local text search implementation of KnowledgeRepository.
    - Loads markdown files and indexes by sections
    - Simple keyword-based search (no embeddings = no cost)
    - Suitable for small to medium knowledge bases
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._docs: List[KnowledgeArticle] = []
        self._loaded = False
    
    def load(self) -> None:
        """Load and process knowledge base file"""
        if not Path(self.file_path).exists():
            print(f"⚠️  Knowledge base file not found: {self.file_path}")
            self._loaded = True
            return
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split by sections (##)
            sections = content.split("##")
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Extract title and content
                lines = section.split("\\n", 1)
                title = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else section
                
                article = KnowledgeArticle(
                    title=title,
                    content=body[:500],  # Truncate for efficiency
                    source=self.file_path
                )
                self._docs.append(article)
            
            self._loaded = True
            print(f"✅  Knowledge base loaded: {len(self._docs)} sections")
        
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            self._loaded = True
    
    def search(self, query: str, top_k: int = 3) -> List[KnowledgeArticle]:
        """Search using keyword matching"""
        if not self._loaded:
            self.load()
        
        if not self._docs:
            return []
        
        # Score documents by keyword occurrences
        query_lower = query.lower()
        keywords = query_lower.split()
        
        scored_docs = []
        for doc in self._docs:
            score = 0
            content_lower = (doc.title + " " + doc.content).lower()
            
            for keyword in keywords:
                score += content_lower.count(keyword)
            
            if score > 0:
                # Create new article with relevance score
                doc_with_score = KnowledgeArticle(
                    title=doc.title,
                    content=doc.content,
                    source=doc.source,
                    relevance_score=min(score / 100.0, 1.0)  # Normalize to 0-1
                )
                scored_docs.append(doc_with_score)
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_docs[:top_k]
    
    def get_all(self) -> List[KnowledgeArticle]:
        """Get all articles"""
        if not self._loaded:
            self.load()
        return self._docs.copy()
    
    def is_loaded(self) -> bool:
        """Check if loaded"""
        return self._loaded
