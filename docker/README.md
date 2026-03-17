# Docker Setup - LangChain DDD Application

This directory contains Docker configuration files for containerizing the LangChain DDD application.

## Files

- **Dockerfile**: Multi-stage docker image definition
- **docker-compose.yml**: Orchestration for running the application
- **.dockerignore**: Files to exclude from Docker build context
- **build.sh**: Script to automate build and deployment

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- `.env` file with configuration

### 2. Build and Run

```bash
# Make build script executable (Linux/Mac)
chmod +x docker/build.sh

# Run the build script
./docker/build.sh

# Or manually build
docker-compose up -d
```

### 3. Interact with the Application

```bash
# Enter the container shell
docker-compose exec langchain-app bash

# Run the application
docker-compose exec langchain-app python app.py

# Run tests
docker-compose exec langchain-app pytest tests/ -v
```

## Environment Configuration

Create or update your `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
DATABASE_PATH=/app/data/chat_history.db
CACHE_FILE=/app/cache/response_cache.json
KNOWLEDGE_BASE_PATH=/app/knowledge_base.md
```

## Common Commands

### Viewing Logs
```bash
docker-compose logs -f langchain-app
```

### Stopping the Container
```bash
docker-compose down
```

### Rebuilding After Code Changes
```bash
docker-compose up -d --build
```

### Running Tests in Container
```bash
docker-compose exec langchain-app pytest tests/ -v --tb=short
```

### Accessing Interactive Shell
```bash
docker-compose exec langchain-app python
```

## Container Structure

```
/app/
├── src/              # Application source code (DDD architecture)
├── tests/            # Test suite
├── data/             # SQLite database (volume mounted)
├── cache/            # Response cache (volume mounted)
├── logs/             # Application logs (volume mounted)
├── app.py            # Entry point
└── requirements.txt  # Python dependencies
```

## Resource Limits

The container is configured with:
- **CPU Limit**: 2 cores
- **CPU Reserve**: 0.5 cores
- **Memory Limit**: 2GB
- **Memory Reserve**: 512MB

Adjust in `docker-compose.yml` as needed.

## Health Check

The container includes a health check that validates:
- Python environment is accessible
- DDD value objects can be instantiated

## Volumes

Three volumes are mounted to persist data:
- `./data`: Database storage
- `./cache`: Response cache
- `./logs`: Application logs

These directories are created automatically on first run.

## Port Mapping

- **Port 8000**: Reserved for future API server implementation

## Troubleshooting

### Container fails to start
```bash
docker-compose logs langchain-app
# Check if .env file exists and has valid OPENAI_API_KEY
```

### Database issues
```bash
# Clear and reinitialize
docker-compose exec langchain-app rm /app/data/chat_history.db
docker-compose restart langchain-app
```

### Permission issues with volumes
```bash
# Fix directory permissions
sudo chown -R $USER:$USER ./data ./cache ./logs
```

## Future Enhancements

- PostgreSQL integration (commented in docker-compose.yml)
- Redis caching layer
- API server with FastAPI
- Monitoring with Prometheus
- Log aggregation with ELK stack

## Production Considerations

For production deployment:

1. Use environment-specific `.env` files
2. Implement secrets management (AWS Secrets Manager, HashiCorp Vault)
3. Add resource monitoring and alerts
4. Configure container registry (Docker Hub, ECR, GCR)
5. Implement CI/CD pipeline for automated builds
6. Add load balancing and auto-scaling
7. Configure logging and monitoring

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/build-images/)
