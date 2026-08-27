from langchain_chroma import Chroma

from agent.embeddings import get_embeddings
from agent.config import settings


def load_vector_store() -> Chroma:
    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embeddings(),
        persist_directory=str(settings.chroma_path),
    )


def get_chunks_by_filename(
    vector_store: Chroma,
    filename: str,
) -> dict:
    return vector_store.get(
        where={"filename": filename},
    )


def get_chunks_by_document_hash(
    vector_store: Chroma,
    document_hash: str,
) -> dict:
    return vector_store.get(
        where={"document_hash": document_hash},
    )
