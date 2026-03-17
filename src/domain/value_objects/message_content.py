"""MessageContent Value Object - Represents message text with validation"""

from typing import Optional


class MessageContent:
    """
    Value Object representing message content.
    - Immutable
    - Validates content safety (no API keys, no dangerous code)
    - Handles text normalization
    """
    
    MAX_LENGTH = 10000
    DANGEROUS_PATTERNS = ["sk-", "api_key=", "password=", "eval(", "exec(", "os.system"]
    
    def __init__(self, value: str):
        """
        Args:
            value: Message content text
            
        Raises:
            ValueError: If content is invalid or contains dangerous patterns
        """
        self._validate(value)
        self._value = value.strip()
    
    @classmethod
    def _validate(cls, value: str) -> None:
        """Validates message content"""
        if not isinstance(value, str):
            raise ValueError(f"Content must be string, got {type(value)}")
        
        if len(value.strip()) == 0:
            raise ValueError("Content cannot be empty")
        
        if len(value) > cls.MAX_LENGTH:
            raise ValueError(f"Content too long (max {cls.MAX_LENGTH} chars)")
        
        # Security checks
        value_lower = value.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in value_lower:
                raise ValueError(f"Content contains dangerous pattern: {pattern}")
    
    @property
    def value(self) -> str:
        """Returns the message content"""
        return self._value
    
    @property
    def length(self) -> int:
        """Returns content length"""
        return len(self._value)
    
    @property
    def is_empty(self) -> bool:
        """Checks if content is empty"""
        return len(self._value.strip()) == 0
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        preview = self._value[:50] + "..." if len(self._value) > 50 else self._value
        return f"MessageContent('{preview}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, MessageContent):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
