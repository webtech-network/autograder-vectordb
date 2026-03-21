"""Vector ingestion routes (CUD operations for vectors, no read)."""

import hashlib
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile

from app.api.schemas import (
    IngestResponse,
    IngestTextRequest,
    IngestVectorsRequest,
    UpsertVectorsRequest,
    UpsertVectorsResponse,
)
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

router = APIRouter(prefix="", tags=["Vector Ingestion"])


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest static assignment documents",
    description=(
        "Uploads assignment reference files, extracts text, splits into chunks, "
        "generates embeddings locally using embed-anything, and upserts vectors into Upstash."
    ),
    responses={
        200: {"description": "Documents were ingested and upserted successfully."},
        400: {"description": "Request was invalid, empty, or had no extractable text."},
    },
)
async def ingest_documents(
    assignment_id: str = Form(
        ...,
        description="Assignment identifier used in vector metadata and future query filtering.",
        examples=["cs101-a1"],
    ),
    files: list[UploadFile] = File(
        ...,
        description="One or more files (.md, .txt, .pdf, .docx) containing static assignment knowledge.",
    ),
) -> IngestResponse:
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

        chunks = splitter.split_text(extracted_text)
        file_hash = hashlib.sha1((upload.filename or "unknown").encode("utf-8")).hexdigest()[:10]
        for idx, chunk in enumerate(chunks):
            chunk_hash = hashlib.sha1(chunk.encode("utf-8")).hexdigest()[:12]
            chunk_id = f"{assignment_id}-{file_hash}-{idx}-{chunk_hash}"
            all_chunks.append(chunk)
            all_metadata.append(
                {
                    "assignment_id": assignment_id,
                    "filename": upload.filename or "unknown",
                    "chunk_index": idx,
                    "chunk_id": chunk_id,
                    "model_id": settings.embedding_model_id,
                }
            )

    if not all_chunks:
        raise NoExtractableTextError("No extractable text found in uploaded files.")

    vectors = embedding_service.embed_texts(all_chunks)
    upserted_count = vector_store.upsert_chunks(
        chunks=all_chunks,
        vectors=vectors,
        metadata_list=all_metadata,
    )

    return IngestResponse(
        assignment_id=assignment_id,
        file_count=len(files),
        chunk_count=len(all_chunks),
        upserted_count=upserted_count,
    )


@router.post(
    "/ingest/text",
    response_model=IngestResponse,
    summary="Ingest raw text",
    description=(
        "Accepts raw text, splits into chunks, generates embeddings, and upserts into Upstash "
        "filtered by assignment_id."
    ),
    responses={
        200: {"description": "Text was ingested successfully."},
        400: {"description": "Request was invalid or text was empty."},
    },
)
async def ingest_raw_text(request: IngestTextRequest) -> IngestResponse:
    settings: Settings = get_settings()
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
        chunk_id = f"{request.assignment_id}-{source_hash}-{idx}-{chunk_hash}"
        all_metadata.append(
            {
                "assignment_id": request.assignment_id,
                "filename": request.source,
                "chunk_index": idx,
                "chunk_id": chunk_id,
                "model_id": settings.embedding_model_id,
            }
        )

    vectors = embedding_service.embed_texts(chunks)
    upserted_count = vector_store.upsert_chunks(
        chunks=chunks,
        vectors=vectors,
        metadata_list=all_metadata,
    )

    return IngestResponse(
        assignment_id=request.assignment_id,
        file_count=0,
        chunk_count=len(chunks),
        upserted_count=upserted_count,
    )


@router.post(
    "/ingest/vectors",
    response_model=IngestResponse,
    summary="Ingest raw embeddings",
    description=(
        "Accepts pre-computed embedding vectors and upserts them into Upstash "
        "filtered by assignment_id. Vector dimension must match the configured embedding model."
    ),
    responses={
        200: {"description": "Vectors were ingested successfully."},
        400: {"description": "Invalid request or dimension mismatch."},
    },
)
async def ingest_raw_vectors(request: IngestVectorsRequest) -> IngestResponse:
    settings: Settings = get_settings()
    embedding_dim = settings.embedding_dimension
    vector_store = get_vector_store_service()

    payload: list[tuple[str, list[float], dict[str, Any] | None, str | None]] = []
    for v in request.vectors:
        if len(v.vector) != embedding_dim:
            raise DimensionMismatchError(
                f"Vector dimension {len(v.vector)} does not match expected {embedding_dim}."
            )
        meta = dict(v.metadata) if v.metadata else {}
        meta["model_id"] = settings.embedding_model_id
        payload.append((v.id, v.vector, meta, v.data))

    upserted_count = vector_store.upsert_assignment_vectors(
        assignment_id=request.assignment_id,
        vectors=payload,
    )

    return IngestResponse(
        assignment_id=request.assignment_id,
        file_count=0,
        chunk_count=len(request.vectors),
        upserted_count=upserted_count,
    )


@router.post(
    "/indexes/{index_name}/vectors",
    response_model=UpsertVectorsResponse,
    summary="Store embeddings in an index",
    description="Upsert vectors or texts (to be embedded) into an index.",
    responses={
        200: {"description": "Vectors upserted successfully."},
        400: {"description": "Invalid request (provide vectors or texts, not both)."},
        404: {"description": "Index not found."},
    },
)
async def upsert_vectors(index_name: str, request: UpsertVectorsRequest) -> UpsertVectorsResponse:
    info = registry_get_index(index_name)
    if info is None:
        raise IndexNotFoundError(f"Index '{index_name}' not found.")

    if request.vectors and request.texts:
        raise IngestionError("Provide either 'vectors' or 'texts', not both.")
    if not request.vectors and not request.texts:
        raise IngestionError("Provide either 'vectors' or 'texts'.")

    vector_store = get_vector_store_service()
    embedding_service = get_embedding_service()

    payload: list[tuple[str, list[float], dict[str, Any] | None, str | None]] = []

    if request.vectors:
        for v in request.vectors:
            if len(v.vector) != info.dimension:
                raise DimensionMismatchError(
                    f"Vector dimension {len(v.vector)} does not match index dimension {info.dimension}."
                )
            payload.append((v.id, v.vector, v.metadata, v.data))

    if request.texts:
        texts = [t.text for t in request.texts]
        vectors = embedding_service.embed_texts(texts)
        for t, vec in zip(request.texts, vectors, strict=True):
            if len(vec) != info.dimension:
                raise DimensionMismatchError(
                    f"Embedding dimension {len(vec)} does not match index dimension {info.dimension}."
                )
            payload.append((t.id, vec, t.metadata, t.text))

    upserted_count = vector_store.upsert_vectors(index_name, payload)
    return UpsertVectorsResponse(index_name=index_name, upserted_count=upserted_count)
