"""Response DTO - Data Transfer Object for chat responses"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResponseDTO:
    """Data Transfer Object for Chat Response"""
    
    content: str
    session_id: str
    is_from_cache: bool = False
    context_used: Optional[list] = field(default_factory=lambda: [])
    metadata: dict = field(default_factory=lambda: {})
    
    @classmethod
    def from_dict(cls, data: dict) -> "ResponseDTO":
        """Create DTO from dictionary"""
        return cls(
            content=data["content"],
            session_id=data["session_id"],
            is_from_cache=data.get("is_from_cache", False),
            context_used=data.get("context_used", []),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "session_id": self.session_id,
            "is_from_cache": self.is_from_cache,
            "context_used": self.context_used,
            "metadata": self.metadata
        }
