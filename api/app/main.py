from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routes import (
    index_management_router,
    vector_ingestion_router,
    vector_operations_router,
)
from app.services.index_registry import _ensure_table_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_table_exists()
    yield


app = FastAPI(
    title="Autograder RAG Service",
    version="0.1.0",
    description=(
        "RAG microservice for assignment knowledge retrieval. "
        "Generates embeddings via OpenAI and stores vectors in Upstash Vector."
    ),
    lifespan=lifespan,
    contact={
        "name": "Autograder Platform Team",
    },
    openapi_tags=[
        {
            "name": "System",
            "description": "Health and system readiness endpoints.",
        },
        {
            "name": "Index Management",
            "description": "CRUD operations for indexes.",
        },
        {
            "name": "Vector Ingestion",
            "description": "Ingest PDF or text into an index.",
        },
        {
            "name": "Vector Operations",
            "description": "Query an index for similar content.",
        },
    ],
)

app.include_router(index_management_router)
app.include_router(vector_ingestion_router)
app.include_router(vector_operations_router)

register_error_handlers(app)


@app.get(
    "/health",
    tags=["System"],
    summary="Service health check",
    description="Returns a simple liveness status used by orchestrators and uptime checks.",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
