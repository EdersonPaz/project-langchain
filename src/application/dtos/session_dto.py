"""Session DTO - Data Transfer Object for sessions"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SessionDTO:
    """Data Transfer Object for Session"""
    
    session_id: str
    created_at: datetime
    message_count: int = 0
    metadata: dict | None = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionDTO":
        """Create DTO from dictionary"""
        return cls(
            session_id=data["session_id"],
            created_at=data.get("created_at", datetime.now()),
            message_count=data.get("message_count", 0),
            metadata=data.get("metadata")
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "message_count": self.message_count,
            "metadata": self.metadata
        }
