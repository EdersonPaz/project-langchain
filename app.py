#!/usr/bin/env python3
"""
LangChain Assistant - DDD Architecture Edition

This is the main entry point for the application.
It initializes the DDD layers and starts the CLI interface.

Architecture:
  - Domain Layer: Core business logic and entities (src/domain/)
  - Application Layer: Use cases and services (src/application/)
  - Infrastructure Layer: Persistence and external services (src/infrastructure/)
  - Interfaces Layer: CLI, API, etc. (src/interfaces/)

Usage:
    python app.py

For more information, see ARCHITECTURE_DDD.md
"""

import sys
import asyncio
from src.interfaces.cli import main



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)

