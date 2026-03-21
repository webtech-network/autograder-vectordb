"""Service for generating text embeddings using embed-anything."""

from collections.abc import Iterable
from typing import Any

from embed_anything import EmbeddingModel, WhichModel, embed_query


class EmbeddingService:
    """Generates dense vector embeddings from text using a local embedding model."""

    def __init__(self, model_id: str) -> None:
        """Initialize the embedding model.

        Args:
            model_id: HuggingFace model identifier (e.g. sentence-transformers/all-MiniLM-L12-v2).
        """
        self._embedder = EmbeddingModel.from_pretrained_local(
            WhichModel.Bert,
            model_id=model_id,
        )

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector.

        Args:
            text: Input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        vectors = self.embed_texts([text])
        return vectors[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings into vectors.

        Args:
            texts: List of input texts to embed.

        Returns:
            List of embedding vectors, one per input text. Empty list if texts is empty.
        """
        if not texts:
            return []
        raw_embeddings = embed_query(texts, embedder=self._embedder)
        return [self._coerce_embedding(item) for item in raw_embeddings]

    @staticmethod
    def _coerce_embedding(item: Any) -> list[float]:
        """Normalize embed-anything output to a list of floats.

        Args:
            item: Raw embedding output (object with .embedding or iterable).

        Returns:
            List of floats.

        Raises:
            ValueError: If the output format is unsupported.
        """
        if hasattr(item, "embedding"):
            embedding = getattr(item, "embedding")
            return [float(value) for value in embedding]
        if isinstance(item, Iterable):
            return [float(value) for value in item]
        raise ValueError("Unsupported embedding output format from embed-anything.")
