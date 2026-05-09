from langchain_groq import ChatGroq
from app.config import settings

_client = None

def get_client() -> ChatGroq:
    global _client
    if _client is None:
        _client = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.model_name,
            temperature=0.1,  # Low temp = consistent, factual responses
            max_tokens=1500
        )
    return _client

def call_llm(messages: list[dict]) -> str:
    """
    Call Groq LLM with a list of messages.
    Returns the raw text response.
    """
    client = get_client()

    # Convert to LangChain message format
    from langchain_core.messages import SystemMessage, HumanMessage

    lc_messages = []
    for msg in messages:
        if msg["role"] == "system":
            lc_messages.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))

    response = client.invoke(lc_messages)
    return response.content