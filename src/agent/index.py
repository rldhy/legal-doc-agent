from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from agent.chunking import chunk_documents
from agent.ingest import load_pdf, get_file_hash
from agent.vectorstore import get_chunks_by_document_hash, get_chunks_by_filename, load_vector_store
from agent.settings import settings


def document_is_indexed(
    vector_store: Chroma,
    document_hash: str,
) -> bool:
    result = get_chunks_by_document_hash(
        vector_store,
        document_hash,
    )

    return bool(result["ids"])


def remove_existing_document(
    vector_store: Chroma,
    filename: str,
) -> int:
    result = get_chunks_by_filename(
        vector_store,
        filename,
    )

    ids = result["ids"]

    if not ids:
        return 0

    vector_store.delete(ids=ids)

    return len(ids)


def process_document(path: Path) -> list[Document]:
    vector_store = load_vector_store()
    document_hash = get_file_hash(path)

    if document_is_indexed(
            vector_store,
            document_hash,
    ):
        print(f"Skipping {path.name}: already indexed")
        return []

    existing = get_chunks_by_filename(
        vector_store,
        path.name,
    )

    if existing["ids"]:
        removed = remove_existing_document(
            vector_store,
            path.name,
        )

        print(
            f"Updating {path.name}: "
            f"removed {removed} old chunks"
        )

    pages = load_pdf(path)
    chunks = chunk_documents(pages)

    ids = [
        chunk.metadata["chunk_id"]
        for chunk in chunks
    ]

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    print(
        f"Indexed {path.name}: "
        f"{len(pages)} pages → {len(chunks)} chunks"
    )

    return chunks


def index_documents(
    documents_dir: Path = settings.documents_path,
) -> None:
    paths = sorted(documents_dir.rglob("*.pdf"))

    if not paths:
        print(f"No PDF documents found in {documents_dir}")
        return

    all_chunks: list[Document] = []

    for path in paths:
        print(f"Processing {path.name}...")
        all_chunks.extend(process_document(path))

    print(
        f"\nIndexed {len(all_chunks)} chunks "
        f"from {len(paths)} documents."
    )


def main():
    index_documents()


if __name__ == "__main__":
    main()
