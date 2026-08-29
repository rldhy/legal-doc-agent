from langchain_core.documents import Document
from agent.models import LegalAnswer


def build_context(documents):
    sections = []

    for index, document in enumerate(documents, start=1):
        sections.append(
            f"""[SOURCE {index}]
Document: {document.metadata["filename"]}
PDF Page: {document.metadata["page_number"]}

{document.page_content}
"""
        )

    return "\n\n".join(sections)


def answer_question(
    query: str,
    documents: list[Document],
    llm,
) -> LegalAnswer:
    context = build_context(documents)

    structured_llm = llm.with_structured_output(
        LegalAnswer
    )

    prompt = f"""
You are a legal document question-answering assistant.

Answer the user's question using ONLY the provided source material.

Rules:
- Do not use outside knowledge.
- Do not make unsupported assumptions.
- The citations field must contain the source numbers that directly support
  the answer.
- Only cite source numbers that appear in the provided material.
- If the sources are insufficient to answer the question:
    - set insufficient_evidence to true
    - explain what information is missing
- Otherwise set insufficient_evidence to false.

Question:
{query}

Sources:
{context}
"""

    return structured_llm.invoke(prompt)


def validate_citations(
    answer: LegalAnswer,
    documents: list[Document],
) -> list[int]:
    valid_sources = set(range(1, len(documents) + 1))

    return [
        citation
        for citation in answer.citations
        if citation in valid_sources
    ]


def citation_sources(
    answer: LegalAnswer,
    documents: list[Document],
) -> list[Document]:
    seen = set()
    sources = []

    for citation in validate_citations(answer, documents):
        document = documents[citation - 1]

        key = (
            document.metadata["filename"],
            document.metadata["page_number"],
        )

        if key in seen:
            continue

        seen.add(key)
        sources.append(document)

    return sources


def print_answer(
    answer: LegalAnswer,
    documents: list[Document],
) -> None:
    print(answer.answer)

    sources = citation_sources(answer, documents)

    if sources:
        print("\nSources:")

        for document in sources:
            print(
                f"- {document.metadata['filename']}, "
                f"PDF page {document.metadata['page_number']}"
            )