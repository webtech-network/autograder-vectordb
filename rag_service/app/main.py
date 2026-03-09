from fastapi import FastAPI

from app.api.routes import (
    index_management_router,
    vector_ingestion_router,
    vector_operations_router,
)


app = FastAPI(
    title="Autograder RAG Service",
    version="0.1.0",
    description=(
        "RAG microservice for static assignment knowledge retrieval. "
        "This service generates embeddings locally using embed-anything and "
        "stores raw vectors in Upstash Vector."
    ),
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
            "description": "Create, update, and delete vectors (no read).",
        },
        {
            "name": "Vector Operations",
            "description": "Search operations for vectors.",
        },
    ],
)

app.include_router(index_management_router)
app.include_router(vector_ingestion_router)
app.include_router(vector_operations_router)


@app.get(
    "/health",
    tags=["System"],
    summary="Service health check",
    description="Returns a simple liveness status used by orchestrators and uptime checks.",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
