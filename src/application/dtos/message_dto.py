"""Message DTO - Data Transfer Object for messages"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class MessageDTO:
    """Data Transfer Object for Message"""
    
    session_id: str
    content: str
    message_type: Literal["human", "assistant", "system"]
    created_at: datetime
    id: int | None = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "MessageDTO":
        """Create DTO from dictionary"""
        return cls(
            id=data.get("id"),
            session_id=data["session_id"],
            content=data["content"],
            message_type=data["message_type"],
            created_at=data.get("created_at", datetime.now())
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "message_type": self.message_type,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
