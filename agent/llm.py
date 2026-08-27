from langchain_ollama import ChatOllama
from agent.config import settings


def get_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_llm_model,
        base_url=settings.ollama_base_url,
        temperature=0,
    )
