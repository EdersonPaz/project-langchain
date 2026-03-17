"""SessionId Value Object - Represents a unique session identifier"""

from typing import Optional
from datetime import datetime
import uuid


class SessionId:
    """
    Value Object representing a unique session ID.
    - Immutable
    - Encapsulates session ID generation and validation
    - Domain logic for session identification
    """
    
    def __init__(self, value: Optional[str] = None):
        """
        Args:
            value: Session ID string. If None, generates a new UUID-based ID.
        """
        if value is None:
            # Generate new session ID with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self._value = f"user_{timestamp}_{uuid.uuid4().hex[:8]}"
        else:
            self._validate(value)
            self._value = value
    
    @staticmethod
    def _validate(value: str) -> None:
        """Validates session ID format"""
        if not isinstance(value, str):
            raise ValueError(f"SessionId must be string, got {type(value)}")
        if len(value) == 0:
            raise ValueError("SessionId cannot be empty")
        if len(value) > 255:
            raise ValueError("SessionId too long (max 255 chars)")
    
    @property
    def value(self) -> str:
        """Returns the session ID value"""
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"SessionId('{self._value}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SessionId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
