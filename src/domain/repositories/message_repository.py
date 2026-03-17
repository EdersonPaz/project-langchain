"""Message Repository - Abstract interface for message persistence"""

from abc import ABC, abstractmethod
from typing import List
from ..entities import Message
from ..value_objects import SessionId


class MessageRepository(ABC):
    """
    Repository interface for Message persistence.
    - Abstract interface (no implementation details)
    - Defines contract for message storage/retrieval
    - Implementation in infrastructure layer
    """
    
    @abstractmethod
    def add(self, message: Message) -> int:
        """
        Persist a message.
        
        Args:
            message: Message entity to save
            
        Returns:
            Message ID in database
        """
        pass
    
    @abstractmethod
    def get_by_session(self, session_id: SessionId, limit: int = 50) -> List[Message]:
        """
        Retrieve messages from a session.
        
        Args:
            session_id: Session to retrieve messages from
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        pass
    
    @abstractmethod
    def get_recent(self, session_id: SessionId, count: int = 5) -> List[Message]:
        """
        Retrieve recent messages from session.
        
        Args:
            session_id: Session ID
            count: Number of recent messages
            
        Returns:
            List of recent messages
        """
        pass
    
    @abstractmethod
    def delete_old(self, session_id: SessionId, keep_count: int = 20) -> int:
        """
        Delete old messages, keeping only recent ones.
        Useful for optimizing token usage.
        
        Args:
            session_id: Session ID
            keep_count: Number of messages to keep
            
        Returns:
            Number of deleted messages
        """
        pass
    
    @abstractmethod
    def clear_session(self, session_id: SessionId) -> int:
        """
        Clear all messages from a session.
        
        Args:
            session_id: Session to clear
            
        Returns:
            Number of deleted messages
        """
        pass
