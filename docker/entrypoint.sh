#!/bin/bash
# Docker entrypoint script for LangChain DDD application

set -e

echo "=========================================="
echo "LangChain DDD Application - Docker Start"
echo "=========================================="
echo ""

# Display configuration
echo "Configuration:"
echo "  Database: $DATABASE_PATH"
echo "  Cache: $CACHE_FILE"
echo "  Knowledge Base: $KNOWLEDGE_BASE_PATH"
echo ""

# Initialize directories if they don't exist
mkdir -p /app/data /app/cache /app/logs

# Check if database needs initialization
if [ ! -f "$DATABASE_PATH" ]; then
    echo "Initializing database..."
    python << EOF
from src.infrastructure.persistence import SQLMessageRepository
repo = SQLMessageRepository("$DATABASE_PATH")
print("Database initialized successfully")
EOF
    echo ""
fi

# Verify imports
echo "Verifying application imports..."
python << EOF
try:
    from src.domain.entities import Message, Session, KnowledgeArticle
    from src.domain.value_objects import SessionId, MessageContent
    from src.domain.repositories import MessageRepository, KnowledgeRepository
    from src.application.services import ChatService, KnowledgeService, SecurityService
    from src.application.dtos import MessageDTO, SessionDTO, ResponseDTO
    from src.infrastructure.persistence import SQLMessageRepository
    from src.infrastructure.external import ResponseCache, OpenAILLMService
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
EOF

echo ""
echo "=========================================="
echo "Application Ready"
echo "=========================================="
echo ""

# Execute the main command
exec "$@"
