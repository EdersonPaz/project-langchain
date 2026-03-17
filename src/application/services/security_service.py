"""Security Service - Validates inputs and detects security issues"""

from typing import Optional


class SecurityService:
    """
    Application service for security validation.
    - Input validation and sanitization
    - Malicious code detection
    - API key and secret detection
    """
    
    DANGEROUS_PATTERNS = {
        "eval(": "Code execution via eval()",
        "exec(": "Code execution via exec()",
        "os.system": "Shell command execution",
        "__import__": "Dynamic module import",
        "compile(": "Code compilation",
        "globals(": "Global namespace access",
        "locals(": "Local namespace access"
    }
    
    SECRET_PATTERNS = {
        "sk-": "OpenAI API key pattern",
        "api_key=": "API key assignment",
        "password=": "Password assignment",
        "secret=": "Secret token assignment",
        "token=": "Token assignment"
    }
    
    @classmethod
    def validate_input(cls, text: str) -> tuple[bool, Optional[str]]:
        """
        Validate input for security issues.
        
        Args:
            text: Input to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for secrets
        text_lower = text.lower()
        for pattern, description in cls.SECRET_PATTERNS.items():
            if pattern in text_lower:
                return False, f"⚠️ Detected potential secret ({description}): {pattern}"
        
        # Check for dangerous code patterns
        for pattern, description in cls.DANGEROUS_PATTERNS.items():
            if pattern in text_lower:
                return False, f"⚠️ Detected dangerous pattern ({description}): {pattern}"
        
        return True, None
    
    @classmethod
    def analyze_code(cls, code: str) -> dict:
        """
        Analyze code for security issues.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        code_lower = code.lower()
        
        for pattern, description in cls.DANGEROUS_PATTERNS.items():
            if pattern in code_lower:
                issues.append({
                    "severity": "High",
                    "pattern": pattern,
                    "description": description
                })
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "safe": len(issues) == 0
        }
    
    @classmethod
    def sanitize_chat_input(cls, text: str) -> str:
        """Sanitize user chat input"""
        # Remove control characters
        text = "".join(char for char in text if char.isprintable() or char in "\n\r\t")
        
        # Strip whitespace
        text = text.strip()
        
        return text
