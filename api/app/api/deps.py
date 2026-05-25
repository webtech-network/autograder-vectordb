"""Shared dependencies for API route handlers."""

from app.core.config import get_settings
from app.services.embedding import EmbeddingService
from app.services.text_splitter import TextSplitterService
from app.services.vector_store import VectorStoreService


def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(
        model_id=settings.embedding_model_id,
        api_key=settings.openai_api_key,
        dimensions=settings.embedding_dimension,
    )


def get_vector_store_service() -> VectorStoreService:
    settings = get_settings()
    return VectorStoreService(url=settings.upstash_url, token=settings.upstash_token)


def get_text_splitter_service() -> TextSplitterService:
    settings = get_settings()
    return TextSplitterService(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
