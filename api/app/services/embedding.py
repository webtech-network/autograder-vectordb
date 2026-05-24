"""Service for generating text embeddings using sentence-transformers."""

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Generates dense vector embeddings from text using a local embedding model."""

    def __init__(self, model_id: str) -> None:
        """Initialize the embedding model.

        Args:
            model_id: HuggingFace model identifier (e.g. sentence-transformers/all-MiniLM-L12-v2).
        """
        self._model = SentenceTransformer(model_id)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector.

        Args:
            text: Input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        embedding = self._model.encode(text)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings into vectors.

        Args:
            texts: List of input texts to embed.

        Returns:
            List of embedding vectors, one per input text. Empty list if texts is empty.
        """
        if not texts:
            return []
        embeddings = self._model.encode(texts)
        return embeddings.tolist()
