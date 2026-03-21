# Autograder RAG Service

`rag_service` is a standalone FastAPI microservice that provides a Retrieval-Augmented Generation (RAG) knowledge layer for the Autograder platform.

The service ingests static assignment knowledge (PDF/Markdown/Text), generates embeddings locally with `embed-anything`, and stores/query vectors in Upstash Vector.

---

## Why this service exists

The core Autograder can call this service to retrieve relevant assignment context before generating feedback.  
This improves answer grounding and consistency by using curated, static documents instead of dynamic student submissions.

---

## Architecture

### Design choices

- **Framework:** FastAPI (async endpoints)
- **Vector DB:** Upstash Vector (used as a pure vector store)
- **Embedding Engine:** `embed-anything` (local embedding generation)
- **Chunking:** `RecursiveCharacterTextSplitter` from `langchain-text-splitters`
- **Document parsing:** `pypdf` for PDFs (with OCR fallback via pdf2image + pytesseract), `python-docx` for DOCX, UTF-8 decode for text-like files
- **Ingestion strategy:** Static assignment data only (Hybrid Split strategy)

### Request flow

1. Client calls `POST /ingest` with `assignment_id` and files.
2. Service extracts text from each file.
3. Text is chunked into retrieval-friendly blocks.
4. Each chunk is embedded locally.
5. Raw vectors + metadata + chunk text are upserted into Upstash.
6. Client calls `POST /query` with `assignment_id` and `question`.
7. Service embeds the question locally and queries Upstash with metadata filter.
8. Top matches are returned with score, text, and metadata.

---

## Project layout

```text
rag_service/
├── app/
│   ├── main.py                # FastAPI app + OpenAPI metadata
│   ├── api/
│   │   ├── deps.py            # Shared dependencies (service getters)
│   │   ├── schemas.py         # Pydantic request/response models
│   │   └── routes/
│   │       ├── index_management.py   # CRUD for indexes
│   │       ├── vector_ingestion.py   # CUD for vectors (ingest, upsert)
│   │       └── vector_operations.py  # Search operations
│   ├── core/
│   │   └── config.py          # Environment-backed settings
│   └── services/
│       ├── embedding.py       # embed-anything wrapper
│       ├── vector_store.py    # Upstash vector operations
│       ├── document_loader.py # PDF/text extraction
│       └── text_splitter.py   # Chunking strategy
├── .env                       # Local runtime config
├── Dockerfile
└── requirements.txt
```

---

## Configuration

Create/update `rag_service/.env`:

```env
UPSTASH_URL=<your-upstash-vector-url>
UPSTASH_TOKEN=<your-upstash-token>
EMBEDDING_MODEL_ID=sentence-transformers/all-MiniLM-L12-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K_DEFAULT=5
```

### Environment variables

- `UPSTASH_URL`: Upstash Vector REST URL
- `UPSTASH_TOKEN`: Upstash Vector token
- `INDEX_REGISTRY_DIR`: Directory for index metadata (default: `/tmp/rag_index_registry`). Use a persistent path in production.
- `EMBEDDING_MODEL_ID`: model identifier used by `embed-anything`
- `CHUNK_SIZE`: target chunk length for splitting
- `CHUNK_OVERLAP`: overlap between adjacent chunks
- `TOP_K_DEFAULT`: default retrieval count (currently request-level `top_k` also supported)
- `MAX_FILE_SIZE_MB`: maximum allowed file size in MB for ingestion (default: `10`)
- `MAX_FILES_PER_REQUEST`: maximum number of files per ingestion request (default: `10`)

---

## Local development

From repository root:

```bash
cd rag_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**PDF OCR (optional):** For scanned PDF support, install system dependencies:

- **macOS:** `brew install poppler tesseract`
- **Ubuntu/Debian:** `apt-get install poppler-utils tesseract-ocr`

Service URLs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

---

## API endpoints

### Index management

Clients can create indexes and store/retrieve embeddings per index.

#### `POST /indexes`

Create a new index.

Request body:

```json
{
  "name": "my-assignment-index",
  "dimension": 384
}
```

- `name`: Unique index name
- `dimension`: Vector dimension (default 384 for all-MiniLM-L12-v2)

#### `GET /indexes`

List all registered indexes.

#### `GET /indexes/{index_name}`

Get metadata for a specific index.

#### `DELETE /indexes/{index_name}`

Delete an index and all its vectors.

#### `POST /indexes/{index_name}/vectors`

Store embeddings in an index. Provide either pre-computed vectors or texts to embed.

Request body (vectors):

```json
{
  "vectors": [
    {
      "id": "vec-1",
      "vector": [0.1, 0.2, ...],
      "metadata": {"source": "doc1"},
      "data": "Optional stored text"
    }
  ]
}
```

Request body (texts to embed):

```json
{
  "texts": [
    {
      "id": "vec-1",
      "text": "Content to embed",
      "metadata": {"source": "doc1"}
    }
  ]
}
```

#### `POST /indexes/{index_name}/query`

Retrieve similar embeddings. Provide either a query vector or text.

Request body:

```json
{
  "vector": [0.1, 0.2, ...],
  "top_k": 5
}
```

Or with text (service embeds it):

```json
{
  "text": "What libraries are disallowed?",
  "top_k": 5
}
```

---

### `GET /health`

Simple liveness probe.

Response:

```json
{
  "status": "ok"
}
```

### `POST /ingest`

Uploads files and ingests them into vector storage. Supports `.md`, `.txt`, `.pdf`, and `.docx`. PDFs use OCR fallback when text extraction yields little content (e.g. scanned documents).

- Content type: `multipart/form-data`
- Form fields:
  - `assignment_id` (string)
  - `files` (one or more files)

Example:

```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "assignment_id=cs101-a1" \
  -F "files=@./docs/assignment-spec.md" \
  -F "files=@./docs/grading-rubric.pdf"
