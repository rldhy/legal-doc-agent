import hashlib
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


def get_file_hash(path: Path) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(8192), b""):
            hasher.update(block)

    return hasher.hexdigest()


def load_pdf(path: Path) -> list[Document]:
    reader = PdfReader(path)
    document_hash = get_file_hash(path)

    documents: list[Document] = []

    for index, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(path.resolve()),
                    "filename": path.name,
                    "document_hash": document_hash,
                    "page": index,
                    "page_number": index + 1,
                    "total_pages": len(reader.pages),
                },
            )
        )

    return documents
