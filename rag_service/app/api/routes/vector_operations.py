"""Vector operations routes (search operations)."""

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    IndexQueryResult,
    QueryIndexRequest,
    QueryIndexResponse,
    QueryRequest,
    QueryResponse,
    QueryResult,
)
from app.api.deps import get_embedding_service, get_vector_store_service
from app.services.index_registry import get_index as registry_get_index

router = APIRouter(prefix="", tags=["Vector Operations"])


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query assignment knowledge base",
    description=(
        "Embeds the input question locally and performs vector similarity search "
        "in Upstash filtered by assignment_id."
    ),
    responses={
        200: {"description": "Semantic search completed successfully."},
        400: {"description": "Invalid query payload."},
    },
)
async def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    embedding_service = get_embedding_service()
    vector_store = get_vector_store_service()

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


@router.post(
    "/indexes/{index_name}/query",
    response_model=QueryIndexResponse,
    summary="Retrieve embeddings from an index",
    description="Query by vector or text. Returns top-k similar vectors.",
    responses={
        200: {"description": "Query completed successfully."},
        400: {"description": "Invalid request (provide vector or text)."},
        404: {"description": "Index not found."},
    },
)
async def query_index(index_name: str, request: QueryIndexRequest) -> QueryIndexResponse:
    info = registry_get_index(index_name)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found.")

    if request.vector and request.text:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'vector' or 'text', not both.",
        )
    if not request.vector and not request.text:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'vector' or 'text'.",
        )

    vector_store = get_vector_store_service()
    embedding_service = get_embedding_service()

    if request.vector:
        query_vector = request.vector
        if len(query_vector) != info.dimension:
            raise HTTPException(
                status_code=400,
                detail=f"Vector dimension {len(query_vector)} does not match index dimension {info.dimension}.",
            )
    else:
        query_vector = embedding_service.embed_text(request.text or "")

    matches = vector_store.query_by_index(
        index_name=index_name,
        vector=query_vector,
        top_k=request.top_k,
    )

    results = [
        IndexQueryResult(
            id=item.get("id", ""),
            score=float(item.get("score", 0.0)),
            text=item.get("data"),
            metadata=item.get("metadata"),
        )
        for item in matches
    ]

    return QueryIndexResponse(index_name=index_name, results=results)
