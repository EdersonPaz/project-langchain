# Assistente LangChain com Persistência e RAG

## 1. Descrição

Este projeto implementa um assistente de linha de comando (CLI)
utilizando **LangChain, OpenAI e Retrieval Augmented Generation (RAG)**.

O assistente:
- ✅ **Mantém histórico persistente** em SQLite (não apaga ao fechar!)
- ✅ **Integra base de conhecimento** com busca semântica via FAISS
- ✅ **Responde em português** com contexto relevante
- ✅ **Valida código Python** quanto a riscos de segurança
- ✅ **Detecta dados sensíveis** (chaves de API)

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
faiss-cpu >= 1.7, < 2.0
sqlalchemy >= 2.0, < 3.0
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
# Executar API FastAPI
python app.py --mode api
# Ou usar uvicorn diretamente:
uvicorn src.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Comandos disponíveis (CLI):

| Comando | Descrição |
|---------|-----------|
| `sair` | Encerra o assistente |
| `limpar` | Inicia uma nova sessão de conversa |
| `historico` | Mostra o histórico da sessão atual |
| Qualquer outra entrada | Envia pergunta ao assistente |

> Docker é opcional e permanece disponível em `docker/` caso queira containerizar o app posteriormente.
## 5. Funcionalidades Novas

### 🗄️ Persistência de Histórico

O histórico agora é salvo em um banco SQLite (`chat_history.db`):

- **Não apaga** ao fechar o programa
- **Organizado por sessão** (session_id)
- **Timestamps** para cada mensagem
- **Recuperável** via comando `historico`

```
chat_history.db (criado automaticamente)
```

### 📚 Base de Conhecimento com RAG

A aplicação carrega `knowledge_base.md` e indexa com FAISS:

1. **Carregamento**: Arquivo dividido em chunks de 500 caracteres
2. **Embeddings**: Usa `text-embedding-3-small` da OpenAI
3. **Indexação**: FAISS para busca vetorial rápida
4. **Recuperação**: Top-3 documentos mais relevantes por pergunta

O contexto relevante é **automaticamente injetado no prompt**:

```
CONTEXTO DA BASE DE CONHECIMENTO:
- Documento 1 mais relevante
- Documento 2 mais relevante
- Documento 3 mais relevante
```

## 6. Funcionamento Interno

### Fluxo de Uma Pergunta

```
1. Usuário digita pergunta
      ↓
2. Busca semântica na base (RAG)
      ↓
3. Recupera top-3 documentos relevantes
      ↓
4. Injeta histórico + contexto no prompt
      ↓
5. OpenAI gera resposta
      ↓
6. Resposta exibida e salva em SQLite
      ↓
7. Ciclo continua
```

### Componentes Principais

| Componente | Função |
|-----------|--------|
| `ChatOpenAI` | Modelo LLM (gpt-4o-mini) |
| `SQLChatMessageHistory` | Persistência de histórico |
| `FAISS` | Vetorização e busca semântica |
| `OpenAIEmbeddings` | Geração de embeddings |
| `RecursiveCharacterTextSplitter` | Divisão de documentos |
| `SQLChatMessageHistory` | Storage em SQLite |

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

## 10. Possíveis Melhorias

- [ ] Persistência de embeddings (FAISS vector cache)
- [ ] API REST com FastAPI
- [ ] Suporte a múltiplos usuários (autenticação)
- [ ] Streaming de respostas
- [ ] Listar arquivos adicionais (PDF, DOCX)
- [ ] Dashboard de métricas
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
├── app.py                    # Código principal
├── src/                      # DDD core (domain, application, infrastructure, interfaces)
├── tests/                    # Testes automatizados
├── requirements.txt          # Dependências Python
├── .env                      # Variáveis de ambiente (não commitar!)
├── chat_history.db           # Banco SQLite (criado automaticamente)
├── knowledge_base.md         # Base de conhecimento para RAG
├── scripts/                  # Scripts de execução local e manutenção
├── docs/                     # Documentos gerados e guias de uso
└── README.md                 # Este arquivo
```

> O suporte Docker foi removido para foco em execução local e estrutura DDD limpa.

## 13. Exemplos de Uso

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

### ❌ "FAISS não encontrado"
```bash
pip install faiss-cpu
```

### ❌ "knowledge_base.md não encontrado"
O arquivo já existe no projeto, mas certifique-se de que está na raiz.

### ❌ "RateLimitError"
Você atingiu o limite de requisições da OpenAI.
Verifique: https://platform.openai.com/account/billing

### ❌ "Embedding falhou"
Certifique-se de que:
- ✓ OPENAI_API_KEY está correto
- ✓ Você tem créditos disponíveis
- ✓ knowledge_base.md não está vazio

## 15. Links Úteis

- 📖 [LangChain Docs](https://python.langchain.com)
- 🤖 [OpenAI API](https://platform.openai.com)
- 📊 [FAISS](https://github.com/facebookresearch/faiss)
- 🐍 [Python Docs](https://docs.python.org/3.11/)

