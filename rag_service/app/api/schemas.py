from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IngestResponse(BaseModel):
    assignment_id: str = Field(description="Assignment identifier used for metadata filtering.")
    file_count: int = Field(description="Number of uploaded files in this ingest request.")
    chunk_count: int = Field(description="Total number of chunks generated across all files.")
    upserted_count: int = Field(description="Total number of vectors upserted into Upstash.")

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
                            "model_id": "sentence-transformers/all-MiniLM-L12-v2",
                        },
                    }
                ],
            }
        }
    )
