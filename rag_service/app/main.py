from fastapi import FastAPI

from app.api.routes import router as api_router


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
            "name": "Knowledge Base",
            "description": "Document ingestion and semantic retrieval endpoints.",
        },
    ],
)

app.include_router(api_router)


@app.get(
    "/health",
    tags=["System"],
    summary="Service health check",
    description="Returns a simple liveness status used by orchestrators and uptime checks.",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
