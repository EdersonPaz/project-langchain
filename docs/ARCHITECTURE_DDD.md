# 🏗️ Arquitetura DDD - LangChain Assistant

## 📋 Overview

O projeto foi refatorado usando **Domain-Driven Design (DDD)** para melhorar escalabilidade, testabilidade e manutenibilidade.

**Status:** ✅ Implementação completa

---

## 🎯 Estrutura de Diretórios

```
project-langchain/
├── src/
│   ├── domain/                    # 🔵 DOMAIN LAYER
│   │   ├── entities/              # Objetos com identidade
│   │   │   ├── message.py         # Message entity
│   │   │   ├── session.py         # Session entity
│   │   │   └── knowledge_article.py
│   │   ├── repositories/          # Interfaces abstratas
│   │   │   ├── message_repository.py
│   │   │   └── knowledge_repository.py
│   │   └── value_objects/         # Objetos imutáveis
│   │       ├── session_id.py      # SessionId value object
│   │       └── message_content.py # MessageContent value object
│   │
│   ├── application/               # 🟢 APPLICATION LAYER
│   │   ├── dtos/                  # Data Transfer Objects
│   │   │   ├── message_dto.py
│   │   │   ├── session_dto.py
│   │   │   └── response_dto.py
│   │   ├── services/              # Application Services
│   │   │   ├── chat_service.py    # Orquestração de chat
│   │   │   ├── knowledge_service.py
│   │   │   └── security_service.py
│   │   └── use_cases/             # Use Cases (lógica de negócio)
│   │       ├── ask_question.py
│   │       ├── manage_session.py
│   │       └── retrieve_context.py
│   │
│   ├── infrastructure/            # 🟡 INFRASTRUCTURE LAYER
│   │   ├── config/                # Configuração centralizada
│   │   │   └── settings.py        # Settings & environment
│   │   ├── persistence/           # Implementações de repository
│   │   │   ├── sql_message_repository.py
│   │   │   └── local_text_knowledge_repository.py
│   │   └── external/              # Serviços externos
│   │       ├── openai_llm_service.py
│   │       ├── response_cache.py      # Cache MD5 JSON (fallback)
│   │       └── semantic_cache.py      # Cache semântico ChromaDB
│   │
│   └── interfaces/                # 🔴 INTERFACES LAYER
│       ├── cli/                   # Command-line interface
│       │   └── main.py            # CLI entry point
│       └── api/                   # FastAPI REST
│           └── main.py            # Endpoints /health /sessions /chat /history
│
├── tests/                         # 📝 Testes automatizados
│   ├── conftest.py                # Fixtures compartilhadas
│   ├── test_app.py                # 25 testes da aplicação
│   ├── test_api.py                # 5 testes da API REST
│   ├── test_performance.py        # 14 testes de performance
│   ├── test_security.py           # 27 testes de segurança
│   └── test_semantic_cache.py     # 17 testes do cache semântico
│
├── scripts/                       # 🛠️ Utilitários
├── docker/                        # 🐳 Docker config
├── docs/                          # 📚 Documentação
├── app.py                         # ✨ Entry point (novo)
└── requirements.txt
```

---

## 🎓 Conceitos DDD Aplicados

### 1. **Domain Layer (Camada de Domínio)**
Define a lógica de negócio central - o "coração" da aplicação.

#### Entities (Entidades)
- `Message` - Representa uma mensagem única com identidade
- `Session` - Representa uma sessão de conversa
- `KnowledgeArticle` - Representa um artigo da base de conhecimento

```python
# Exemplo: Message entity
message = Message(
    session_id=SessionId("user_20240316"),
    content=MessageContent("Olá!"),
    message_type="human"
)
```

#### Value Objects (Objetos de Valor)
- `SessionId` - ID único e imutável de sessão
- `MessageContent` - Conteúdo de mensagem com validação

**Características:**
- ✅ Imutáveis (não mudam após criação)
- ✅ Validação embutida
- ✅ Comparáveis por valor

```python
# Exemplo: SessionId VO
sid1 = SessionId()  # Gera novo ID
sid2 = SessionId("user_123")  # Específico

assert sid1 != sid2
```

