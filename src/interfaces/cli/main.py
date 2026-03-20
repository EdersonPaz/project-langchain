"""CLI Main Interface - User-facing command-line interface"""

import sys
from datetime import datetime
from typing import Optional
from openai import RateLimitError

# Imports from DDD layers
from ...infrastructure.config import Settings
from ...infrastructure.persistence import SQLMessageRepository, LocalTextKnowledgeRepository
from ...infrastructure.external import OpenAILLMService, ResponseCache, SemanticCache
from ...application.services import ChatService, KnowledgeService, SecurityService
from ...domain.value_objects import SessionId
from ...domain.entities import Message
from ...domain.value_objects import MessageContent


class ChatCLI:
    """
    Command-line interface for the chat assistant.
    - Handles user interaction
    - Orchestrates services
    - Manages conversation loop
    """
    
    def __init__(self):
        # Load configuration
        Settings.validate()
        
        # Initialize infrastructure layer
        self.message_repo = SQLMessageRepository(Settings.DB_PATH)
        self.knowledge_repo = LocalTextKnowledgeRepository(Settings.KNOWLEDGE_BASE_FILE)

        # Use semantic cache when enabled, fall back to MD5 cache otherwise
        if Settings.USE_SEMANTIC_CACHE:
            self.cache = SemanticCache(
                persist_dir=Settings.SEMANTIC_CACHE_DIR,
                threshold=Settings.SEMANTIC_CACHE_THRESHOLD
            )
            if not self.cache.is_ready():
                print("[WARNING] Falling back to MD5 cache (install chromadb + sentence-transformers)")
                self.cache = ResponseCache(Settings.CACHE_FILE)
        else:
            self.cache = ResponseCache(Settings.CACHE_FILE)

        self.llm_service = OpenAILLMService(
            model=Settings.OPENAI_MODEL,
            temperature=Settings.OPENAI_TEMPERATURE
        )
        
        # Initialize application services
        self.chat_service = ChatService(
            message_repo=self.message_repo,
            knowledge_repo=self.knowledge_repo,
            model=Settings.OPENAI_MODEL,
            temperature=Settings.OPENAI_TEMPERATURE,
            db_path=Settings.DB_PATH
        )
        
        self.knowledge_service = KnowledgeService(self.knowledge_repo)
        self.security_service = SecurityService()
        
        # Current session
        self.session_id = SessionId()
    
    def print_welcome(self):
        """Print welcome message"""
        print("=" * 70)
        print("[AI] LangChain Assistant - DDD Architecture Edition")
        print("=" * 70)
        print(f"[OK] Model: {Settings.OPENAI_MODEL}")
        print(f"[OK] RAG: {'Enabled' if Settings.USE_RAG else 'Disabled'}")
        cache_type = "Semantic (ChromaDB)" if isinstance(self.cache, SemanticCache) and self.cache.is_ready() else "MD5 (JSON)"
        print(f"[OK] Cache: {cache_type} - {self.cache.size()} responses cached")
        print(f"[DB] Database: {Settings.DB_PATH}")
        print("=" * 70)
        print("\\nCommands:")
        print("  'help'      - Show available commands")
        print("  'new'       - Start new session")
        print("  'history'   - View session history")
        print("  'cache'     - Show cache status")
        print("  'clear'     - Clear current session")
        print("  'exit'      - Exit application")
        print("=" * 70 + "\\n")
    
    def print_help(self):
        """Print help message"""
        help_text = """
Available Commands:
  
  help              Show this help message
  new               Start a new conversation session
  history [count]   View conversation history (default: 10 messages)
  cache             Show cache statistics  
  cache clear       Clear all cached responses
  clear             Clear current session messages
  debug             Toggle debug mode
  models            Show available models
  exit / quit       Exit the application

Tips:
  - Type 'help' anytime for commands
  - Questions are automatically cached for performance
  - Your conversation is persistent in the database
  - Type 'Ctrl+C' to interrupt long responses
"""
        print(help_text)
    
    def print_history(self, count: int = 10):
        """Print conversation history"""
        messages = self.message_repo.get_by_session(SessionId(self.session_id.value), limit=count)
        
        if not messages:
            print("\\nNo messages in this session yet.\\n")
            return

        print(f"\\nConversation History ({len(messages)} messages):")
        print("-" * 70)
        
        for msg in messages:
            prefix = "[You]" if msg.message_type == "human" else "[AI]"
            preview = msg.content.value[:60] + "..." if msg.content.length > 60 else msg.content.value
            timestamp = msg.created_at.strftime("%H:%M:%S")
            print(f"{prefix} [{timestamp}] {preview}")
        
        print("-" * 70 + "\\n")
    
    def process_command(self, user_input: str) -> bool:
        """
        Process special commands.
        Returns True if command was processed, False if it's a regular question.
        """
        cmd = user_input.strip().lower()
        
        if cmd in ["help", "?"]:
            self.print_help()
            return True
        
        if cmd == "new":
            self.session_id = SessionId()
            print(f"[NEW] Session started: {self.session_id}\\n")
            return True
        
        if cmd.startswith("history"):
            count = 10
            if " " in cmd:
                try:
                    count = int(cmd.split()[1])
                except ValueError:
                    count = 10
            self.print_history(count)
            return True
        
        if cmd == "cache":
            size = self.cache.size()
            print(f"\\n[CACHE] Status: {size} responses cached\\n")
            return True
        
        if cmd == "cache clear":
            self.cache.clear()
            print("\\n[CACHE] Cleared!\\n")
            return True
        
        if cmd == "clear":
            count = self.message_repo.clear_session(SessionId(self.session_id.value))
            print(f"\\n[CLEAR] Removed {count} messages from this session\\n")
            return True
        
        if cmd == "models":
            print("\\nAvailable Models (by cost):")
            for model, info in OpenAILLMService.MODELS.items():
                tier = info["tier"].upper()
                input_cost = info["cost_per_1m_input"]
                output_cost = info["cost_per_1m_output"]
                print(f"  {model:20} [{tier:10}] \${input_cost}/M in, \${output_cost}/M out")
            print()
            return True
        
        if cmd in ["exit", "quit", "bye", "sair"]:
            return None  # Signal to exit
        
        return False  # Not a command
    
    async def run_conversation(self):
        """Main conversation loop"""
        self.print_welcome()
        
        while True:
            try:
                user_input = input("\\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command
                result = self.process_command(user_input)
                if result is None:
                    print("\\n[EXIT] Goodbye!\\n")
                    break
                if result:  # Command was processed
                    continue
                
                # Validate input for security
                is_valid, error_msg = self.security_service.validate_input(user_input)
                if not is_valid:
                    print(f"\\n[WARNING] {error_msg}\\n")
                    continue
                
                # Check cache
                cached_response = self.cache.get(user_input)
                if cached_response:
                    print(f"\\n[AI] (from cache): {cached_response}\\n")
                    continue
                
                # Get response from chat service
                try:
                    response_dto = await self.chat_service.ask(
                        query=user_input,
                        session_id=self.session_id.value,
                        use_context=Settings.USE_RAG
                    )
                    
                    source = response_dto.metadata.get("source", "openai")
                    print(f"\\n[AI] ({source}): {response_dto.content}\\n")
                    
                    # Cache the response
                    if Settings.ENABLE_RESPONSE_CACHE:
                        self.cache.set(user_input, response_dto.content)
                    
                    # Optimize history (delete old messages)
                    self.message_repo.delete_old(
                        SessionId(self.session_id.value),
                        keep_count=Settings.MAX_HISTORY_MESSAGES
                    )
                
                except RateLimitError:
                    print("\\n[WARNING] OpenAI Rate Limit Reached")
                    print("Visit: https://platform.openai.com/account/billing\\n")
            
            except KeyboardInterrupt:
                print("\\n\\n[EXIT] Interrupted by user!\\n")
                break
            
            except Exception as e:
                print(f"\\n[ERROR] {e}\\n")


def main():
    """Entry point for CLI"""
    import asyncio
    
    cli = ChatCLI()
    try:
        asyncio.run(cli.run_conversation())
    except KeyboardInterrupt:
        print("\\n\\n👋 Goodbye!\\n")
