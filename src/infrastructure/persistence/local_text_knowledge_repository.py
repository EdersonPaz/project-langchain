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
            print(f"[KB] WARNING: file not found: {self.file_path}")
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
                    content=body[:1000],
                    source=self.file_path
                )
                self._docs.append(article)
            
            self._loaded = True
            print(f"[KB] Loaded: {len(self._docs)} sections")

        except Exception as e:
            print(f"[KB] ERROR loading knowledge base: {e}")
            self._loaded = True
    
    _STOP_WORDS = {
        "a", "o", "e", "de", "do", "da", "dos", "das", "em", "no", "na",
        "nos", "nas", "um", "uma", "uns", "umas", "que", "se", "com", "por",
        "para", "ao", "aos", "as", "os", "é", "são", "foi", "tem", "ter",
        "ser", "seu", "sua", "seus", "suas", "mais", "ou", "mas", "como",
        "the", "is", "in", "on", "at", "to", "of", "a", "an", "and", "or",
    }

    def search(self, query: str, top_k: int = 3) -> List[KnowledgeArticle]:
        """Search using keyword matching (stop words filtered)"""
        if not self._loaded:
            self.load()

        if not self._docs:
            return []

        # Score documents by keyword occurrences (ignoring stop words)
        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if w not in self._STOP_WORDS and len(w) > 2]

        if not keywords:
            return []
        
        scored_docs = []
        for doc in self._docs:
            title_lower = doc.title.lower()
            content_lower = doc.content.lower()

            score = 0
            for keyword in keywords:
                # Title matches count 3x more than body matches
                score += title_lower.count(keyword) * 3
                score += content_lower.count(keyword)

            if score > 0:
                doc_with_score = KnowledgeArticle(
                    title=doc.title,
                    content=doc.content,
                    source=doc.source,
                    relevance_score=min(score / 100.0, 1.0)
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
