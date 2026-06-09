"""Vector ingestion routes — ingest PDF or text into a given index."""

import hashlib
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile

from app.api.schemas import IngestResponse, IngestTextRequest
from app.api.deps import (
    get_embedding_service,
    get_text_splitter_service,
    get_vector_store_service,
)
from app.api.errors import (
    DimensionMismatchError,
    FileTooLargeError,
    IndexNotFoundError,
    IngestionError,
    NoExtractableTextError,
    TooManyFilesError,
)
from app.core.config import Settings, get_settings
from app.services.document_loader import DocumentLoaderService
from app.services.index_registry import get_index as registry_get_index

router = APIRouter(prefix="/indexes", tags=["Vector Ingestion"])


@router.post(
    "/{index_name}/ingest/pdf",
    response_model=IngestResponse,
    summary="Ingest PDF documents into an index",
    description=(
        "Uploads PDF files, extracts text, splits into chunks, "
        "generates embeddings via OpenAI, and upserts vectors into the specified index. "
        "Each file's name is used as the source identifier."
    ),
    responses={
        200: {"description": "Documents were ingested and upserted successfully."},
        400: {"description": "Request was invalid, empty, or had no extractable text."},
        404: {"description": "Index not found."},
    },
)
async def ingest_pdf(
    index_name: str,
    files: list[UploadFile] = File(
        ...,
        description="One or more PDF files to ingest.",
    ),
    source: str | None = Form(
        default=None,
        description="Optional source identifier. If omitted, each file's name is used.",
    ),
) -> IngestResponse:
    info = registry_get_index(index_name)
    if info is None:
        raise IndexNotFoundError(f"Index '{index_name}' not found.")

    if not files:
        raise IngestionError("At least one file is required.")

    settings: Settings = get_settings()
    max_bytes = settings.max_file_size_mb * 1024 * 1024

    if len(files) > settings.max_files_per_request:
        raise TooManyFilesError(
            f"Too many files. Maximum is {settings.max_files_per_request} per request."
        )

    for upload in files:
        if upload.size is not None and upload.size > max_bytes:
            raise FileTooLargeError(
                f"File '{upload.filename}' exceeds the {settings.max_file_size_mb}MB limit."
            )
        if not (upload.filename or "").lower().endswith(".pdf"):
            raise IngestionError(f"File '{upload.filename}' is not a PDF.")

    embedding_service = get_embedding_service()
    vector_store = get_vector_store_service()
    splitter = get_text_splitter_service()

    all_chunks: list[str] = []
    all_metadata: list[dict[str, Any]] = []

    for upload in files:
        content = await upload.read()
        extracted_text = DocumentLoaderService.extract_text(upload.filename or "unknown", content)
        if not extracted_text.strip():
            continue

        file_source = source or (upload.filename or "unknown")
        chunks = splitter.split_text(extracted_text)
        source_hash = hashlib.sha1(file_source.encode("utf-8")).hexdigest()[:10]
        for idx, chunk in enumerate(chunks):
            chunk_hash = hashlib.sha1(chunk.encode("utf-8")).hexdigest()[:12]
            chunk_id = f"{index_name}-{source_hash}-{idx}-{chunk_hash}"
            all_chunks.append(chunk)
            all_metadata.append(
                {
                    "index_name": index_name,
                    "source": file_source,
                    "chunk_index": idx,
                    "chunk_id": chunk_id,
                }
            )

    if not all_chunks:
        raise NoExtractableTextError("No extractable text found in uploaded files.")

    vectors = embedding_service.embed_texts(all_chunks)

    payload: list[tuple[str, list[float], dict[str, Any] | None, str | None]] = []
    for chunk, vector, metadata in zip(all_chunks, vectors, all_metadata, strict=True):
        if len(vector) != info.dimension:
            raise DimensionMismatchError(
                f"Embedding dimension {len(vector)} does not match index dimension {info.dimension}."
            )
        payload.append((metadata["chunk_id"], vector, metadata, chunk))

    upserted_count = vector_store.upsert_vectors(index_name, payload)

    return IngestResponse(
        index_name=index_name,
        source=all_metadata[0]["source"] if all_metadata else "",
        chunk_count=len(all_chunks),
        upserted_count=upserted_count,
    )


@router.post(
    "/{index_name}/ingest/text",
    response_model=IngestResponse,
    summary="Ingest raw text into an index",
    description=(
        "Accepts raw text, splits into chunks, generates embeddings via OpenAI, "
        "and upserts vectors into the specified index."
    ),
    responses={
        200: {"description": "Text was ingested successfully."},
        400: {"description": "Request was invalid or text was empty."},
        404: {"description": "Index not found."},
    },
)
async def ingest_text(index_name: str, request: IngestTextRequest) -> IngestResponse:
    info = registry_get_index(index_name)
    if info is None:
        raise IndexNotFoundError(f"Index '{index_name}' not found.")

    embedding_service = get_embedding_service()
    vector_store = get_vector_store_service()
    splitter = get_text_splitter_service()

    chunks = splitter.split_text(request.text)
    if not chunks:
        raise IngestionError("No chunks produced from text.")

    source_hash = hashlib.sha1(request.source.encode("utf-8")).hexdigest()[:10]
    all_metadata: list[dict[str, Any]] = []
    for idx, chunk in enumerate(chunks):
        chunk_hash = hashlib.sha1(chunk.encode("utf-8")).hexdigest()[:12]
        chunk_id = f"{index_name}-{source_hash}-{idx}-{chunk_hash}"
        all_metadata.append(
            {
                "index_name": index_name,
                "source": request.source,
                "chunk_index": idx,
                "chunk_id": chunk_id,
            }
        )

    vectors = embedding_service.embed_texts(chunks)

    payload: list[tuple[str, list[float], dict[str, Any] | None, str | None]] = []
    for chunk, vector, metadata in zip(chunks, vectors, all_metadata, strict=True):
        if len(vector) != info.dimension:
            raise DimensionMismatchError(
                f"Embedding dimension {len(vector)} does not match index dimension {info.dimension}."
            )
        payload.append((metadata["chunk_id"], vector, metadata, chunk))

    upserted_count = vector_store.upsert_vectors(index_name, payload)

    return IngestResponse(
        index_name=index_name,
        source=request.source,
        chunk_count=len(chunks),
        upserted_count=upserted_count,
    )
