from langchain_ollama import OllamaEmbeddings
from agent.config import settings

def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
    )
