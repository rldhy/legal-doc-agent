from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "gemma3:12b"
    ollama_embedding_model: str = "nomic-embed-text"

    chroma_path: Path = Path("/.chroma")
    chroma_collection_name: str = "legal_documents"

    documents_path: Path = Path("/data/documents")

    chunk_size: int = 1000
    chunk_overlap: int = 150

    retrieval_candidate_count: int = 8
    retrieval_result_count: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()