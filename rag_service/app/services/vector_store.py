"""Service for vector storage and retrieval using Upstash Vector."""

from typing import Any

from upstash_vector import Index


def _escape_filter_value(value: str) -> str:
    """Escape single quotes for Upstash filter strings."""
    return value.replace("'", "\\'")


class VectorStoreService:
    """Manages vector upserts, queries, and deletes in Upstash Vector."""

    def __init__(self, url: str, token: str) -> None:
        """Initialize the Upstash Vector client.

        Args:
            url: Upstash Vector REST URL.
            token: Upstash Vector REST token.

        Raises:
            ValueError: If url or token is empty.
        """
        if not url or not token:
            raise ValueError("UPSTASH_URL and UPSTASH_TOKEN must be configured.")
        self._index = Index(url=url, token=token)

    def upsert_chunks(
        self,
        chunks: list[str],
        vectors: list[list[float]],
        metadata_list: list[dict[str, Any]],
    ) -> int:
        """Upsert document chunks with embeddings and metadata (assignment-based flow).

        Args:
            chunks: List of chunk texts (stored as data).
            vectors: List of embedding vectors, one per chunk.
            metadata_list: List of metadata dicts (e.g. assignment_id, chunk_id).

        Returns:
            Number of vectors upserted.
        """
        payload = []
        for idx, (chunk, vector, metadata) in enumerate(
            zip(chunks, vectors, metadata_list, strict=True)
        ):
            chunk_id = metadata.get("chunk_id", f"chunk-{idx}")
            payload.append((chunk_id, vector, metadata, chunk))

        self._index.upsert(vectors=payload)
        return len(payload)

    def upsert_assignment_vectors(
        self,
        assignment_id: str,
        vectors: list[tuple[str, list[float], dict[str, Any] | None, str | None]],
    ) -> int:
        """Upsert pre-computed vectors with assignment_id metadata (assignment-based flow).

        Args:
            assignment_id: Metadata filter for assignment scope.
            vectors: List of (id, vector, metadata, data) tuples.

        Returns:
            Number of vectors upserted.
        """
        payload = []
        for vec_id, vector, metadata, data in vectors:
            meta = dict(metadata) if metadata else {}
            meta["assignment_id"] = assignment_id
            payload.append((vec_id, vector, meta, data))

        self._index.upsert(vectors=payload)
        return len(payload)

    def query(
        self,
        vector: list[float],
        assignment_id: str,
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Query vectors filtered by assignment_id (assignment-based flow).

        Args:
            vector: Query embedding vector.
            assignment_id: Metadata filter for assignment scope.
            top_k: Maximum number of results to return.

        Returns:
            List of matches with id, score, metadata, and data.
        """
        response = self._index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            include_data=True,
            filter=f"assignment_id = '{assignment_id}'",
        )

        results: list[dict[str, Any]] = []
        for item in response:
            if hasattr(item, "to_dict"):
                results.append(item.to_dict())  # type: ignore[no-any-return]
                continue
            if isinstance(item, dict):
                results.append(item)
                continue
            results.append(
                {
                    "id": getattr(item, "id", ""),
                    "score": float(getattr(item, "score", 0.0)),
                    "metadata": getattr(item, "metadata", None),
                    "data": getattr(item, "data", None),
                }
            )
        return results

    def upsert_vectors(
        self,
        index_name: str,
        vectors: list[tuple[str, list[float], dict[str, Any] | None, str | None]],
    ) -> int:
        """Upsert vectors into an index (index management flow).

        Args:
            index_name: Logical index name (stored in metadata).
            vectors: List of (id, vector, metadata, data) tuples.

        Returns:
            Number of vectors upserted.
        """
        payload = []
        for vec_id, vector, metadata, data in vectors:
            meta = dict(metadata) if metadata else {}
            meta["index_name"] = index_name
            payload.append((vec_id, vector, meta, data))

        self._index.upsert(vectors=payload)
        return len(payload)

    def query_by_index(
        self,
        index_name: str,
        vector: list[float],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Query vectors filtered by index_name (index management flow).

        Args:
            index_name: Logical index name to filter by.
            vector: Query embedding vector.
            top_k: Maximum number of results to return.

        Returns:
            List of matches with id, score, metadata, and data.
        """
        response = self._index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            include_data=True,
            filter=f"index_name = '{_escape_filter_value(index_name)}'",
        )

        results: list[dict[str, Any]] = []
        for item in response:
            if hasattr(item, "to_dict"):
                results.append(item.to_dict())  # type: ignore[no-any-return]
                continue
            if isinstance(item, dict):
                results.append(item)
                continue
            results.append(
                {
                    "id": getattr(item, "id", ""),
                    "score": float(getattr(item, "score", 0.0)),
                    "metadata": getattr(item, "metadata", None),
                    "data": getattr(item, "data", None),
                }
            )
        return results

    def delete_by_index(self, index_name: str) -> int:
        """Delete all vectors in an index. Returns number of deleted vectors."""
        response = self._index.delete(filter=f"index_name = '{_escape_filter_value(index_name)}'")
        return int(response.get("deleted", 0))
