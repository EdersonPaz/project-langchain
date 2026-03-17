@echo off
REM Run LangChain DDD Application without Docker (Windows)

echo.
echo ======================================
echo LangChain DDD - Local Execution
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3.11+ is not installed or not in PATH
    echo Please install Python from https://www.python.org
    exit /b 1
)

echo Checking Python installation...
python --version

REM Check if virtual environment exists
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo.
    echo Creating .env file...
    (
        echo OPENAI_API_KEY=sk-your-key-here
        echo DATABASE_PATH=chat_history.db
        echo CACHE_FILE=response_cache.json
        echo KNOWLEDGE_BASE_PATH=knowledge_base.md
    ) > .env
    echo Please update .env with your OpenAI API key
)

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies
    exit /b 1
)

echo Dependencies installed successfully
echo.

REM Verify imports
echo Verifying application imports...
python -c "from src.domain.entities import Message, Session; print('- Domain entities OK')" || exit /b 1
python -c "from src.application.services import ChatService; print('- Application services OK')" || exit /b 1
python -c "from src.infrastructure.persistence import SQLMessageRepository; print('- Infrastructure OK')" || exit /b 1

echo.
echo ======================================
echo Running LangChain DDD Application
echo ======================================
echo.

REM Guarantee docs folder exists and keep root clean
if not exist docs mkdir docs
for %%f in (RUN_LOCAL.md DOCKER_SETUP.md PROJECT_MAP.md OPTIMIZATION_RESULTS.md ARCHITECTURE_DDD.md TESTING_SCENARIOS.md TESTING_STRUCTURE.md TESTING_SUMMARY.md SYSTEM_PROMPT_RESTORED.md README-new.md) do (
    if exist %%f move /Y %%f docs\
)

REM Run the application
python app.py

REM Move any generated docs to docs/ and clean root
if not exist docs mkdir docs
for %%f in (RUN_LOCAL.md DOCKER_SETUP.md PROJECT_MAP.md OPTIMIZATION_RESULTS.md ARCHITECTURE_DDD.md TESTING_SCENARIOS.md TESTING_STRUCTURE.md TESTING_SUMMARY.md SYSTEM_PROMPT_RESTORED.md README-new.md) do (
    if exist %%f move /Y %%f docs\
)

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat
