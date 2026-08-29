# AI Agent Development Guide

This file provides context, architectural constraints, and development guidance for AI coding agents working on this repository.

Read this file before making changes. Inspect the existing implementation before proposing or modifying architecture.

## Project Overview

Legal Document Agent is a local-first RAG application for querying legal documents using natural language.

The application:

1. Ingests legal documents.
2. Extracts text and source metadata.
3. Splits documents into retrieval chunks.
4. Generates embeddings locally using Ollama.
5. Stores embeddings and metadata in Chroma.
6. Retrieves relevant chunks for a user's question.
7. Uses a locally hosted LLM to generate a grounded structured answer.
8. Validates citations against retrieved evidence.
9. Renders citations back to the original documents and PDF pages.

The system is intentionally designed so that document contents, embeddings, vector storage, retrieval, and LLM inference can remain local.

The goal is not merely to create a chatbot over PDFs. The long-term goal is to build a reliable local research system for identifying relationships, obligations, events, dates, and other facts across collections of legal documents while preserving traceability to the underlying evidence.

## Current Milestone

V1 is complete.

V1 supports:

* PDF ingestion
* Page-level provenance metadata
* Content-based document fingerprints
* Recursive text chunking
* Deterministic chunk/vector IDs
* Local Ollama embeddings
* Persistent Chroma storage
* Idempotent document indexing
* Semantic vector retrieval
* Duplicate retrieval filtering
* Local LLM inference
* Structured Pydantic responses
* Citation validation
* PDF page-level source citations
* Interactive CLI querying
* Single-query CLI execution
* Environment-based configuration

Future changes should preserve this functionality unless a change explicitly replaces or improves it.

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
* uv
* uv_build
* Docker

Do not introduce `langchain-community`.

Prefer standalone LangChain integration packages or direct library usage.

Examples of existing standalone integrations include:

* `langchain-ollama`
* `langchain-chroma`
* `langchain-text-splitters`

## Package and Project Structure

The repository uses a `src/` Python package layout.

```text
legal-doc-agent/
├── data/
│   └── documents/
├── docs/
├── images/
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── main.py
│       ├── index.py
│       ├── ingest.py
│       ├── chunking.py
│       ├── embeddings.py
│       ├── vectorstore.py
│       ├── retrieval.py
│       ├── llm.py
│       ├── models.py
│       ├── rag.py
│       └── settings.py
├── .env.example
├── AGENTS.md
├── pyproject.toml
├── uv.lock
└── README.md
```

`src/` is the source root. It is not part of the Python package name.

Use imports such as:

```python
from agent.settings import settings
```

### Module Responsibilities

`main.py`
: CLI entry point and query application orchestration.

`index.py`
: Discovers documents and coordinates indexing.

`ingest.py`
: Reads PDFs, extracts page text, calculates document fingerprints, and creates page-level LangChain `Document` objects with provenance metadata.

`chunking.py`
: Splits page documents into retrieval chunks while preserving metadata and assigning deterministic chunk IDs.

`embeddings.py`
: Configures the local Ollama embedding model.

`vectorstore.py`
: Creates or loads the persistent Chroma collection and contains vector-store-related helpers.

`retrieval.py`
: Performs semantic retrieval and retrieval-level processing such as deduplication.

`llm.py`
: Configures the local Ollama generation model.

`models.py`
: Contains Pydantic models used for structured responses.

`rag.py`
: Builds grounded context, invokes the LLM, validates citations, maps citations to retrieved evidence, and renders answers.

`settings.py`
: Contains typed application configuration backed by environment variables.

Keep these responsibilities separated. Do not move the entire pipeline into `main.py` or `index.py`.

## Architecture

Indexing and querying are intentionally separate workflows.

### Indexing

```text
PDF Documents
     │
     ▼
   pypdf
     │
     ▼
Page Documents + Metadata
     │
     ▼
Text Chunking
     │
     ▼
Ollama Embeddings
     │
     ▼
   Chroma
```

Documents should be indexed when the underlying document corpus changes.

Do not re-index documents during normal query execution.

### Querying

```text
User Question
     │
     ▼
Query Embedding
     │
     ▼
Chroma Vector Search
     │
     ▼
Candidate Chunks
     │
     ▼
Deduplication
     │
     ▼
Grounded Context
     │
     ▼
Local LLM
     │
     ▼
Structured Response
     │
     ▼
Citation Validation
     │
     ▼
Answer + Source References
```

## Architectural Invariants

The following behaviors are intentional. Treat them as invariants unless a task explicitly requires changing them.

### Keep Processing Local by Default

The project is local-first.

Do not introduce external hosted LLM, embedding, vector database, document-processing, or reranking APIs unless explicitly requested.

Legal document contents should not be transmitted to external services by default.

If a proposed feature requires sending document contents outside the local environment, call this out explicitly before implementing it.

### Preserve Provenance

Every retrieval chunk must retain enough metadata to trace it back to the original source.

At minimum, preserve:

* source
* filename
* document hash
* physical PDF page number
* chunk ID

Do not discard provenance during ingestion, chunking, indexing, retrieval, or generation.

