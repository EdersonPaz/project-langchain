# Executar sem Docker (Local)

## Windows (Rápido)

```powershell
# 1. Execute o script de inicialização
.\run-local.bat

# Ele irá:
# - Criar virtual environment
# - Instalar dependências
# - Verificar imports
# - Rodar a aplicação
```

## Linux / Mac

```bash
# 1. Torne o script executável
chmod +x run-local.sh

# 2. Execute
./run-local.sh
```

## Passo a Passo Manual

Se os scripts não funcionarem:

### 1. Criar Virtual Environment
```powershell
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Criar arquivo .env
```bash
# Crie um arquivo .env com:
OPENAI_API_KEY=sk-your-key-here
DATABASE_PATH=chat_history.db
CACHE_FILE=response_cache.json
```

### 4. Verificar Imports
```bash
python -c "from src.domain.entities import Message; print('OK')"
```

### 5. Executar a Aplicação
```bash
# CLI padrão
python app.py --mode cli

# API FastAPI (desenvolvimento)
python app.py --mode api

# Ou com uvicorn (recomendado para produção local):
uvicorn src.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_app.py -v

# Com coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Próximos Passos

Quando Docker estiver instalado, use:
```bash
# Build image
docker build -f docker/Dockerfile -t langchain-ddd:latest .

# Rodar container
docker-compose up -d

# Interagir
docker-compose exec langchain-app python app.py
```

---

## Troubleshooting

### "Python não encontrado"
- Instale Python 3.11+ de https://www.python.org
- Ou use `python3` em vez de `python`

### "ModuleNotFoundError"
```bash
# Certifique-se que venv está ativado:
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Depois instale novamente:
pip install -r requirements.txt
```

### "OpenAI API key error"
- Atualize o arquivo `.env` com uma chave válida
- Ou defina variável de ambiente:
```bash
# Windows
set OPENAI_API_KEY=sk-your-key

# Linux/Mac
export OPENAI_API_KEY=sk-your-key
```

---

**Quer instalar Docker?** Veja `DOCKER_SETUP.md`
