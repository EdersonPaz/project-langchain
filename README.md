# Assistente LangChain com Persistência e RAG

## 1. Descrição

Este projeto implementa um assistente de linha de comando (CLI) e API REST
utilizando **LangChain, OpenAI e Retrieval Augmented Generation (RAG)**,
seguindo arquitetura **Domain-Driven Design (DDD)**.

O assistente:
- ✅ **Mantém histórico persistente** em SQLite (não apaga ao fechar!)
- ✅ **Integra base de conhecimento** com busca por palavras-chave (sem custo de API)
- ✅ **Cache semântico** com ChromaDB + sentence-transformers (reduz chamadas ao LLM em até 70%)
- ✅ **Responde em português** com contexto relevante
- ✅ **Valida código Python** quanto a riscos de segurança
- ✅ **Detecta dados sensíveis** (chaves de API)
- ✅ **API REST FastAPI** com endpoints `/health`, `/sessions`, `/chat`, `/history`

## 2. Requisitos

- **Python 3.11+**
- **Conta OpenAI** com créditos ativos
- **Bibliotecas necessárias** (ver requirements.txt)

### Dependências

```
langchain-core >= 0.3, < 0.4
langchain-openai >= 0.3, < 0.4
langchain-community >= 0.3, < 0.4
python-dotenv >= 1.0, < 2.0
sqlalchemy >= 2.0, < 3.0

# Cache semântico (embeddings locais — sem custo de API)
chromadb >= 0.5, < 1.0
sentence-transformers >= 3.0, < 4.0
```

## 3. Configuração

### Passo 1: Instalar dependências

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Passo 2: Criar arquivo `.env`

Na raiz do projeto, crie um arquivo `.env`:

```env
OPENAI_API_KEY=sk-sua-chave-aqui

# Configurações opcionais (valores padrão abaixo)
LANGCHAIN_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.5
USE_RAG=true
ENABLE_RESPONSE_CACHE=true

# Cache semântico
USE_SEMANTIC_CACHE=true
SEMANTIC_CACHE_DIR=cache/semantic_cache
SEMANTIC_CACHE_THRESHOLD=0.90
```

⚠️ **Nunca compartilhe sua chave de API!**

## 4. Execução (Local)

> Nota: o projeto mantém toda documentação gerada em `docs/`.
> Se aparecer `README-new.md`, `RUN_LOCAL.md`, etc. na raiz, o script `run-local` já move automaticamente para `docs/`.

1. Ative seu virtual environment e instale dependências, ou use `scripts/run-local.bat` / `scripts/run-local.sh`:

Windows:
```powershell
scripts\run-local.bat
```

Linux/macOS:
```bash
chmod +x run-local.sh && ./run-local.sh
```

2. Alternativa manual:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
# Executar em modo CLI
python app.py --mode cli
```

### API FastAPI

```bash
python app.py --mode api
# Ou com uvicorn:
uvicorn src.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

### API via Docker

```bash
docker build -t project-langchain:latest .
docker run -d --name project-langchain-container -p 8000:8000 project-langchain:latest
```

### Comandos disponíveis (CLI):

| Comando | Descrição |
|---------|-----------|
| `sair` | Encerra o assistente |
| `limpar` | Inicia uma nova sessão de conversa |
| `historico` | Mostra o histórico da sessão atual |
| Qualquer outra entrada | Envia pergunta ao assistente |

> Docker é opcional e permanece disponível em `docker/` caso queira containerizar o app posteriormente.
## 5. Funcionalidades

### 🗄️ Persistência de Histórico

O histórico é salvo em um banco SQLite (`chat_history.db`):

- **Não apaga** ao fechar o programa
- **Organizado por sessão** (session_id)
- **Timestamps** para cada mensagem
- **Recuperável** via comando `historico`
- **Auto-limpeza**: mantém apenas as últimas N mensagens (configurável)

```
chat_history.db (criado automaticamente)
```

### 📚 Base de Conhecimento com RAG (sem custo)

A aplicação carrega `knowledge_base.md` usando busca por palavras-chave local:

1. **Carregamento**: Arquivo dividido em seções (`##`)
2. **Busca**: Matching de palavras-chave — **sem embeddings, sem custo de API**
3. **Recuperação**: Top-3 seções mais relevantes por pergunta
4. **Injeção**: Contexto automaticamente adicionado ao prompt

