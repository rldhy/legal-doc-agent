![Project Banner](/images/legal-doc-agent-banner.png)

# Legal Document Agent

A local AI-powered RAG application for querying legal documents using natural language.

The agent ingests legal documents, indexes their contents in a vector database, retrieves relevant passages for a question, and uses a locally hosted LLM to generate grounded answers with references to the source documents.

All document processing, embeddings, retrieval, and LLM inference can run locally.

## Features

* PDF document ingestion
* Recursive text chunking with source metadata
* Local embeddings with Ollama
* Persistent vector storage with Chroma
* Semantic retrieval across indexed documents
* Local LLM inference with Ollama
* Structured LLM responses
* Source validation and PDF page citations
* Idempotent document indexing
* Interactive and single-query CLI modes

## Architecture

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
Chroma Retrieval
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

## Tech Stack

* Python
* LangChain
* Ollama
* Gemma 3
* Chroma
* pypdf
* Pydantic
* Docker

Ollama runs locally in Docker with NVIDIA GPU acceleration.

## Project Structure

```text
src/agent/
├── main.py          # CLI entry point
├── index.py         # Document indexing
├── ingest.py        # PDF loading and metadata
├── chunking.py      # Document chunking
├── embeddings.py    # Ollama embedding configuration
├── vectorstore.py   # Chroma vector store
├── retrieval.py     # Semantic retrieval
├── llm.py           # Local LLM configuration
├── models.py        # Structured response models
└── rag.py           # RAG and citation logic
```

Legal documents are stored under:

```text
data/documents/
```

## Running Ollama

The project expects Ollama to be available at:

```text
http://localhost:11434
```

For example, Ollama can be started with Docker and NVIDIA GPU support:

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

## Indexing Documents

Place PDF documents in:

```text
data/documents/
```

Then run:

```bash
python -m agent.index
```

The indexer discovers PDFs, extracts their contents, creates chunks and embeddings, and stores them in the persistent Chroma vector store.

Indexing is idempotent. Documents that have not changed are skipped, while modified documents are re-indexed.

## Querying Documents

### Interactive Mode

```bash
python -m agent.main
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

### Single Query

A question can also be supplied directly:

```bash
python -m agent.main "What records must the partnership maintain?"
```

## How Answers Are Generated

For each question, the application:

1. Generates an embedding for the question.
2. Searches Chroma for semantically relevant document chunks.
3. Removes duplicate retrieval results.
4. Provides the retrieved evidence to the local LLM.
5. Generates a structured answer using only the supplied evidence.
6. Validates the LLM's requested citations against the retrieved documents.
7. Displays the answer with document and PDF page references.

The LLM is instructed not to answer questions when the retrieved documents do not provide sufficient evidence.

## Current Limitations

V1 intentionally keeps the RAG pipeline simple.

Current limitations include:

* PDF documents only
* Generic recursive text chunking
* Vector similarity retrieval without reranking
* PDF page-level citations rather than section/clause-level citations
* Limited handling of tables of contents and other document structure
* No explicit understanding of amendments or superseded contractual terms

## Future Work

Potential improvements include:

* Section- and clause-aware legal document chunking
* Table-of-contents detection and filtering
* Hybrid semantic and keyword retrieval
* Retrieval reranking
* Section-level citations
* Support for additional document formats
* Cross-document reasoning
* Structured extraction of parties, dates, obligations, and events
* Amendment and contract-version awareness
* RAG evaluation and retrieval-quality benchmarks
* LangGraph-based agent workflows

## Disclaimer

This project is intended for experimentation and educational purposes. Generated responses should not be considered legal advice, and important conclusions should be verified against the original source documents.
