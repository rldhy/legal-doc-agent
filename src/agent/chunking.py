import hashlib

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agent.settings import settings


def chunk_documents(
    documents: list[Document],
    chunk_size: int = settings.chunk_size,
    chunk_overlap: int = settings.chunk_overlap,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    for chunk_index, chunk in enumerate(chunks):
        document_hash = chunk.metadata["document_hash"]

        raw_id = (
            f"{document_hash}:"
            f"{chunk.metadata['page_number']}:"
            f"{chunk_index}"
        )

        chunk.metadata["chunk_id"] = hashlib.sha256(
            raw_id.encode()
        ).hexdigest()

    return chunks