import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    upstash_url: str = os.getenv("UPSTASH_URL", "")
    upstash_token: str = os.getenv("UPSTASH_TOKEN", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model_id: str = os.getenv(
        "EMBEDDING_MODEL_ID",
        "text-embedding-3-small",
    )
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k_default: int = int(os.getenv("TOP_K_DEFAULT", "5"))
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    max_files_per_request: int = int(os.getenv("MAX_FILES_PER_REQUEST", "10"))

    # DynamoDB settings
    dynamodb_table_name: str = os.getenv("DYNAMODB_TABLE_NAME", "rag-index-registry")
    dynamodb_endpoint_url: str = os.getenv("DYNAMODB_ENDPOINT_URL", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")


def get_settings() -> Settings:
    return Settings()