```

Example response:

```json
{
  "assignment_id": "cs101-a1",
  "file_count": 2,
  "chunk_count": 26,
  "upserted_count": 26
}
```

### `POST /ingest/text`

Ingest raw text directly (no file upload). Text is split, embedded, and stored.

Request body:

```json
{
  "assignment_id": "cs101-a1",
  "text": "Your raw text content here...",
  "source": "raw-text"
}
```

- `assignment_id`: Assignment scope for metadata filtering
- `text`: Raw text to split and embed
- `source`: Optional label (default: `raw-text`)

### `POST /ingest/vectors`

Ingest pre-computed embedding vectors. Vector dimension must match the embedding model (default 384).

Request body:

```json
{
  "assignment_id": "cs101-a1",
  "vectors": [
    {
      "id": "vec-1",
      "vector": [0.1, 0.2, ...],
      "metadata": {"source": "api"},
      "data": "Optional stored text"
    }
  ]
}
```

### `POST /query`

Retrieves semantically similar chunks for a question scoped to one assignment.

Request body:

```json
{
  "assignment_id": "cs101-a1",
  "question": "What libraries are disallowed?",
  "top_k": 5
}
```

Example:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_id": "cs101-a1",
    "question": "What libraries are disallowed?",
    "top_k": 5
  }'
```

Example response:

```json
{
  "assignment_id": "cs101-a1",
  "question": "What libraries are disallowed?",
  "results": [
    {
      "id": "cs101-a1-3fbc0f07f0-0-3324150f772e",
      "score": 0.91,
      "text": "Students may not use numpy or pandas for Assignment 1...",
      "metadata": {
        "assignment_id": "cs101-a1",
        "filename": "assignment-spec.md",
        "chunk_index": 0,
        "chunk_id": "cs101-a1-3fbc0f07f0-0-3324150f772e",
        "model_id": "sentence-transformers/all-MiniLM-L12-v2"
      }
    }
  ]
}
```

---

## Swagger/OpenAPI documentation

OpenAPI docs are generated automatically by FastAPI and now include:

- endpoint tags, summaries, and descriptions
- request model descriptions and examples
- response model descriptions and examples
- endpoint-level error response descriptions for common failures

Use:

- `GET /docs` for Swagger UI
- `GET /openapi.json` for machine-readable OpenAPI schema

---

## Docker

Build and run:

```bash
cd rag_service
docker build -t autograder-rag-service .
docker run --rm -p 8000:8000 --env-file .env autograder-rag-service
```

---

## Notes and operational guidance

- Keep assignment IDs stable. They are the retrieval namespace via metadata filtering.
- Re-ingesting the same documents produces new chunk IDs if chunk content changes.
- This service currently supports text extraction from PDF and text-like files.
- For best retrieval quality, keep source docs clean and structured.

---

## Upload limits

File ingestion (`POST /ingest`) enforces the following limits:

- **Max file size:** 10 MB per file (configurable via `MAX_FILE_SIZE_MB`)
- **Max files per request:** 10 (configurable via `MAX_FILES_PER_REQUEST`)

Files exceeding the size limit are rejected with HTTP 413 before any processing occurs.

---

## Architecture decision: synchronous ingestion

The ingestion pipeline (upload → text extraction → chunking → embedding → upsert) runs synchronously within a single HTTP request. This was a deliberate choice given the current usage pattern:

- Ingestions are infrequent — instructors upload files only when creating or updating an activity.
- Concurrency is low — typically one instructor at a time per course.
- The upload size cap (10 MB) bounds memory usage and processing time.

**If usage patterns change** — e.g. a higher number of concurrent users, more frequent ingestions, or significantly larger files — this architecture would need to be refactored. The expected migration path would be: accept the upload, persist the file to object storage (e.g. S3), return a job ID immediately, and process asynchronously via a task queue. This would decouple upload latency from processing time and enable retries without re-uploading.