```
CONTEXTO DA BASE DE CONHECIMENTO:
- Seção 1 mais relevante
- Seção 2 mais relevante
- Seção 3 mais relevante
```

### 🧠 Cache Semântico (novo)

Evita chamadas repetidas ao LLM com busca por similaridade semântica:

- **ChromaDB** persistido em disco (`cache/semantic_cache/`)
- **Embeddings locais** via `sentence-transformers` (modelo multilíngue português)
- **Threshold configurável** (padrão: 90% de similaridade)
- **Fallback automático** para cache MD5 se ChromaDB não estiver disponível
- **Hit rate estimado**: 50-70% em uso real (vs. 15-20% do cache MD5)

| Pergunta | Cache MD5 | Cache Semântico |
|---|---|---|
| "Como criar uma chain?" (exato) | HIT | HIT |
| "Como faço uma chain?" (similar) | MISS | HIT |
| "Como construir uma chain?" (similar) | MISS | HIT |

## 6. Funcionamento Interno

### Fluxo de Uma Pergunta

```
1. Usuário digita pergunta
      ↓
2. Validação de segurança (SecurityService)
      ↓
3. Cache semântico (SemanticCache / ResponseCache)
   → HIT: retorna resposta sem chamar LLM (zero tokens)
   → MISS: continua
      ↓
4. Busca por palavras-chave na base (RAG local, sem custo)
      ↓
5. Injeta histórico + contexto no prompt
      ↓
6. OpenAI gera resposta
      ↓
7. Armazena no cache semântico
      ↓
8. Resposta exibida e salva em SQLite
      ↓
9. Ciclo continua
```

### Componentes Principais

| Componente | Função |
|-----------|--------|
| `ChatOpenAI` | Modelo LLM (gpt-3.5-turbo padrão) |
| `SQLChatMessageHistory` | Persistência de histórico em SQLite |
| `LocalTextKnowledgeRepository` | Busca por palavras-chave na KB (sem custo) |
| `SemanticCache` | Cache semântico com ChromaDB + sentence-transformers |
| `ResponseCache` | Cache MD5 em JSON (fallback) |
| `SecurityService` | Validação de entrada e detecção de padrões perigosos |
| `ChatService` | Orquestração de LLM, RAG e histórico |

## 7. Estrutura do Banco de Dados

