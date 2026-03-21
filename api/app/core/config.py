import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    upstash_url: str = os.getenv("UPSTASH_URL", "")
    upstash_token: str = os.getenv("UPSTASH_TOKEN", "")
    embedding_model_id: str = os.getenv(
        "EMBEDDING_MODEL_ID",
        "sentence-transformers/all-MiniLM-L12-v2",
    )
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k_default: int = int(os.getenv("TOP_K_DEFAULT", "5"))
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "512"))
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    max_files_per_request: int = int(os.getenv("MAX_FILES_PER_REQUEST", "10"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
