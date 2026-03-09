"""Simple file-based registry for index metadata."""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class IndexInfo:
    """Metadata for a registered index."""

    name: str
    dimension: int
    created_at: str


def _get_registry_path() -> Path:
    """Return the path to the indexes JSON file. Creates parent dir if needed."""
    data_dir = Path(os.getenv("INDEX_REGISTRY_DIR", "/tmp/rag_index_registry"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "indexes.json"


def _load_registry() -> dict[str, dict]:
    """Load the index registry from disk. Returns empty dict if file does not exist."""
    path = _get_registry_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_registry(registry: dict[str, dict]) -> None:
    """Persist the index registry to disk."""
    path = _get_registry_path()
    with open(path, "w") as f:
        json.dump(registry, f, indent=2)


def create_index(name: str, dimension: int) -> IndexInfo:
    """Register a new index in the registry.

    Args:
        name: Unique index name.
        dimension: Vector dimension for this index.

    Returns:
        IndexInfo for the created index.

    Raises:
        ValueError: If an index with the same name already exists.
    """
    registry = _load_registry()
    if name in registry:
        raise ValueError(f"Index '{name}' already exists.")
    from datetime import datetime, timezone

    info = IndexInfo(
        name=name,
        dimension=dimension,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    registry[name] = asdict(info)
    _save_registry(registry)
    return info


def get_index(name: str) -> IndexInfo | None:
    """Get index metadata by name.

    Args:
        name: Index name to look up.

    Returns:
        IndexInfo if found, None otherwise.
    """
    registry = _load_registry()
    data = registry.get(name)
    if data is None:
        return None
    return IndexInfo(**data)


def list_indexes() -> list[IndexInfo]:
    """List all registered indexes.

    Returns:
        List of IndexInfo for every index in the registry.
    """
    registry = _load_registry()
    return [IndexInfo(**data) for data in registry.values()]


def delete_index(name: str) -> bool:
    """Remove index from registry. Does not delete vectors in Upstash.

    Args:
        name: Index name to remove.

    Returns:
        True if the index existed and was removed, False if it was not found.
    """
    registry = _load_registry()
    if name not in registry:
        return False
    del registry[name]
    _save_registry(registry)
    return True
