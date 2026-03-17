# Assistente LangChain - Otimizado para AWS

## 1. Descrição

Este projeto implementa um assistente de linha de comando (CLI)
utilizando **LangChain e OpenAI**.

**✅ Otimizado para AWS com foco em REDUÇÃO DE CUSTOS:**
- RAG com busca textual local (sem embeddings caros)
- Modelo padrão: gpt-3.5-turbo ($0.50/$1.50 por 1M tokens)
- Histórico persistente em SQLite
- Cache de respostas (evita duplicação)
- Resumo automático de histórico (economiza tokens)

O assistente mantém histórico de conversa por sessão e responde
sempre em português, ajudando com revisão de código e boas práticas
em Python e LangChain.

## 2. Requisitos

- Python 3.11+
- Conta OpenAI com créditos ativos
- Bibliotecas (ver requirements.txt)

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
LANGCHAIN_MODEL=gpt-3.5-turbo        # Modelo (padrão: mais barato)
USE_RAG=true                          # Busca local (padrão: ativado)
```

Copie de `.env.example` se criar manualmente:
```bash
cp .env.example .env
```

⚠️ Nunca compartilhe sua chave de API. Adicione `.env` ao `.gitignore`!

## 4. Execução

No terminal, dentro da pasta do projeto:

```bash
python app.py
```

Digite sua pergunta e pressione ENTER.
Digite "sair" para encerrar o assistente.

## 5. Otimização para AWS

### Custos Reduzidos

| Modelo | Custo Input | Custo Output | Status |
|--------|-------------|--------------|--------|
| gpt-3.5-turbo | $0.50/1M | $1.50/1M | ✅ **Padrão** |
| gpt-4o-mini | $0.15/1M | $0.60/1M | Melhor qualidade |
| gpt-4-turbo | $10/1M | $30/1M | ❌ Caro |

### RAG SEM EMBEDDINGS

- Busca textual local: 0 chamadas à API
- Sem Pinecone/Weaviate: 0 custo de cliente vetorial
- Sem text-embedding-3-small: economia de $2 por 1M tokens

### ECONOMIAS NO HISTÓRICO

- Cache de respostas: evita 2ª chamada ao LLM
- Histórico limitado a 20 mensagens: 50% menos tokens
- Resumo automático: mantém contexto, reduz tamanho

## 6. Comandos da CLI

Durante a execução:

```
'sair'      → Encerrar assistente
'nova'      → Iniciar uma nova sessão
'historico' → Exibir histórico da sessão atual
'cache'     → Mostrar tamanho do cache
```

## 7. Histórico de Conversa

✅ **PERSISTENTE**: Salvo em SQLite (arquivo `chat_history.db`)
✅ **POR SESSÃO**: Cada dia tem uma sessão (pode criar novas com 'nova')
✅ **OTIMIZADO**: Histórico limitado a 20 mensagens (economiza tokens)

O histórico inclui:
- Timestamp de cada mensagem
- Tipo (human/assistant)
- Conteúdo completo

Benefícios:
- Recuperar contexto após reiniciar o programa
- Analisar histórico via comando 'historico'
- Otimizar custos limitando tamanho do histórico

## 8. Base de Conhecimento (RAG)

✅ **SEM EMBEDDINGS CAROS** - Busca textual local

### Como usar

1. Crie arquivo `knowledge_base.md` na raiz do projeto
2. Escreva o conhecimento organizado com seções (`##`)
3. Exemplo:

```markdown
## LangChain Básico

LangChain é um framework para construir aplicações com LLMs...

## Instalação

pip install langchain langchain-openai
```

### Como funciona

- Lê o arquivo automaticamente
- Divide em seções (`##`)
- Busca por palavras-chave (sem custo!)
- Injeta contexto relevante no prompt

⚠️ **IMPORTANTE**: Se `knowledge_base.md` não existir, RAG é desabilitado
(aplicação continua funcionando sem RAG)

## 9. Cache de Respostas

✅ **ECONOMIZA TOKENS**

Respostas frequentes ficam em cache:
- Arquivo: `cache/response_cache.json`
- Hash MD5 da pergunta = chave
- Resposta anterior armazenada

