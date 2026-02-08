1. Descrição

Este projeto implementa um assistente de linha de comando (CLI)
utilizando LangChain e OpenAI.
O assistente mantém histórico de conversa por sessão e responde
sempre em português, ajudando com revisão de código e boas práticas
em Python e LangChain.

2. Requisitos

Python 3.11
Conta OpenAI com créditos ativos
Bibliotecas:
langchain-core
langchain-openai
langchain-community
python-dotenv

3. Configuração

Crie um arquivo chamado .env na raiz do projeto com o conteúdo:
OPENAI_API_KEY=sk-sua-chave-aqui
⚠️ Nunca compartilhe sua chave de API.

4. Execução

No terminal, dentro da pasta do projeto, execute:
python app.py
Digite sua pergunta e pressione ENTER.
Digite "sair" para encerrar o assistente.

5. Funcionamento interno (resumo)

O fluxo principal é:
O usuário digita uma pergunta
O sistema injeta o histórico da conversa
O prompt do sistema define o comportamento do assistente
O modelo OpenAI gera a resposta
O histórico é armazenado em memória

6. Histórico de Conversa

O histórico é mantido em memória RAM e separado por sessão.
Atualmente, todas as conversas usam o mesmo session_id.
Em aplicações reais (API), o session_id pode vir de:
token do usuário
cookie
header HTTP

7. Segurança

O sistema:
valida se a API Key está configurada
alerta caso o usuário tente enviar chaves ou tokens

8. Limitações atuais

Histórico não persistente (reinicia ao fechar o programa)
Sem base de conhecimento (RAG)
Sem streaming de resposta

9. Possíveis melhorias

Persistir histórico em banco ou Redis
Adicionar leitura de PDFs (RAG)
Criar uma API com FastAPI
Implementar streaming de respostas
Adicionar validação estruturada de saída

10. Estrutura do Projeto

app.py → código principal
.env → variáveis de ambiente

11. Ambiente de Teste

Ambiente recomendado para testes:
Sistema operacional: Windows / Linux / macOS

Python: 3.11.x

Execução via terminal local
