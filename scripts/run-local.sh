#!/bin/bash
# Run LangChain DDD Application without Docker (Linux/Mac)

set -e

echo ""
echo "======================================"
echo "LangChain DDD - Local Execution"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3.11+ is not installed"
    echo "Please install Python from https://www.python.org"
    exit 1
fi

echo "Checking Python installation..."
python3 --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
DATABASE_PATH=chat_history.db
CACHE_FILE=response_cache.json
KNOWLEDGE_BASE_PATH=knowledge_base.md
EOF
    echo "Please update .env with your OpenAI API key"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Dependencies installed successfully"
echo ""

# Verify imports
echo "Verifying application imports..."
python -c "from src.domain.entities import Message, Session; print('- Domain entities OK')" || exit 1
python -c "from src.application.services import ChatService; print('- Application services OK')" || exit 1
python -c "from src.infrastructure.persistence import SQLMessageRepository; print('- Infrastructure OK')" || exit 1

echo ""
echo "======================================"
echo "Running LangChain DDD Application"
echo "======================================"
echo ""

# Run the application
python app.py

# Deactivate virtual environment on exit
deactivate
