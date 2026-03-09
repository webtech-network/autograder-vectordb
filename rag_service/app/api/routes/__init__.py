"""API route modules."""

from app.api.routes.index_management import router as index_management_router
from app.api.routes.vector_ingestion import router as vector_ingestion_router
from app.api.routes.vector_operations import router as vector_operations_router

__all__ = [
    "index_management_router",
    "vector_ingestion_router",
    "vector_operations_router",
]