#### Repositories (Interfaces Abstratas)
- `MessageRepository` - Interface para armazenar/recuperar mensagens
- `KnowledgeRepository` - Interface para buscar na base de conhecimento

**Princípio**: Abstrath o "como armazenar" - o Domain não conhece SQLite/FAISS

```python
# Exemplo: Interface
class MessageRepository(ABC):
    @abstractmethod
    def add(self, message: Message) -> int: pass
    @abstractmethod
    def get_by_session(self, session_id: SessionId) -> List[Message]: pass
```

### 2. **Application Layer (Camada de Aplicação)**
Orquestra os componentes do domínio - coordena o fluxo.

#### DTOs (Data Transfer Objects)
- `MessageDTO` - Transporta dados de Message entre camadas
- `ResponseDTO` - Transporta resposta da LLM
- `SessionDTO` - Transporta dados de session

**Por que:** Desacoplar representação interna de transporte

```python
# Exemplo: DTO
message_dto = MessageDTO.from_dict({
    "session_id": "user_123",
    "content": "Seu conteúdo",
    "message_type": "human"
})
```

#### Application Services
- `ChatService` - Orquestra integração LLM + histórico
- `KnowledgeService` - Gerencia base de conhecimento
- `SecurityService` - Valida inputs, detecta padrões perigosos

```python
# Exemplo: Service
chat_service = ChatService(
    message_repo=repo,
    knowledge_repo=kb_repo
)
response = await chat_service.ask(
    query="O que é LangChain?",
    session_id="user_123"
)
```

#### Use Cases (Serão implementados)
- `AskQuestionUseCase` - Pergunta uma questão
- `ManageSessionUseCase` - Cria/gerencia sessões
- `RetrieveContextUseCase` - Busca contexto na KB

### 3. **Infrastructure Layer (Camada de Infraestrutura)**
Implementa detalhes técnicos - como armazenar,integrar com APIs.

#### Configuration (`settings.py`)
```python
Settings.OPENAI_MODEL = "gpt-3.5-turbo"  # Centralizadamente
Settings.DB_PATH = "chat_history.db"
Settings.USE_RAG = True
```

#### Persistence (Repositórios Concretos)
- `SQLMessageRepository` - Implementação SQLite do MessageRepository
- `LocalTextKnowledgeRepository` - Busca textual da BaseKnowledgeRepository

```python
# Exemplo: Implementação concreta
class SQLMessageRepository(MessageRepository):
    def add(self, message: Message) -> int:
        # Implementação SQLite aqui
        pass
```

#### External Services
- `OpenAILLMService` - Integração com OpenAI (seleção de modelo, custo)
- `ResponseCache` - Cache MD5 em JSON (fallback, sem dependências extras)
- `SemanticCache` - Cache semântico com ChromaDB + sentence-transformers

```python
# SemanticCache — match por similaridade, não por texto exato
cache = SemanticCache(persist_dir="cache/semantic_cache", threshold=0.90)
cache.set("Como criar uma chain?", "Use o operador pipe: prompt | llm.")
cache.get("Como faço uma chain?")  # HIT — 0 tokens consumidos
```

### 4. **Interfaces Layer (Camada de Interface)**
Expõe o sistema ao usuário final.

#### CLI (`src/interfaces/cli/main.py`)
```python
class ChatCLI:
    def run_conversation(self):
        # Loop de conversa com usuário
        pass
```

#### API REST (`src/interfaces/api/main.py`)
Endpoints disponíveis:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Status da API |
| POST | `/sessions` | Criar nova sessão |
| POST | `/chat` | Enviar pergunta (com cache semântico) |
| GET | `/history/{session_id}` | Histórico da sessão |

---

## 🔄 Fluxo de Dados DDD

### Exemplo: Usuário faz uma pergunta

