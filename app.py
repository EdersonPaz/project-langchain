import os
from dotenv import load_dotenv

# =========================================================
# 1️⃣ CARREGAMENTO DE VARIÁVEIS DE AMBIENTE
# =========================================================
# Carrega o conteúdo do arquivo .env para o ambiente
load_dotenv()

# Validação defensiva da API Key
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("❌ OPENAI_API_KEY não configurada no .env")

# =========================================================
# 2️⃣ IMPORTS DO LANGCHAIN
# =========================================================
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationSummaryMemory
from langchain.tools import tool
from langchain.callbacks import StdOutCallbackHandler

from openai import RateLimitError


# =========================================================
# 3️⃣ PROMPT DO SISTEMA
# =========================================================
# Define o "papel" fixo do assistente
system_prompt = """
Você é um assistente especialista em LLMs e LangChain com Python.
Responda sempre em português, de forma clara e objetiva.

Sempre que possível:
- pergunte qual ambiente o usuário utiliza
- pergunte versão do Python e do LangChain
- pergunte onde a solução será aplicada

Ajude com:
- revisão de código
- boas práticas
- organização de projetos
- ambientes de teste

⚠️ Se detectar chaves de API, tokens ou dados sensíveis,
emita um alerta de segurança imediatamente.
"""

# Prompt com histórico
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])


# =========================================================
# 4️⃣ MODELO LLM
# =========================================================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    callbacks=[StdOutCallbackHandler()]  # Loga prompts e respostas no terminal
)

# Cadeia base
chain = prompt | llm


# =========================================================
# 5️⃣ TOOL (FUNÇÃO QUE O LLM PODE USAR)
# =========================================================
@tool
def validar_codigo_python(codigo: str) -> str:
    """
    Analisa código Python e aponta riscos básicos de segurança.
    """
    alertas = []

    if "eval(" in codigo:
        alertas.append("Uso de eval detectado (risco de segurança).")

    if "exec(" in codigo:
        alertas.append("Uso de exec detectado (risco de segurança).")

    if "os.system" in codigo:
        alertas.append("Execução de comandos do sistema detectada.")

    if not alertas:
        return "✅ Nenhum problema crítico encontrado."

    return "⚠️ Alertas encontrados:\n- " + "\n- ".join(alertas)


# =========================================================
# 6️⃣ MEMÓRIA POR SESSÃO
# =========================================================
# Armazena histórico por usuário (em memória RAM)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Retorna o histórico da sessão.
    Se não existir, cria um novo.
    """
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# =========================================================
# 7️⃣ WRAPPER COM HISTÓRICO
# =========================================================
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)


# =========================================================
# 8️⃣ FUNÇÃO PRINCIPAL DO ASSISTENTE
# =========================================================
def iniciar_assistente():
    print("🤖 Assistente LangChain iniciado")
    print("Digite 'sair' para encerrar\n")

    session_id = "user123"  # Em API isso viria do token ou header

    while True:
        pergunta_usuario = input("Você: ")

        # Encerrar aplicação
        if pergunta_usuario.lower() in ["sair", "exit"]:
            print("👋 Assistente encerrado com sucesso!")
            break

        # Alerta simples de segurança
        if "sk-" in pergunta_usuario:
            print("⚠️ ALERTA: Não envie chaves de API ou dados sensíveis.")
            continue

        try:
            resposta = chain_with_history.invoke(
                {"input": pergunta_usuario},
                config={"configurable": {"session_id": session_id}}
            )

            print("\nAssistente:", resposta.content, "\n")

        except RateLimitError:
            print(
                "\n⚠️ Limite de uso da OpenAI atingido.\n"
                "Verifique seu plano em:\n"
                "https://platform.openai.com/account/billing\n"
            )


# =========================================================
# 9️⃣ ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    iniciar_assistente()
