![Project Banner](/images/legal-doc-agent-banner.png)

# Legal Document Agent

A local-first RAG application for querying legal documents using natural language.

Legal Document Agent ingests legal documents, indexes their contents using embeddings and vector search, retrieves relevant passages for a question, and uses a locally hosted LLM to generate grounded answers with citations to the original source documents.

All document processing, embeddings, retrieval, and LLM inference run locally.

## Features

* PDF document ingestion
* Recursive text chunking with preserved source metadata
* Local embeddings with Ollama
* Persistent vector storage with Chroma
* Semantic vector search across indexed documents
* Local LLM inference with Ollama
* Structured LLM responses with Pydantic
* Validated document and PDF page citations
* Idempotent document indexing
* Interactive and single-query CLI modes
* Environment-based configuration

## Architecture

The application separates document indexing from question answering.

```text
                    Indexing

PDF Documents
     │
     ▼
   pypdf
     │
     ▼
LangChain Documents
     │
     ▼
Text Chunking
     │
     ▼
Ollama Embeddings
     │
     ▼
   Chroma


                    Querying

User Question
     │
     ▼
Ollama Embedding
     │
     ▼
Chroma Vector Search
     │
     ▼
Relevant Chunks
     │
     ▼
Gemma 3 via Ollama
     │
     ▼
Structured Answer
     │
     ▼
Validated Source Citations
```

Documents are processed once during indexing and stored in a persistent Chroma collection. Queries use the existing index, so documents do not need to be reprocessed each time the application runs.

## Tech Stack

* Python 3.12
* LangChain
* Ollama
* Gemma 3
* Nomic Embed Text
* Chroma
* pypdf
* Pydantic
* uv
* Docker

Ollama runs locally in Docker with NVIDIA GPU acceleration.

## Project Structure

```text
legal-doc-agent/
├── data/
│   └── documents/        # Local legal documents
├── docs/                 # Additional project documentation
├── images/               # README and project assets
├── src/
│   └── agent/
│       ├── main.py       # CLI entry point
│       ├── index.py      # Document indexing
│       ├── ingest.py     # PDF loading, hashing, and metadata
│       ├── chunking.py   # Document chunking
│       ├── embeddings.py # Ollama embedding configuration
│       ├── vectorstore.py# Chroma vector store
│       ├── retrieval.py  # Semantic retrieval and deduplication
│       ├── llm.py        # Local LLM configuration
│       ├── models.py     # Structured response models
│       ├── rag.py        # RAG and citation logic
│       └── settings.py     # Application configuration
├── .env.example
├── AGENTS.md
├── pyproject.toml
├── uv.lock
└── README.md
```

Legal documents under `data/documents/` are intentionally excluded from Git.

## Getting Started

### Prerequisites

The project requires:

* Python 3.12+
* uv
* Docker
* Ollama

An NVIDIA GPU is optional, but can significantly improve local model inference performance.

### Install Dependencies

Clone the repository and install the project dependencies:

```bash
git clone <repository-url>
cd legal-doc-agent

uv sync
```

`uv` creates and manages the project's virtual environment and installs the dependencies defined in `pyproject.toml`.

### Configure the Application

Copy the example environment file:

```bash
cp .env.example .env
```

The default configuration uses:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=gemma3:12b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

CHROMA_PATH=.chroma
CHROMA_COLLECTION_NAME=legal_documents

DOCUMENTS_PATH=data/documents

RETRIEVAL_CANDIDATE_COUNT=8
RETRIEVAL_RESULT_COUNT=5

CHUNK_SIZE=1000
CHUNK_OVERLAP=150
```

These values can be changed in `.env` without modifying the application code.

## Running Ollama

The project expects Ollama to be available at:

```text
http://localhost:11434
```

Ollama can be started with Docker and NVIDIA GPU support:

```bash
docker run -d \
  --gpus=all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

Pull the required models:

```bash
docker exec -it ollama ollama pull gemma3:12b
docker exec -it ollama ollama pull nomic-embed-text
```

Verify that the models are available:

```bash
docker exec -it ollama ollama list
```

