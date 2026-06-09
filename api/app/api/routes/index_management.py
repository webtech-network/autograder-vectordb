"""Index management routes (CRUD operations for indexes)."""

from fastapi import APIRouter

from app.api.deps import get_vector_store_service
from app.api.errors import IndexAlreadyExistsError, IndexNotFoundError
from app.api.schemas import CreateIndexRequest, IndexResponse, ListIndexesResponse
from app.services.index_registry import (
    create_index as registry_create_index,
    delete_index as registry_delete_index,
    get_index as registry_get_index,
    list_indexes as registry_list_indexes,
)

router = APIRouter(prefix="/indexes", tags=["Index Management"])


@router.post(
    "",
    response_model=IndexResponse,
    summary="Create an index",
    description="Register a new index. Vectors must match the specified dimension.",
    responses={
        200: {"description": "Index created successfully."},
        400: {"description": "Index name already exists or invalid request."},
    },
)
async def create_index(request: CreateIndexRequest) -> IndexResponse:
    try:
        info = registry_create_index(name=request.name, dimension=request.dimension)
    except ValueError as e:
        raise IndexAlreadyExistsError(str(e))
    return IndexResponse(
        name=info.name,
        dimension=info.dimension,
        created_at=info.created_at,
    )


@router.get(
    "",
    response_model=ListIndexesResponse,
    summary="List indexes",
    description="List all registered indexes.",
)
async def list_indexes() -> ListIndexesResponse:
    indexes = registry_list_indexes()
    return ListIndexesResponse(
        indexes=[
            IndexResponse(name=i.name, dimension=i.dimension, created_at=i.created_at)
            for i in indexes
        ]
    )


@router.get(
    "/{index_name}",
    response_model=IndexResponse,
    summary="Get index",
    description="Get metadata for a specific index.",
    responses={
        404: {"description": "Index not found."},
    },
)
async def get_index(index_name: str) -> IndexResponse:
    info = registry_get_index(index_name)
    if info is None:
        raise IndexNotFoundError(f"Index '{index_name}' not found.")
    return IndexResponse(
        name=info.name,
        dimension=info.dimension,
        created_at=info.created_at,
    )


@router.delete(
    "/{index_name}",
    summary="Delete an index",
    description="Remove the index from the registry and delete all its vectors.",
    responses={
        200: {"description": "Index deleted successfully."},
        404: {"description": "Index not found."},
    },
)
async def delete_index(index_name: str) -> dict[str, str | int]:
    info = registry_get_index(index_name)
    if info is None:
        raise IndexNotFoundError(f"Index '{index_name}' not found.")
    vector_store = get_vector_store_service()
    deleted_count = vector_store.delete_by_index(index_name)
    registry_delete_index(index_name)
    return {"status": "deleted", "index_name": index_name, "vectors_deleted": deleted_count}


@router.delete(
    "/{index_name}/sources/{source}",
    summary="Delete vectors by source",
    description="Delete all vectors from a specific source within an index.",
    responses={
        200: {"description": "Vectors from source deleted successfully."},
        404: {"description": "Index not found."},
    },
)
async def delete_source(index_name: str, source: str) -> dict[str, str | int]:
    info = registry_get_index(index_name)
    if info is None:
        raise IndexNotFoundError(f"Index '{index_name}' not found.")
    vector_store = get_vector_store_service()
    deleted_count = vector_store.delete_by_source(index_name, source)
    return {"status": "deleted", "index_name": index_name, "source": source, "vectors_deleted": deleted_count}
