#!/bin/bash
# Build and run LangChain DDD application in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== LangChain DDD Docker Setup ===${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please update .env with your OpenAI API key${NC}"
    else
        cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
DATABASE_PATH=/app/data/chat_history.db
CACHE_FILE=/app/cache/response_cache.json
KNOWLEDGE_BASE_PATH=/app/knowledge_base.md
EOF
        echo -e "${YELLOW}Created basic .env file. Please update OPENAI_API_KEY${NC}"
    fi
fi

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p data cache logs

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

# Build image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -f docker/Dockerfile -t langchain-ddd:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Docker image built successfully${NC}\n"
else
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
fi

# Run container
echo -e "${YELLOW}Starting Docker container...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Container started successfully${NC}\n"
    echo -e "${GREEN}=== Container Running ===${NC}"
    docker-compose ps
    echo -e "\n${YELLOW}To interact with the application:${NC}"
    echo "docker-compose exec langchain-app python app.py"
    echo -e "\n${YELLOW}To view logs:${NC}"
    echo "docker-compose logs -f"
else
    echo -e "${RED}Failed to start container${NC}"
    exit 1
fi