For more detailed Docker and NVIDIA GPU setup instructions, see [`docs/ollama-docker-setup.md`](docs/ollama-docker-setup.md).

## Indexing Documents

Place PDF documents under:

```text
data/documents/
```

Then build or update the index:

```bash
uv run index-agent
```

The indexer:

1. Discovers PDF documents.
2. Extracts their text and source metadata.
3. Splits each document into chunks.
4. Generates embeddings locally using Ollama.
5. Stores the chunks and embeddings in Chroma.

Indexing is idempotent. Each document is identified using a content hash:

* New documents are indexed.
* Unchanged documents are skipped.
* Modified documents replace their previously indexed contents.

This allows the indexer to be run repeatedly without creating duplicate vectors.

## Querying Documents

### Interactive Mode

Start the interactive CLI:

```bash
uv run query-agent
```

Example:

```text
Legal Document Agent
Type 'quit' or 'exit' to stop.

> What records must the partnership maintain?

The Partnership must maintain its Agreement and all amendments thereto,
full and accurate books showing receipts and expenditures, assets and
liabilities, Profits and Losses, and other records required by the Act.

Sources:
- sample-partnership-agreement.pdf, PDF page 14
```

Enter additional questions at the prompt, or type `quit` or `exit` to stop.

## How Answers Are Generated

For each question, the application:

1. Generates an embedding for the question using Ollama.
2. Searches Chroma for semantically relevant document chunks.
3. Removes duplicate retrieval results.
4. Provides the retrieved evidence to the local LLM.
5. Generates a structured response using only the supplied evidence.
6. Validates the LLM's requested citations against the retrieved documents.
7. Maps validated citations back to their source documents and PDF pages.
8. Displays the grounded answer with source references.

The retrieved chunks form the evidence available to the LLM. The model is explicitly instructed not to rely on outside knowledge or unsupported assumptions.

If the retrieved documents do not provide enough evidence to answer a question, the response indicates that the available evidence is insufficient.

### Citation Validation

Citation generation is intentionally separated between the LLM and the application.

The LLM identifies which retrieved sources support its answer using structured source IDs. The application then validates those IDs and maps them back to the original document metadata.

```text
Retrieved Evidence
       │
       ▼
  [SOURCE 1]
  [SOURCE 2]
  [SOURCE 3]
       │
       ▼
      LLM
       │
       ▼
Structured Answer
answer + source IDs
       │
       ▼
Citation Validation
       │
       ▼
filename + PDF page
```

This prevents the model from directly inventing filenames or page numbers and keeps citation provenance tied to the retrieval pipeline.

## Current Limitations

V1 intentionally keeps the RAG pipeline simple and deterministic.

Current limitations include:

* PDF documents only
* Generic recursive text chunking
* Vector similarity retrieval without reranking
* PDF page-level citations rather than section/clause-level citations
* Limited handling of tables of contents and other document structure
* No explicit understanding of amendments or superseded contractual terms
* No structured legal entity or obligation extraction

## Future Work

Potential improvements include:

* Section- and clause-aware legal document chunking
* Table-of-contents detection and filtering
* Hybrid semantic and keyword retrieval
* Retrieval reranking
* Section- and clause-level citations
* Support for additional document formats
* Cross-document reasoning
* Structured extraction of parties, dates, obligations, and events
* Amendment and contract-version awareness
* RAG evaluation and retrieval-quality benchmarks
* LangGraph-based agent workflows for multi-step legal document research

The goal is to evolve the current deterministic RAG pipeline into a system capable of reasoning across relationships, obligations, events, dates, and related documents while preserving evidence traceability.

## Privacy

Legal documents can contain confidential or sensitive information. This project is designed to keep document processing local by default.

PDF parsing, embeddings, vector storage, retrieval, and LLM inference can all run on the local machine without sending document contents to an external model provider.

Users are responsible for ensuring that their use of documents and models complies with applicable confidentiality, licensing, and data-handling requirements.

## Disclaimer

This project is intended for experimentation and educational purposes. Generated responses should not be considered legal advice, and important conclusions should always be verified against the original source documents.
