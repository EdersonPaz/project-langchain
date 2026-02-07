import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from openai import RateLimitError


# Validação da API Key
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY não configurada")


# Prompt do sistema
system_prompt = """Você é um assistente especialista em LLMs e LangChain com Python.
Você responde de forma clara, objetiva e sempre em português.

Sempre que possível:
- pergunte qual ambiente o usuário utiliza (local, cloud, API, etc.)
- pergunte versão do Python e do LangChain
- pergunte onde a solução será aplicada (script, API, produção)

Ajude com:
- revisão e melhoria de código
- boas práticas
- organização de projeto
- ambientes de teste

⚠️ Se o usuário enviar chaves de API, tokens ou dados sensíveis,
emita um alerta de segurança imediatamente.
"""


prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])


# Modelo
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0 #0.7
)

chain = prompt | llm


# Histórico em memória (por sessão)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)


def iniciar_assistente():
    print("🤖 Assistente LangChain iniciado! Digite 'sair' para encerrar.\n")

    while True:
        pergunta_usuario = input("Você: ")

        if pergunta_usuario.lower() in ["sair", "exit"]:
            print("Assistente: Encerrado com sucesso!")
            break

        try:
            resposta = chain_with_history.invoke(
                {"input": pergunta_usuario},
                config={"configurable": {"session_id": "user123"}}
            )

            print("Assistente:", resposta.content)

        except RateLimitError:
            print(
                "⚠️ Assistente: limite de uso da OpenAI atingido.\n"
                "Verifique seu plano ou créditos em https://platform.openai.com/account/billing\n"
            )


if __name__ == "__main__":
    iniciar_assistente()