Future section-aware parsing should add metadata such as article, section, subsection, or printed page label without replacing the existing provenance fields.

### Physical PDF Pages Are the V1 Citation Unit

V1 citations refer to physical PDF page numbers.

Do not silently replace these with printed page labels, section numbers, or model-generated page references.

If richer citation types are added later, retain a reliable mapping back to the physical PDF source.

### Retrieved Evidence Defines the Citation Namespace

Source IDs supplied to the LLM correspond to the documents in the retrieved evidence list for that invocation.

For example:

```text
[SOURCE 1] -> retrieved[0]
[SOURCE 2] -> retrieved[1]
[SOURCE 3] -> retrieved[2]
```

Citation IDs must be validated against that exact retrieved list.

Never map model-generated source IDs against:

* every indexed chunk
* every document in Chroma
* the original unfiltered candidate set when a different list was supplied to the model

This invariant is essential for citation correctness.

### Do Not Let the LLM Invent Citations

The LLM may identify which supplied sources support its answer.

The application owns citation validation, source mapping, and rendering.

Do not trust model-generated:

* filenames
* page numbers
* section numbers
* URLs
* document identifiers
* source identifiers

unless they are validated against application-controlled metadata.

Prefer deterministic application logic for provenance whenever possible.

### Ground Answers in Retrieved Evidence

The generation model must answer using only the evidence supplied for the current question.

When the evidence is insufficient, prefer an explicit insufficient-evidence response over a plausible but unsupported answer.

Do not weaken grounding behavior merely to increase answer coverage.

### Retrieval and Generation Are Separate Concerns

Do not assume prompt changes can compensate for poor retrieval.

When investigating an incorrect or incomplete answer, inspect the pipeline in this order:

1. What chunks were retrieved?
2. Do the retrieved chunks contain the necessary evidence?
3. Was the correct evidence ranked highly enough?
4. Was useful evidence removed during deduplication or filtering?
5. Only then inspect generation behavior.

Retrieval quality should remain testable independently of the LLM.

### Keep Indexing Idempotent

Re-running the indexer against unchanged documents must not create duplicate vectors.

Current behavior is:

```text
new document       -> index
unchanged document -> skip
modified document  -> remove old chunks and re-index
```

Document fingerprints are based on file contents.

Chunk/vector IDs should remain deterministic.

Changes to indexing logic must preserve the ability to safely run the indexer multiple times.

### Prefer Deterministic Application Logic

Use the LLM where semantic reasoning is useful.

Prefer normal Python code for:

* validation
* hashing
* source mapping
* citation rendering
* deduplication
* configuration
* filesystem operations
* deterministic indexing decisions

Do not move deterministic behavior into prompts without a clear reason.

## Configuration

Runtime configuration lives in:

```text
src/agent/settings.py
```

Configuration is loaded from environment variables using `pydantic-settings`.

`.env.example` is the canonical documentation for configurable values.

Current settings include:

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

Do not hard-code configurable values elsewhere when a corresponding setting exists.

When adding configuration:

1. Add the typed setting to `settings.py`.
2. Add the example/default to `.env.example` when appropriate.
3. Update documentation if users need to know about it.

Never commit `.env`.

## Python and Dependency Management

This project uses `uv` for Python environments, dependency management, locking, and command execution.

Do not use `pip`, `pipx`, Poetry, Conda, or `requirements.txt` for project dependency management.

Install and synchronize the project environment with:

```bash
uv sync
```

Add a runtime dependency with:

```bash
uv add <package>
```

Add a development dependency with:

```bash
uv add --dev <package>
```

Run Python commands through the project environment using `uv run`.

When dependencies change, update and commit both:

```text
pyproject.toml
uv.lock
```

The project uses `uv_build` as its Python build backend.

Do not introduce another build backend unless there is a concrete requirement that `uv_build` cannot satisfy.

## Development Commands

Create a local environment file if one does not already exist:

```bash
cp .env.example .env
```

Install/synchronize dependencies:

```bash
uv sync
```

Index documents:

```bash
uv run index-agent
```

Start interactive query mode:

```bash
uv run query-agent
```

Prefer the configured project entry points over `python -m` commands in documentation and examples.

## Ollama

Ollama is expected to expose its API at the configured `OLLAMA_BASE_URL`.

The default development configuration uses:

```text
Generation model:
gemma3:12b

Embedding model:
nomic-embed-text
```

Do not assume these model names are hard-coded. Read them from application configuration.

All LLM and embedding integrations should use the configured Ollama base URL.

Detailed Docker and NVIDIA setup instructions are available under `docs/`.

## Dependency Guidelines

Prefer a small dependency surface.

Before adding a package:

1. Check whether Python's standard library already provides the functionality.
2. Check whether an existing project dependency already provides it.
3. Prefer focused standalone packages over large umbrella dependencies.
4. Confirm that the dependency supports the project's Python version.
5. Explain why the new dependency is useful.
6. Add it using `uv add` or `uv add --dev`.

Avoid dependencies whose only purpose is replacing a small amount of straightforward application code.

Do not introduce `langchain-community`.

## Legal Document Considerations

Legal documents contain structure and relationships that generic text pipelines may miss.

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
* related agreements
* superseded provisions