Exemplo:
- 1ª pergunta: $0.02 (LLM)
- 2ª pergunta idêntica: $0.00 (cache)

## 10. Segurança

O sistema:
- Valida se a API Key está configurada
- Alerta se detectar strings com "sk-" (potencial chave de API)
- Alerta se detectar "api_key" na entrada

⚠️ NUNCA envie chaves de API ou dados sensíveis no chat!

## 11. Estrutura do Projeto

```
project-langchain/
├── app.py                      # Código principal
├── requirements.txt            # Dependências Python
├── .env                        # Variáveis de ambiente (não comitar!)
├── .env.example                # Exemplo de .env
├── README.md                   # Este arquivo
├── chat_history.db             # Histórico persistente (SQLite)
├── cache/                      # Cache de respostas
│   └── response_cache.json     # Respostas em cache
└── knowledge_base.md           # Base de conhecimento (opcional)
```

## 12. Arquitetura Otimizada para AWS

```
┌─────────────────┐
│   Usuário (CLI) │
└────────┬────────┘
         │
    [Pergunta]
         │
    ┌────▼─────────────────────┐
    │  Cache de Respostas      │
    │  (response_cache.json)   │ ← Hit = $0 ✅
    └────┬─────────────────────┘
         │ Miss
    ┌────▼──────────────────────┐
    │  Busca Textual Local       │
    │  (BuscaTextoLocal)         │ ← $0 ✅
    │  knowledge_base.md         │
    └────┬──────────────────────┘
         │
    ┌────▼────────────────────────┐
    │  LangChain Chain            │
    │  + Histórico (SQLite) 20msg │ ← Otimizado
    │  + gpt-3.5-turbo           │ ← $0.50/$1.50
    │  + Prompt do Sistema       │
    └────┬───────────────────────┘
         │
    ┌────▼──────────────┐
    │  OpenAI API       │
    │  (Única chamada)  │
    └────┬──────────────┘
         │
    ┌────▼────────────────┐
    │  Resposta           │
    │  + Salva em Cache   │
    │  + Salva em SQLite  │
    └────────────────────┘
```

## 13. Estimativa de Custos

Assumindo:
- 100 perguntas/mês
- 50% de hits em cache
- Histórico limitado a 20 mensagens
- gpt-3.5-turbo

**Cálculo:**
- Perguntas com LLM: 100 × 50% = 50
- Média de tokens: 200 input + 150 output
- Custo: 50 × (0.0000005 × 200 + 0.0000015 × 150) ≈ **$0.16/mês**

**vs. sem otimizações** (100% LLM, histórico completo):
- Mesmo cenário: ≈$1.20/mês → **7.5x mais caro!**

## 14. Variáveis de Ambiente

```env
# Obrigatório
OPENAI_API_KEY=sk-...

# Opcional (valores padrão)
LANGCHAIN_MODEL=gpt-3.5-turbo     # Modelo LLM
USE_RAG=true                       # Ativar RAG local
```

## 15. Limitações Atuais

- Histórico não suporta múltiplos arquivos
- RAG limitado a busca textual (sem embeddings semânticos)
- Sem streaming de respostas

## 16. Possíveis Melhorias

- Integração com DynamoDB (ao invés de SQLite em produção AWS)
- CloudWatch logs para monitoramento
- Lambda function (invoke via API Gateway)
- Multi-tenancy com session_id por usuário
- Summarização de histórico longo com LLM
- Streaming de respostas com WebSocket

## 17. Deploy em AWS

### Opção 1: EC2 + LocalStack

```bash
# Criar instância EC2
# Instalar Python, dependências
# Upload do código
# Executar em background com supervisor
```

### Opção 2: Lambda + RDS

```python
# Containerizar com Docker
# Push para ECR
# Deploy em Lambda com RDS para histórico
```

### Opção 3: ECS + Fargate

```bash
# Containerizar
# Push para ECR
# Deploy em ECS/Fargate
```

## 18. Ambiente de Teste

Recomendado:
- Sistema operacional: Windows / Linux / macOS
- Python: 3.11.x
- Execução via terminal local
- Para AWS: Containerizar com Docker

## Contribuições

Sinta-se à vontade para sugerir melhorias! 🚀