```
1. CLI / API recebe input do usuário
   ↓
2. SecurityService valida input (detecta API keys, código perigoso)
   ↓
3. SemanticCache.get() — busca por similaridade semântica
   → HIT: retorna resposta cached (zero tokens consumidos)
   → MISS: continua
   ↓
4. ChatService.ask() é chamada
      └─→ LocalTextKnowledgeRepository busca contexto (sem custo de API)
      └─→ ChatOpenAI gera resposta (LLM call)
      └─→ SQLMessageRepository salva no histórico
   ↓
5. SemanticCache.set() — armazena para futuras queries similares
   ↓
6. ResponseDTO é retornada
   ↓
7. CLI / API exibe resposta ao usuário
```

---

## 🔌 Mapeamento do Código Antigo → DDD

| Funcionalidade Antiga | Novo Módulo | Camada |
|---------------------------|-------------|--------|
| `inicializar_banco_de_dados()` | `SQLMessageRepository` | Infrastructure |
| `BuscaTextoLocal` | `LocalTextKnowledgeRepository` | Infrastructure |
| `CacheRespostas` (MD5) | `ResponseCache` | Infrastructure |
| Cache semântico (novo) | `SemanticCache` | Infrastructure |
| `criar_prompt()` | `ChatService._create_prompt()` | Application |
| `criar_llm()` | `OpenAILLMService` | Infrastructure |
| `iniciar_assistente()` | `ChatCLI.run_conversation()` | Interfaces |
| — (novo) | `FastAPI app` | Interfaces |

---

## 📚 Benefícios da Arquitetura DDD

### Antes (Monolítico)
```
❌ app.py com 500 linhas misturando tudo
❌ Difícil testar (tudo interdependente)
❌ Difícil adicionar features
❌ Lógica de domínio espalhada no código
```

### Depois (DDD)
```
✅ Separação clara de responsabilidades
✅ Cada camada tem um propósito
✅ Fácil testar (mocks simples via interfaces)
✅ Fácil escalar (adicionar features sem quebrar)
✅ Código expressa intenção ("domain-driven")
```

---

## 🚀 Como Usar

### No novo app.py (super simples!)

```python
from src.interfaces.cli import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
```

Pronto! A magia do DDD acontece nos bastidores:

1. CLI inicializa layer de Infraestrutura (Settings, Repos, Cache)
2. Infraestrutura injeta dependências nos Services
3. Services implementam Application logic
4. Domain entities encapsulam regras de negócio

---

## 📝 Próximos Passos

### Phase 1: Consolidação ✅ Concluída
- [x] Estrutura de pastas criada
- [x] Domain layer definido
- [x] Value Objects implementados
- [x] Repository interfaces criadas
- [x] Todos os módulos implementados e testados

### Phase 2: Testes ✅ Concluída
- [x] 88 testes passando (5 arquivos de teste)
- [x] Testes de API, App, Performance, Segurança e SemanticCache
- [x] Mocks de repositories e serviços externos

### Phase 3: Documentação ✅ Concluída
- [x] README atualizado
- [x] Arquitetura documentada (este arquivo)
- [x] Documentação de otimizações de tokens

### Phase 4: Otimização de Tokens ✅ Concluída
- [x] Cache semântico (ChromaDB + sentence-transformers)
- [x] RAG sem custo de API (keyword search)
- [x] Fallback automático para MD5 cache

---

## 🎯 Princípios DDD Implementados

| Princípio | Implementação | Benefício |
|-----------|---|---|
| **Ubiquitous Language** | Nomes claros (SessionId, MessageContent) | Código explica negócio |
| **Bounded Contexts** | Domain / Application / Infrastructure | Cada camada clara |
| **Entities vs VOs** | Message vs SessionId | Distinção semântica |
| **Repository Pattern** | MessageRepository abstrato | Trocar BD sem mudar lógica |
| **Dependency Injection** | Services recebem repos | Fácil testar |
| **Domain Events** | (Futuro) | Reatividade entre agregados |

---

## 📖 Referências

- **Domain-Driven Design** - Eric Evans (2003)
- **Clean Architecture** - Uncle Bob Martin
- **Padrões de Linguagem Pattern** - GoF

---

**Criado em:** 2024-03-16
**Atualizado em:** 2026-03-17
**Arquitetura:** DDD (Domain-Driven Design)
**Status:** ✅ Implementação Completa | 88 testes passando
