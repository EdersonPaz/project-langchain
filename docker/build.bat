@echo off
rem Build and run LangChain DDD application in Docker (Windows)

setlocal enabledelayedexpansion

echo.
echo === LangChain DDD Docker Setup ===
echo.

rem Check if .env file exists
if not exist .env (
    echo Error: .env file not found
    echo Creating .env from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo Please update .env with your OpenAI API key
    ) else (
        (
            echo OPENAI_API_KEY=sk-your-key-here
            echo DATABASE_PATH=/app/data/chat_history.db
            echo CACHE_FILE=/app/cache/response_cache.json
            echo KNOWLEDGE_BASE_PATH=/app/knowledge_base.md
        ) > .env
        echo Created basic .env file. Please update OPENAI_API_KEY
    )
) else (
    echo .env file found
)

rem Create required directories
echo.
echo Creating required directories...
if not exist data mkdir data
if not exist cache mkdir cache
if not exist logs mkdir logs

rem Build image
echo.
echo Building Docker image...
docker build -f docker/Dockerfile -t langchain-ddd:latest .

if %ERRORLEVEL% neq 0 (
    echo Failed to build Docker image
    exit /b 1
)

echo Docker image built successfully
echo.

rem Run container
echo.
echo Starting Docker container...
docker-compose up -d

if %ERRORLEVEL% neq 0 (
    echo Failed to start container
    exit /b 1
)

echo Container started successfully
echo.
echo === Container Running ===
docker-compose ps
echo.
echo To interact with the application:
echo   docker-compose exec langchain-app python app.py
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop the container:
echo   docker-compose down
echo.

endlocal
