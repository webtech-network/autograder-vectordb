import hashlib
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.schemas import IngestResponse, QueryRequest, QueryResponse, QueryResult
from app.core.config import Settings, get_settings
from app.services.document_loader import DocumentLoaderService
from app.services.embedding import EmbeddingService
from app.services.text_splitter import TextSplitterService
from app.services.vector_store import VectorStoreService


router = APIRouter(prefix="", tags=["Knowledge Base"])


@lru_cache
def _get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(model_id=settings.embedding_model_id)


@lru_cache
def _get_vector_store_service() -> VectorStoreService:
    settings = get_settings()
    return VectorStoreService(url=settings.upstash_url, token=settings.upstash_token)


@lru_cache
def _get_text_splitter_service() -> TextSplitterService:
    settings = get_settings()
    return TextSplitterService(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest static assignment documents",
    description=(
        "Uploads assignment reference files, extracts text, splits into chunks, "
        "generates embeddings locally using embed-anything, and upserts vectors into Upstash."
    ),
    responses={
        200: {
            "description": "Documents were ingested and upserted successfully.",
        },
        400: {
            "description": "Request was invalid, empty, or had no extractable text.",
        },
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
        description="One or more files (.md, .txt, .pdf) containing static assignment knowledge.",
    ),
) -> IngestResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required.")

    settings: Settings = get_settings()
    embedding_service = _get_embedding_service()
    vector_store = _get_vector_store_service()
    splitter = _get_text_splitter_service()

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
        raise HTTPException(status_code=400, detail="No extractable text found in uploaded files.")

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
    "/query",
    response_model=QueryResponse,
    summary="Query assignment knowledge base",
    description=(
        "Embeds the input question locally and performs vector similarity search "
        "in Upstash filtered by assignment_id."
    ),
    responses={
        200: {
            "description": "Semantic search completed successfully.",
        },
        400: {
            "description": "Invalid query payload.",
        },
    },
)
async def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    embedding_service = _get_embedding_service()
    vector_store = _get_vector_store_service()

    query_vector = embedding_service.embed_text(request.question)
    matches = vector_store.query(
        vector=query_vector,
        assignment_id=request.assignment_id,
        top_k=request.top_k,
    )

    results = [
        QueryResult(
            id=item.get("id", ""),
            score=float(item.get("score", 0.0)),
            text=item.get("data"),
            metadata=item.get("metadata"),
        )
        for item in matches
    ]

    return QueryResponse(
        assignment_id=request.assignment_id,
        question=request.question,
        results=results,
    )
