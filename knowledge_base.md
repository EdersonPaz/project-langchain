# Base de Conhecimento - LangChain e Python

## LangChain Basics

### O que é LangChain?
LangChain é um framework para desenvolver aplicações impulsionadas por modelos de linguagem grandes (LLMs).
Ele fornece componentes reutilizáveis para construir aplicações complexas com LLMs.

### Componentes Principais

#### 1. Models (Modelos)
Os models são interfaces para LLMs como OpenAI, Anthropic, etc.
Exemplo: ChatOpenAI, Ollama, HuggingFace

#### 2. Prompts (Prompts)
Prompts são templates para formatar input para o modelo.
Use ChatPromptTemplate para criar prompts estruturados com variáveis.

#### 3. Output Parsers
Output parsers estruturam a saída dos modelos em formatos úteis.
Exemplos: JSONOutputParser, StrOutputParser, CommaSeparatedListOutputParser

#### 4. Chains (Cadeias)
Chains conectam múltiplos componentes para criar workflows complexos.
Use o operador | (pipe) para conectar componentes: prompt | model | parser

#### 5. Memory (Memória)
Memory mantém histórico de conversas.
Tipos: ChatMessageHistory, ConversationBufferMemory, ConversationSummaryMemory

#### 6. Tools (Ferramentas)
Tools permitem que o modelo execute ações.
Use @tool decorator para criar ferramentas customizadas.

#### 7. Agents (Agentes)
Agents usam LLMs para decidir quais tools usar.
Exemplo: ReAct (Reasoning + Acting)

## Boas Práticas

### Organizando Projetos com LangChain

1. **Estrutura de Pastas**
```
projeto/
├── app.py           # Código principal
├── .env             # Variáveis de ambiente
├── requirements.txt # Dependências
├── prompts/         # Templates de prompts
├── tools/           # Ferramentas customizadas
├── chains/          # Definição de chains
└── data/            # Dados de treinamento
```

2. **Versionamento de Dependências**
- Sempre use ranges específicas (>=0.3,<0.4)
- Teste compatibilidade entre versions
- Use requirements-lock.txt em produção

3. **Segurança**
- Nunca commitar .env ou API keys
- Usar environment variables
- Validar inputs antes de passar ao LLM
- Sanitizar outputs sensíveis

### Error Handling

```python
from openai import RateLimitError

try:
    resposta = chain.invoke({"input": pergunta})
except RateLimitError:
    print("Rate limit atingido")
except Exception as e:
    print(f"Erro: {e}")
```

### Performance e Otimização

1. **Caching**
- Use cache para respostas duplicadas
- LangChain fornece integração com Redis

2. **Streaming**
- Use .stream() ou .astream() para respostas em tempo real
- Reduz latência percebida

3. **Batch Processing**
- Use .batch() para processar múltiplas entradas
- Mais eficiente que chamar sequencialmente

4. **Assincronismo**
- Use async/await para I/O não-bloqueante
- chain.ainvoke() para chamadas assincronizadas

## Retrieval Augmented Generation (RAG)

### O que é RAG?
RAG é uma técnica que combina retrieved documents com geração de texto.
Permite que o modelo tenha acesso a conhecimento externo.

### Componentes de RAG

1. **Vetorização (Embeddings)**
- Converte texto em vetores numéricos
- OpenAIEmbeddings, HuggingFaceEmbeddings

2. **Vector Store**
- Armazena e busca vetores
- Exemplos: FAISS, Chroma, Pinecone, Weaviate

3. **Retriever**
- Busca documentos relevantes baseado no input
- Exemplo: similarity_search_with_score

4. **Pipeline RAG**
- Input → Buscar documentos → Aumentar prompt → Gerar resposta

## Python Best Practices

### Type Hints
```python
def funcao(param: str) -> str:
    return f"Resultado: {param}"
```

### Docstrings
Use docstrings para documentar funções:
```python
def funcao(x: int) -> int:
    """
    Descrição curta.
    
    Args:
        x: Descrição do parâmetro
        
    Returns:
        Descrição do retorno
    """
    pass
```

### Estrutura de Classes
```python
class Assistente:
    def __init__(self, config: dict) -> None:
        self.config = config
        
    def processar(self, input: str) -> str:
        pass
```

### Virtual Environments
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows python -m pip install -r requirements.txt
```

## Debugging

### Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Mensagem de debug")
```

### Callbacks
LangChain oferece callbacks para monitorar execução:
- StdOutCallbackHandler: imprime prompts e respostas
- LangChainTracer: salva traces em LangSmith

## Recursos Úteis

- Documentação: https://python.langchain.com
- GitHub: https://github.com/langchain-ai/langchain
- Discord: https://discord.gg/cU2adEKapZ
- LangSmith: https://smith.langchain.com (debugging e testing)