Do not assume semantic similarity alone determines which provision governs a question.

For example, a table of contents may be highly similar to a query while containing no substantive evidence.

Similarly, a semantically relevant provision may have been modified or superseded by an amendment.

Future retrieval improvements should account for these characteristics without weakening provenance.

## Error Handling

Prefer explicit failures with actionable messages.

Important failure cases include:

* document directory does not exist
* no supported documents are found
* PDF cannot be parsed
* Ollama is unavailable
* required generation model is unavailable
* required embedding model is unavailable
* Chroma cannot be opened
* indexing fails
* no relevant evidence is retrieved
* structured model response cannot be validated
* citation IDs are invalid

Do not silently swallow indexing, retrieval, generation, or citation errors.

Avoid broad exception handling unless errors are re-raised or converted into useful application-level messages.

## Testing Philosophy

Prioritize tests around externally meaningful behavior and architectural invariants rather than only implementation details.

Tests should not require a live LLM when the behavior being tested can be isolated.

### Indexing

Verify that:

* new documents are indexed
* unchanged documents are skipped
* modified documents replace old chunks
* repeated indexing does not create duplicate vectors
* document hashes are stable
* chunk IDs are deterministic
* provenance metadata survives ingestion and chunking

### Retrieval

Given a known document corpus and question, verify that the expected supporting clause appears within the top retrieved results.

Retrieval tests should be separable from answer-generation tests where practical.

### Grounding

Verify that:

* answers are based on supplied evidence
* unsupported questions produce an insufficient-evidence response
* evidence supplied to the model is clearly associated with source IDs

### Citations

Verify that:

* invalid source IDs are rejected
* citation IDs map only to the retrieved evidence supplied to the model
* duplicate document/page citations are collapsed
* rendered filenames and page numbers come from metadata rather than generated text

### Configuration

When configuration behavior changes, verify:

* environment variables are loaded correctly
* defaults behave as expected
* paths are represented consistently
* application code does not duplicate configuration constants

## V2 Areas of Interest

Likely future work includes:

* section-aware legal document parsing
* article/section/subsection metadata
* table-of-contents detection and filtering
* hybrid keyword and semantic search
* retrieval reranking
* section- and clause-level citations
* additional document formats
* structured extraction of parties and dates
* obligation extraction
* event extraction
* cross-document reasoning
* amendment and supersession awareness
* retrieval evaluation datasets
* RAG quality metrics
* LangGraph-based agent workflows

Do not implement these opportunistically.

Prefer incremental changes with measurable improvements over increasing architectural complexity.

## Guidance for Agentic Features

The current application is primarily a deterministic RAG system, not an autonomous agent.

Do not introduce LangGraph, tool loops, planning loops, or multi-agent architecture simply to make the project more "agentic."

Agent orchestration becomes useful when the system must make meaningful decisions such as:

* whether additional retrieval is necessary
* which document or collection should be searched
* whether a referenced agreement should be retrieved
* whether an amendment needs to be inspected
* whether structured metadata or semantic search is more appropriate
* whether evidence from multiple documents must be reconciled

When introducing agentic behavior:

1. Identify the decision that cannot be handled cleanly by the existing deterministic pipeline.
2. Define the tools or state required to make that decision.
3. Preserve provenance across every tool call.
4. Keep deterministic validation outside the LLM.
5. Add evaluation or tests for the new behavior.

Until these behaviors are required, prefer the simpler RAG pipeline.

## Working With Documents

Legal documents used for local development live under:

````text
data/documents/
````

Actual legal documents should not be committed to Git.

Do not modify, delete, rename, or commit user documents unless explicitly requested.

Do not commit the generated Chroma database.

Treat document contents as potentially confidential even when working with sample documents.

## When Making Changes

Before modifying code:

1. Read this file.
2. Inspect the relevant existing modules and tests.
3. Understand the current data flow before proposing a replacement.
4. Preserve provenance and citation behavior.
5. Reuse existing configuration.
6. Keep indexing and querying separate.
7. Avoid unnecessary abstractions and dependencies.
8. Add or update relevant tests.
9. Run the relevant tests.
10. Update README, `.env.example`, or other documentation when user-visible behavior or setup changes.

For substantial architectural changes, explain the proposed approach before modifying multiple modules.

Do not perform unrelated refactors as part of a focused task unless they are necessary for the requested change.

## Definition of Done

For a typical code change, consider the work complete when:

* the requested behavior is implemented
* existing architectural invariants are preserved
* relevant tests pass
* new behavior has appropriate test coverage where practical
* provenance and citation behavior remain correct
* dependencies and `uv.lock` are updated when necessary
* configuration documentation is updated when necessary
* user-facing commands or behavior are reflected in the README when necessary
* no unrelated files or local legal documents are committed

## Project Philosophy

Optimize for:

**grounding > plausible answers**

**retrieval quality > prompt cleverness**

**validated provenance > model-generated citations**

**deterministic application logic > unnecessary LLM decisions**

**simple workflows > unnecessary agent complexity**

**local processing > external services**

Reliability and evidence traceability are more important than making the system appear more intelligent or autonomous.
