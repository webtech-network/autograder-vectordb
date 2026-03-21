"""Centralized error handlers registered on the FastAPI app."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.errors.exceptions import (
    DimensionMismatchError,
    FileTooLargeError,
    IndexAlreadyExistsError,
    IndexNotFoundError,
    IngestionError,
    NoExtractableTextError,
    RAGServiceError,
    TooManyFilesError,
    VectorOperationError,
    VectorStoreError,
)


def register_error_handlers(app: FastAPI) -> None:
    """Register all centralized exception handlers on the app."""

    # --- Index Management ---

    @app.exception_handler(IndexNotFoundError)
    async def _index_not_found(request: Request, exc: IndexNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(IndexAlreadyExistsError)
    async def _index_exists(request: Request, exc: IndexAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    # --- Vector Ingestion ---

    @app.exception_handler(FileTooLargeError)
    async def _file_too_large(request: Request, exc: FileTooLargeError) -> JSONResponse:
        return JSONResponse(status_code=413, content={"detail": exc.detail})

    @app.exception_handler(TooManyFilesError)
    async def _too_many_files(request: Request, exc: TooManyFilesError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(NoExtractableTextError)
    async def _no_text(request: Request, exc: NoExtractableTextError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(DimensionMismatchError)
    async def _dim_mismatch(request: Request, exc: DimensionMismatchError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(IngestionError)
    async def _ingestion_error(request: Request, exc: IngestionError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    # --- Vector Operations ---

    @app.exception_handler(VectorOperationError)
    async def _vector_op_error(request: Request, exc: VectorOperationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    # --- Vector Store ---

    @app.exception_handler(VectorStoreError)
    async def _vector_store_error(request: Request, exc: VectorStoreError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": exc.detail})

    # --- Catch-all for any RAGServiceError subclass not handled above ---

    @app.exception_handler(RAGServiceError)
    async def _rag_service_error(request: Request, exc: RAGServiceError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": exc.detail})
