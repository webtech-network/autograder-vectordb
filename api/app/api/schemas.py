from typing import Any

from pydantic import BaseModel, Field


# --- Ingestion schemas ---


class IngestResponse(BaseModel):
    index_name: str = Field(description="Index where vectors were upserted.")
    chunk_count: int = Field(description="Total number of chunks generated.")
    upserted_count: int = Field(description="Total number of vectors upserted.")


class IngestTextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Raw text to split, embed, and store.",
    )
    source: str = Field(
        default="raw-text",
        description="Optional source label for metadata.",
    )


# --- Index management schemas ---


class CreateIndexRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        description="Unique name for the index.",
        examples=["my-assignment-index"],
    )
    dimension: int = Field(
        default=768,
        ge=1,
        le=4096,
        description="Vector dimension. Must match your embedding model output.",
    )


class IndexResponse(BaseModel):
    name: str = Field(description="Index name.")
    dimension: int = Field(description="Vector dimension.")
    created_at: str = Field(description="ISO timestamp when the index was created.")


class ListIndexesResponse(BaseModel):
    indexes: list[IndexResponse] = Field(description="List of registered indexes.")


# --- Query schemas ---


class QueryIndexRequest(BaseModel):
    vector: list[float] | None = Field(
        default=None,
        description="Query vector for similarity search.",
    )
    text: str | None = Field(
        default=None,
        description="Text to embed and use as query (alternative to vector).",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum number of results to return.",
    )


class IndexQueryResult(BaseModel):
    id: str = Field(description="Vector ID.")
    score: float = Field(description="Similarity score.")
    text: str | None = Field(default=None, description="Stored data/text if present.")
    metadata: dict[str, Any] | None = Field(default=None, description="Vector metadata.")


class QueryIndexResponse(BaseModel):
    index_name: str = Field(description="Index that was queried.")
    results: list[IndexQueryResult] = Field(description="Ranked retrieval results.")
