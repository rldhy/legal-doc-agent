# AI Agent Development Guide

This file provides context and development guidance for AI coding agents working on this repository.

## Project Overview

This project is a local-first RAG application for querying legal documents using natural language.

The application:

1. Ingests legal documents.
2. Extracts text and source metadata.
3. Splits documents into retrieval chunks.
4. Generates embeddings locally using Ollama.
5. Stores embeddings and metadata in Chroma.
6. Retrieves relevant chunks for a user's question.
7. Uses a locally hosted LLM to generate a grounded answer.
8. Validates and renders citations back to the original documents.

The system is designed to keep document contents, embeddings, retrieval, and inference local.

## Current Milestone

V1 is complete.

V1 supports:

* PDF ingestion
* Page-level provenance metadata
* Recursive text chunking
* Local Ollama embeddings
* Persistent Chroma storage
* Idempotent document indexing
* Semantic retrieval
* Duplicate retrieval filtering
* Local LLM inference
* Structured answers
* Citation validation
* PDF page-level source citations
* Interactive CLI querying
* Single-query CLI execution

Future changes should preserve this functionality unless explicitly replacing it.

## Technology Stack

Primary technologies:

* Python 3.12+
* LangChain core and standalone integrations
* Ollama
* Gemma 3 12B
* Nomic Embed Text
* Chroma
* pypdf
* Pydantic
* pydantic-settings
* Docker

Do not introduce `langchain-community`. Prefer standalone LangChain integration packages or direct library usage.

## Project Structure

The application code lives under:

```text
src/agent/
```

Major modules:

```text
main.py
    CLI entry point and application orchestration.

index.py
    Discovers and indexes documents.

ingest.py
    Reads PDFs and creates page-level LangChain Documents.
    Responsible for source metadata and document fingerprints.

chunking.py
    Splits page Documents into retrieval chunks while preserving metadata.

embeddings.py
    Configures the local Ollama embedding model.

vectorstore.py
    Creates or loads the persistent Chroma collection and provides
    vector-store-related helpers.

retrieval.py
    Retrieves candidate chunks and performs retrieval-level processing
    such as deduplication.

llm.py
    Configures the local Ollama generation model.

models.py
    Contains Pydantic models used for structured LLM responses.

rag.py
    Builds grounded context, invokes the LLM, validates citations,
    and renders answers.

config.py
    Contains typed application configuration backed by environment variables.
```

Documents for local development are stored under:

```text
data/documents/
```

Actual legal documents should not be committed to Git.

## Architecture

### Indexing

```text
PDF
 │
 ▼
pypdf
 │
 ▼
Page Documents + metadata
 │
 ▼
Chunking
 │
 ▼
Ollama embeddings
 │
 ▼
Chroma
```

Indexing is separate from querying.

Do not re-index documents during normal query execution.

### Querying

```text
User question
     │
     ▼
Query embedding
     │
     ▼
Chroma similarity search
     │
     ▼
Candidate chunks
     │
     ▼
Deduplication
     │
     ▼
Grounded prompt
     │
     ▼
Local LLM
     │
     ▼
Structured response
     │
     ▼
Citation validation
     │
     ▼
Answer + source references
```

## Important Design Principles

### Keep inference local

The project is intentionally local-first.

Do not introduce external hosted LLM or embedding APIs unless explicitly requested.

Legal document text should not be transmitted to external services by default.

### Preserve provenance

Every document chunk must retain enough metadata to trace it back to the original source.

At minimum, preserve:

* source
* filename
* document hash
* PDF page number
* chunk ID

Never discard provenance during transformations.

Future section-aware parsing should add metadata rather than replacing existing provenance.

### Do not let the LLM invent citations

The LLM may identify which retrieved sources support an answer, but the application owns citation validation and rendering.

Never trust model-generated filenames, page numbers, section numbers, URLs, or source identifiers without validating them against application-controlled metadata.

Citation IDs returned by the model must correspond to sources actually supplied to that model invocation.

### Ground answers in retrieved evidence

The generation model must answer using the supplied source material.

When evidence is insufficient, the application should prefer an explicit insufficient-evidence response over an unsupported answer.

Do not weaken grounding prompts merely to make the model answer more questions.

### Retrieval and generation are separate concerns

Do not assume that improving the prompt fixes poor retrieval.

When investigating incorrect answers, inspect:

1. What chunks were retrieved?
2. Did they contain the necessary evidence?
3. Were the correct chunks ranked highly enough?
4. Only then inspect generation behavior.

Retrieval quality should be testable independently of the LLM.

### Keep indexing idempotent

Re-running the indexer against unchanged documents must not create duplicate vectors.

Current indexing behavior should distinguish:

```text
new document       → index
unchanged document → skip
modified document  → replace previous chunks
```

Document fingerprints are based on file contents.

Chunk/vector IDs should be deterministic.

### Keep modules focused

Avoid putting the entire pipeline into `main.py`.

`main.py` should primarily orchestrate existing components.

