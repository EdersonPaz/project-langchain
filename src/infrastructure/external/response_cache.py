"""Response Cache - JSON-based caching for responses"""

import json
import hashlib
from pathlib import Path
from typing import Optional


class ResponseCache:
    """
    Simple JSON-based response cache.
    - Caches LLM responses to avoid duplicate calls
    - Saves tokens and reduces costs
    - Persistent across sessions
    """
    
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self._cache: dict = {}
        self.load()
    
    def load(self) -> None:
        """Load cache from file"""
        if Path(self.cache_file).exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception as e:
                print(f"[WARNING] Could not load cache: {e}")
                self._cache = {}
        else:
            self._cache = {}
    
    def save(self) -> None:
        """Save cache to file"""
        try:
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARNING] Could not save cache: {e}")
    
    @staticmethod
    def _make_key(text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[str]:
        """
        Retrieve cached response.
        
        Args:
            query: Query text
            
        Returns:
            Cached response or None
        """
        key = self._make_key(query)
        return self._cache.get(key)
    
    def set(self, query: str, response: str) -> None:
        """
        Cache a response.
        
        Args:
            query: Query text
            response: Response text to cache
        """
        key = self._make_key(query)
        self._cache[key] = response
        self.save()
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache = {}
        self.save()
    
    def size(self) -> int:
        """Get number of cached responses"""
        return len(self._cache)
    
    def __contains__(self, query: str) -> bool:
        """Check if query is in cache"""
        key = self._make_key(query)
        return key in self._cache
