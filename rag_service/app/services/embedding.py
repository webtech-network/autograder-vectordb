from collections.abc import Iterable
from typing import Any

from embed_anything import EmbeddingModel, WhichModel, embed_query


class EmbeddingService:
    def __init__(self, model_id: str) -> None:
        self._embedder = EmbeddingModel.from_pretrained_local(
            WhichModel.Bert,
            model_id=model_id,
        )

    def embed_text(self, text: str) -> list[float]:
        vectors = self.embed_texts([text])
        return vectors[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        raw_embeddings = embed_query(texts, embedder=self._embedder)
        return [self._coerce_embedding(item) for item in raw_embeddings]

    @staticmethod
    def _coerce_embedding(item: Any) -> list[float]:
        if hasattr(item, "embedding"):
            embedding = getattr(item, "embedding")
            return [float(value) for value in embedding]
        if isinstance(item, Iterable):
            return [float(value) for value in item]
        raise ValueError("Unsupported embedding output format from embed-anything.")
