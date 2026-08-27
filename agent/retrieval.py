from langchain_chroma import Chroma
from langchain_core.documents import Document

from agent.config import settings


def deduplicate_documents(documents: list[Document]) -> list[Document]:
    seen = set()
    unique = []

    for document in documents:
        key = document.page_content.strip()

        if key not in seen:
            seen.add(key)
            unique.append(document)

    return unique


def retrieve_documents(
        vector_store: Chroma,
        query: str,
        candidate_count: int = settings.retrieval_candidate_count,
        result_count: int = settings.retrieval_result_count,
) -> list[Document]:
    retrieved = vector_store.similarity_search(
        query,
        k=candidate_count,
    )

    results = deduplicate_documents(retrieved)

    return results[:result_count]
