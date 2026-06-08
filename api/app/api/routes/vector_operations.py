"""Vector operations routes — query a given index."""

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    IndexQueryResult,
    QueryIndexRequest,
    QueryIndexResponse,
)
from app.api.deps import get_embedding_service, get_vector_store_service
from app.services.index_registry import get_index as registry_get_index

router = APIRouter(prefix="/indexes", tags=["Vector Operations"])


@router.post(
    "/{index_name}/query",
    response_model=QueryIndexResponse,
    summary="Query an index",
    description="Semantic similarity search by text or vector. Returns top-k results.",
    responses={
        200: {"description": "Query completed successfully."},
        400: {"description": "Invalid request (provide vector or text, not both)."},
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
