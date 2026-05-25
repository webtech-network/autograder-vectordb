from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IngestResponse(BaseModel):
    assignment_id: str = Field(description="Assignment identifier used for metadata filtering.")
    file_count: int = Field(description="Number of uploaded files in this ingest request.")
    chunk_count: int = Field(description="Total number of chunks generated across all files.")
    upserted_count: int = Field(description="Total number of vectors upserted into Upstash.")


class IngestTextRequest(BaseModel):
    assignment_id: str = Field(
        ...,
        description="Assignment identifier used for metadata filtering.",
        examples=["cs101-a1"],
    )
    text: str = Field(
        ...,
        min_length=1,
        description="Raw text to split, embed, and store.",
    )
    source: str = Field(
        default="raw-text",
        description="Optional source label for metadata.",
    )


class IngestVectorInput(BaseModel):
    """Single vector input for assignment-based ingest."""

    id: str = Field(..., description="Unique ID for this vector.")
    vector: list[float] = Field(..., description="Pre-computed embedding vector.")
    metadata: dict[str, Any] | None = Field(default=None, description="Optional metadata.")
    data: str | None = Field(default=None, description="Optional text stored with the vector.")


class IngestVectorsRequest(BaseModel):
    assignment_id: str = Field(
        ...,
        description="Assignment identifier used for metadata filtering.",
        examples=["cs101-a1"],
    )
    vectors: list[IngestVectorInput] = Field(
        ...,
        min_length=1,
        description="Pre-computed embedding vectors to store.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assignment_id": "cs101-a1",
                "file_count": 2,
                "chunk_count": 26,
                "upserted_count": 26,
            }
        }
    )


class QueryRequest(BaseModel):
    assignment_id: str = Field(
        ...,
        description="Assignment key used to filter vector search results.",
        examples=["cs101-a1"],
    )
    question: str = Field(
        ...,
        min_length=1,
        description="Natural-language query from the autograder or user.",
        examples=["How should recursion depth be handled in this assignment?"],
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of top matching chunks to return.",
        examples=[5],
    )


class QueryResult(BaseModel):
    id: str = Field(description="Chunk ID from the vector index.")
    score: float = Field(description="Similarity score returned by Upstash Vector.")
    text: str | None = Field(
        default=None,
        description="Original chunk text when include_data is enabled in query.",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Chunk metadata (assignment_id, filename, chunk index, and model).",
    )


class QueryResponse(BaseModel):
    assignment_id: str = Field(description="Assignment ID used in this query.")
    question: str = Field(description="Original input question.")
    results: list[QueryResult] = Field(description="Ranked retrieval results.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assignment_id": "cs101-a1",
                "question": "What are the banned Python libraries for this task?",
                "results": [
                    {
                        "id": "cs101-a1-3fbc0f07f0-0-3324150f772e",
                        "score": 0.91,
                        "text": "Students may not use numpy or pandas for Assignment 1...",
                        "metadata": {
                            "assignment_id": "cs101-a1",
                            "filename": "assignment-spec.md",
                            "chunk_index": 0,
                            "chunk_id": "cs101-a1-3fbc0f07f0-0-3324150f772e",
                            "model_id": "text-embedding-3-small",
                        },
                    }
                ],
            }
        }
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
        default=384,
        ge=1,
        le=4096,
        description="Vector dimension. Must match your embedding model (default 384 for all-MiniLM-L12-v2).",
    )


class IndexResponse(BaseModel):
    name: str = Field(description="Index name.")
    dimension: int = Field(description="Vector dimension.")
    created_at: str = Field(description="ISO timestamp when the index was created.")


class ListIndexesResponse(BaseModel):
    indexes: list[IndexResponse] = Field(description="List of registered indexes.")


class VectorInput(BaseModel):
    id: str = Field(..., description="Unique ID for this vector.")
    vector: list[float] = Field(..., description="Embedding vector.")
    metadata: dict[str, Any] | None = Field(default=None, description="Optional metadata.")
    data: str | None = Field(default=None, description="Optional text/data stored with the vector.")


class TextInput(BaseModel):
    id: str = Field(..., description="Unique ID for this vector.")
    text: str = Field(..., description="Text to embed (service will generate the vector).")
    metadata: dict[str, Any] | None = Field(default=None, description="Optional metadata.")


class UpsertVectorsRequest(BaseModel):
    vectors: list[VectorInput] | None = Field(
        default=None,
        description="Pre-computed vectors to upsert.",
    )
    texts: list[TextInput] | None = Field(
        default=None,
        description="Texts to embed and upsert (alternative to vectors).",
    )


class UpsertVectorsResponse(BaseModel):
    index_name: str = Field(description="Index where vectors were upserted.")
    upserted_count: int = Field(description="Number of vectors upserted.")


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
