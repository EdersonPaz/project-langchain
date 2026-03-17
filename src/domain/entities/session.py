"""Session Entity - Represents a conversation session"""

from datetime import datetime
from typing import Optional
from ..value_objects import SessionId


class Session:
    """
    Entity representing a conversation session.
    - Container for messages
    - Business logic for session management
    """
    
    def __init__(
        self,
        session_id: SessionId,
        created_at: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ):
        """
        Args:
            session_id: Unique session identifier
            created_at: Session creation timestamp
            metadata: Additional session data
        """
        self._session_id = session_id
        self._created_at = created_at or datetime.now()
        self._metadata = metadata or {}
        self._message_count = 0
    
    @property
    def session_id(self) -> SessionId:
        """Returns session ID"""
        return self._session_id
    
    @property
    def created_at(self) -> datetime:
        """Returns creation timestamp"""
        return self._created_at
    
    @property
    def message_count(self) -> int:
        """Returns number of messages in session"""
        return self._message_count
    
    @property
    def metadata(self) -> dict:
        """Returns session metadata"""
        return self._metadata
    
    def increment_message_count(self) -> None:
        """Increment message counter"""
        self._message_count += 1
    
    def is_old(self, hours: int = 24) -> bool:
        """Check if session is older than specified hours"""
        age = datetime.now() - self._created_at
        return age.total_seconds() > (hours * 3600)
    
    def __repr__(self) -> str:
        return (
            f"Session(id={self._session_id.value}, "
            f"messages={self._message_count}, "
            f"created_at={self._created_at})"
        )