```sql
CREATE TABLE IF NOT EXISTS message_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    message_type TEXT NOT NULL,
    message_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Exemplo de Dados

```
session_id: user_20260316
message_type: human | ai
message_content: "Qual é a diferença entre..."
created_at: 2026-03-16 14:30:45
```

## 8. Segurança

✅ **Validações implementadas:**

- ✔️ Verifica se OPENAI_API_KEY está configurada
- ✔️ Detecta strings começadas com "sk-" (API keys)
- ✔️ Alerta para uso de `eval()`, `exec()`, `os.system` em código
- ✔️ Nunca monitora terminal (apenas prompts + respostas)

## 9. Limitações Atuais

- ⚠️ Base de conhecimento carregada em memória (OK até ~100MB)
- ⚠️ Sem streaming de respostas (aguarda completar)
- ⚠️ Sem autenticação de usuários
- ⚠️ Sem limite de requisições (respeite quotas OpenAI!)
- ⚠️ ChromaDB pode ser bloqueado por políticas de controle de aplicativos (Windows) — fallback automático para cache MD5

## 10. Possíveis Melhorias

- [x] Cache semântico com ChromaDB + embeddings locais
- [x] API REST com FastAPI
- [x] RAG sem custo de API (busca por palavras-chave)
- [ ] LLM local com Ollama (custo zero)
- [ ] Sumarização automática de histórico longo
- [ ] Suporte a múltiplos usuários (autenticação)
- [ ] Streaming de respostas
- [ ] Ingestão de arquivos adicionais (PDF, DOCX)
- [ ] Dashboard de métricas de uso e custo
- [ ] Exportar histórico (JSON/CSV)
- [ ] Interface web (Streamlit/Gradio)

## 11. Ambiente de Teste

```
Sistema operacional: Windows / Linux / macOS
Python: 3.11.x
Execução: Terminal local
Tempo de startup: ~2-3s (carregamento de embeddings)
```

## 12. Estrutura do Projeto

```
project-langchain/
├── app.py                    # Entry point (CLI + API)
├── src/
│   ├── domain/               # Entidades, Value Objects, Repositórios abstratos
│   ├── application/          # Services (ChatService, KnowledgeService, SecurityService)
│   ├── infrastructure/
│   │   ├── config/           # Settings (lê .env)
│   │   ├── persistence/      # SQLite e busca local na KB
│   │   └── external/
│   │       ├── openai_llm_service.py
│   │       ├── response_cache.py    # Cache MD5 (fallback)
│   │       └── semantic_cache.py    # Cache semântico (ChromaDB)
│   └── interfaces/
│       ├── cli/              # Interface de linha de comando
│       └── api/              # FastAPI (endpoints REST)
├── tests/
│   ├── conftest.py           # Fixtures compartilhadas
│   ├── test_app.py           # 25 testes da aplicação
│   ├── test_api.py           # 5 testes da API REST
│   ├── test_performance.py   # 14 testes de performance
│   ├── test_security.py      # 27 testes de segurança
│   └── test_semantic_cache.py # 17 testes do cache semântico
├── knowledge_base.md         # Base de conhecimento para RAG
├── requirements.txt          # Dependências Python
├── .env                      # Variáveis de ambiente (não commitar!)
├── chat_history.db           # Banco SQLite (criado automaticamente)
├── cache/
│   ├── response_cache.json   # Cache MD5 persistido
│   └── semantic_cache/       # ChromaDB (criado automaticamente)
├── scripts/                  # Scripts de execução e manutenção
├── docs/                     # Documentação técnica
└── README.md                 # Este arquivo
```

## 13. Docker

O projeto agora usa um único arquivo de Dockerfile consolidado em `docker/Dockerfile` (build multi-stage, healthcheck e entrypoint). O Dockerfile raiz foi removido para evitar inconsistências.

### Build usando o Dockerfile consolidado

```bash
docker build -f docker/Dockerfile -t project-langchain:latest .
```

### Executar container

```bash
docker run -d --name project-langchain-container -p 8000:8000 project-langchain:latest
```

### Parar/Remover

```bash
docker stop project-langchain-container && docker rm project-langchain-container
```

## 14. Exemplos de Uso

### Exemplo 1: Fazer uma pergunta

```
Você: O que é LangChain?
📚 [buscando na base de conhecimento...]

Assistente: LangChain é um framework para desenvolver aplicações 
impulsionadas por modelos de linguagem grandes (LLMs). 
Ele fornece componentes reutilizáveis...
```

### Exemplo 2: Ver histórico

```
Você: historico

📋 Histórico da sessão: user_20260316

--------------------------------------------------------------
[2026-03-16 14:30:45] human: O que é LangChain?
[2026-03-16 14:31:02] ai: LangChain é um framework para...
[2026-03-16 14:32:15] human: Como usar FAISS?
[2026-03-16 14:32:45] ai: FAISS é uma biblioteca para...
--------------------------------------------------------------
```

### Exemplo 3: Iniciar nova sessão

```
Você: limpar
🔄 Nova sessão iniciada: user_20260316_143000

Você: (novo histórico cria a partir daqui)
```

## 14. Troubleshooting

### ❌ "knowledge_base.md não encontrado"
O arquivo já existe no projeto. Certifique-se de que está na raiz.

### ❌ "RateLimitError"
Você atingiu o limite de requisições da OpenAI.
Verifique: https://platform.openai.com/account/billing

### ❌ "[SemanticCache] WARNING: failed to initialize"
O ChromaDB não pôde ser carregado (ex: bloqueio por política do sistema no Windows).
O cache MD5 (JSON) será usado automaticamente como fallback — a aplicação funciona normalmente.
Para habilitar o cache semântico, ajuste as permissões ou use Linux/macOS/Docker.

### ❌ "OPENAI_API_KEY is not configured"
Certifique-se de que:
- ✓ O arquivo `.env` existe na raiz do projeto
- ✓ A variável `OPENAI_API_KEY=sk-...` está configurada corretamente
- ✓ Você tem créditos disponíveis na OpenAI

## 15. Links Úteis

- 📖 [LangChain Docs](https://python.langchain.com)
- 🤖 [OpenAI API](https://platform.openai.com)
- 🧠 [ChromaDB](https://docs.trychroma.com)
- 🤗 [sentence-transformers](https://www.sbert.net)
- 🐍 [Python Docs](https://docs.python.org/3.11/)