Prefer small functions with clear responsibilities over large framework-driven abstractions.

## Configuration

Runtime configuration is defined through environment variables and loaded by `config.py`.

Use `.env.example` as the canonical list of configurable values.

Typical settings include:

```text
OLLAMA_BASE_URL
OLLAMA_LLM_MODEL
OLLAMA_EMBEDDING_MODEL

CHROMA_PATH
CHROMA_COLLECTION_NAME

DOCUMENTS_PATH

CHUNK_SIZE
CHUNK_OVERLAP

RETRIEVAL_CANDIDATE_COUNT
RETRIEVAL_RESULT_COUNT
```

Do not hard-code these values elsewhere if a configuration setting already exists.

Never commit `.env`.

## Development Commands

Create a local environment file:

```bash
cp .env.example .env
```

Index documents:

```bash
python -m agent.index
```

Start interactive query mode:

```bash
python -m agent.main
```

Ask a single question:

```bash
python -m agent.main "What records must the partnership maintain?"
```

## Ollama

Ollama is expected to expose its API at the configured `OLLAMA_BASE_URL`.

The development environment currently uses:

```text
Generation model:
gemma3:12b

Embedding model:
nomic-embed-text
```

Do not assume these names are hard-coded. Read them from configuration.

Detailed Docker/NVIDIA setup instructions are available under `docs/`.

## Dependencies

Prefer minimal dependencies.

Before adding a package:

1. Check whether Python's standard library already provides the functionality.
2. Check whether an existing project dependency already provides it.
3. Prefer focused standalone integrations over large umbrella packages.
4. Explain why a new dependency is necessary.

In particular, avoid adding dependencies solely to replace simple application code.

## Legal Document Considerations

Legal documents have structure that generic text documents may not.

Be aware of:

* articles
* sections
* subsections
* defined terms
* exhibits
* schedules
* amendments
* cross-references
* tables of contents
* signature pages
* page labels versus physical PDF pages

Do not assume semantic similarity alone is sufficient to determine which provision governs a question.

A table of contents, for example, may be highly similar to a query while containing no substantive answer.

## Error Handling

Prefer explicit failures with useful messages.

Examples include:

* document directory does not exist
* no supported documents found
* PDF cannot be parsed
* Ollama is unavailable
* required model is unavailable
* Chroma cannot be opened
* no relevant evidence is retrieved
* structured model response cannot be validated

Do not silently swallow indexing, retrieval, or citation errors.

## Testing Philosophy

As the project evolves, prioritize tests around system behavior rather than only implementation details.

Important areas include:

### Indexing

* new documents are indexed
* unchanged documents are skipped
* modified documents replace old chunks
* duplicate vectors are not created
* metadata survives ingestion and chunking

### Retrieval

Given a known question, verify that the expected supporting clause appears within the top retrieved results.

### Grounding

Verify that questions unsupported by the indexed documents produce an insufficient-evidence response.

### Citations

Verify that:

* invalid source IDs are rejected
* citations correspond to retrieved chunks
* duplicate document/page citations are collapsed
* rendered citations come from metadata rather than generated text

## V2 Areas of Interest

Likely future work includes:

* section-aware legal document parsing
* article/section/subsection metadata
* table-of-contents detection
* hybrid keyword + semantic search
* retrieval reranking
* section-level citations
* multiple document formats
* structured extraction of parties and dates
* obligation extraction
* event extraction
* cross-document reasoning
* amendment and supersession awareness
* retrieval evaluation datasets
* RAG quality metrics
* LangGraph-based agent workflows

Do not implement all of these opportunistically.

Prefer incremental changes with measurable improvements over increasing architectural complexity.

## Guidance for Agentic Features

The current application is primarily a RAG system, not an autonomous agent.

Do not introduce LangGraph or multi-step agent loops simply to make the architecture more "agentic."

Agent orchestration becomes useful when the system needs to make decisions such as:

* whether another retrieval is necessary
* which document collection to search
* whether to inspect an amendment
* whether a referenced agreement must be retrieved
* whether structured metadata or semantic search is more appropriate

Until those behaviors are required, prefer the simpler deterministic RAG pipeline.

## When Making Changes

Before modifying the code:

1. Inspect the relevant existing modules.
2. Understand the current data flow.
3. Preserve provenance and citation behavior.
4. Reuse existing configuration.
5. Avoid unnecessary abstractions.
6. Keep indexing and querying separate.
7. Run or update relevant tests.
8. Update documentation when behavior or setup changes.

For substantial architectural changes, explain the proposed approach before modifying multiple modules.

## Project Philosophy

Optimize for:

**grounding > plausible answers**

**retrieval quality > prompt cleverness**

**validated provenance > model-generated citations**

**simple deterministic workflows > unnecessary agent complexity**

**local processing > external services**

The long-term goal is not merely to create a chatbot over PDFs. It is to build a reliable local system for researching relationships, obligations, events, dates, and other facts across collections of legal documents while preserving traceability back to the underlying evidence.
