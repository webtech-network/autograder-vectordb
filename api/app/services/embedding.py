"""Service for generating text embeddings using OpenAI's API."""

from openai import OpenAI


class EmbeddingService:
    """Generates dense vector embeddings from text using OpenAI's embedding models."""

    def __init__(self, model_id: str, api_key: str, dimensions: int | None = None) -> None:
        """Initialize the embedding service.

        Args:
            model_id: OpenAI model identifier (e.g. text-embedding-3-small).
            api_key: OpenAI API key.
            dimensions: Optional output dimension (for models that support truncation).
        """
        self._model_id = model_id
        self._dimensions = dimensions
        self._client = OpenAI(api_key=api_key)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector.

        Args:
            text: Input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        response = self._client.embeddings.create(
            input=text,
            model=self._model_id,
            dimensions=self._dimensions,
        )
        return response.data[0].embedding

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings into vectors.

        Args:
            texts: List of input texts to embed.

        Returns:
            List of embedding vectors, one per input text. Empty list if texts is empty.
        """
        if not texts:
            return []
        response = self._client.embeddings.create(
            input=texts,
            model=self._model_id,
            dimensions=self._dimensions,
        )
        return [item.embedding for item in response.data]
