from typing import Any

from upstash_vector import Index


class VectorStoreService:
    def __init__(self, url: str, token: str) -> None:
        if not url or not token:
            raise ValueError("UPSTASH_URL and UPSTASH_TOKEN must be configured.")
        self._index = Index(url=url, token=token)

    def upsert_chunks(
        self,
        chunks: list[str],
        vectors: list[list[float]],
        metadata_list: list[dict[str, Any]],
    ) -> int:
        payload = []
        for idx, (chunk, vector, metadata) in enumerate(
            zip(chunks, vectors, metadata_list, strict=True)
        ):
            chunk_id = metadata.get("chunk_id", f"chunk-{idx}")
            payload.append((chunk_id, vector, metadata, chunk))

        self._index.upsert(vectors=payload)
        return len(payload)

    def query(
        self,
        vector: list[float],
        assignment_id: str,
        top_k: int,
    ) -> list[dict[str, Any]]:
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
