"""Feature-specific exception classes."""


# --- Base ---


class RAGServiceError(Exception):
    """Base exception for all RAG service errors."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


# --- Index Management ---


class IndexNotFoundError(RAGServiceError):
    """Raised when a requested index does not exist."""


class IndexAlreadyExistsError(RAGServiceError):
    """Raised when creating an index that already exists."""


# --- Vector Ingestion ---


class IngestionError(RAGServiceError):
    """Base for ingestion-related errors."""


class FileTooLargeError(IngestionError):
    """Raised when an uploaded file exceeds the size limit."""


class TooManyFilesError(IngestionError):
    """Raised when too many files are sent in a single request."""


class NoExtractableTextError(IngestionError):
    """Raised when no text could be extracted from uploaded files."""


class DimensionMismatchError(IngestionError):
    """Raised when a vector dimension does not match the expected dimension."""


# --- Vector Operations ---


class VectorOperationError(RAGServiceError):
    """Base for query/search-related errors."""


# --- Vector Store ---


class VectorStoreError(RAGServiceError):
    """Raised when the underlying vector store (Upstash) fails."""
