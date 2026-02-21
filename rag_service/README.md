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
- **Document parsing:** `pypdf` for PDFs, UTF-8 decode fallback for text-like files
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
│   │   ├── routes.py          # /ingest and /query endpoints
│   │   └── schemas.py         # Pydantic request/response models
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
- `EMBEDDING_MODEL_ID`: model identifier used by `embed-anything`
- `CHUNK_SIZE`: target chunk length for splitting
- `CHUNK_OVERLAP`: overlap between adjacent chunks
- `TOP_K_DEFAULT`: default retrieval count (currently request-level `top_k` also supported)

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

Service URLs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

---

## API endpoints

### `GET /health`

Simple liveness probe.

Response:

```json
{
  "status": "ok"
}
```

### `POST /ingest`

Uploads files and ingests them into vector storage.

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
