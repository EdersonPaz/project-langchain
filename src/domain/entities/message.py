"""Message Entity - Represents a single message in conversation"""

from datetime import datetime
from typing import Literal
from ..value_objects import MessageContent, SessionId


class Message:
    """
    Entity representing a single message.
    - Has unique identity (id + session_id)
    - Immutable after creation
    - Encapsulates message business logic
    """
    
    def __init__(
        self,
        session_id: SessionId,
        content: MessageContent,
        message_type: Literal["human", "assistant", "system"],
        message_id: int | None = None,
        created_at: datetime | None = None
    ):
        """
        Args:
            session_id: Session this message belongs to
            content: Message text content
            message_type: Type of message (user input or assistant response)
            message_id: Database ID (optional for new messages)
            created_at: Creation timestamp (optional)
        """
        self._id = message_id
        self._session_id = session_id
        self._content = content
        self._message_type = message_type
        self._created_at = created_at or datetime.now()
    
    @property
    def id(self) -> int | None:
        """Returns message ID (None if not persisted yet)"""
        return self._id
    
    @property
    def session_id(self) -> SessionId:
        """Returns session ID"""
        return self._session_id
    
    @property
    def content(self) -> MessageContent:
        """Returns message content"""
        return self._content
    
    @property
    def message_type(self) -> str:
        """Returns message type"""
        return self._message_type
    
    @property
    def created_at(self) -> datetime:
        """Returns creation timestamp"""
        return self._created_at
    
    def is_persisted(self) -> bool:
        """Check if message was persisted to database"""
        return self._id is not None
    
    def __repr__(self) -> str:
        return (
            f"Message(id={self._id}, session={self._session_id.value}, "
            f"type={self._message_type}, created_at={self._created_at})"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "id": self._id,
            "session_id": self._session_id.value,
            "content": self._content.value,
            "message_type": self._message_type,
            "created_at": self._created_at.isoformat()
        }
