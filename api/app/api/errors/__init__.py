"""Centralized error handling: feature-specific exceptions and handlers."""

from app.api.errors.exceptions import (
    IndexAlreadyExistsError,
    IndexNotFoundError,
    IngestionError,
    FileTooLargeError,
    TooManyFilesError,
    NoExtractableTextError,
    DimensionMismatchError,
    VectorOperationError,
    VectorStoreError,
)
from app.api.errors.handlers import register_error_handlers

__all__ = [
    "IndexAlreadyExistsError",
    "IndexNotFoundError",
    "IngestionError",
    "FileTooLargeError",
    "TooManyFilesError",
    "NoExtractableTextError",
    "DimensionMismatchError",
    "VectorOperationError",
    "VectorStoreError",
    "register_error_handlers",
]
