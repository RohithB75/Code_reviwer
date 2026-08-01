from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse
from app.application.services.review_engine import ReviewParseError
from app.infrastructure.ollama_client import OllamaClientError, OllamaConnectionError, OllamaResponseError, OllamaTimeoutError

logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning("HTTP error on %s %s: %s", request.method, request.url.path, exc.detail)
        payload = ErrorResponse(error="http_error", message=str(exc.detail), details=None)
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("Validation error on %s %s", request.method, request.url.path)
        payload = ErrorResponse(
            error="validation_error",
            message="Request validation failed.",
            details=exc.errors(),
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        payload = ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred.",
            details=None,
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())

    @app.exception_handler(OllamaConnectionError)
    async def ollama_connection_exception_handler(request: Request, exc: OllamaConnectionError) -> JSONResponse:
        logger.warning("Ollama connection failure on %s %s: %s", request.method, request.url.path, exc)
        payload = ErrorResponse(error="ollama_connection_error", message=str(exc), details=None)
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload.model_dump())

    @app.exception_handler(OllamaTimeoutError)
    async def ollama_timeout_exception_handler(request: Request, exc: OllamaTimeoutError) -> JSONResponse:
        logger.warning("Ollama timeout on %s %s: %s", request.method, request.url.path, exc)
        payload = ErrorResponse(error="ollama_timeout_error", message=str(exc), details=None)
        return JSONResponse(status_code=status.HTTP_504_GATEWAY_TIMEOUT, content=payload.model_dump())

    @app.exception_handler(OllamaResponseError)
    async def ollama_response_exception_handler(request: Request, exc: OllamaResponseError) -> JSONResponse:
        logger.warning("Ollama response error on %s %s: %s", request.method, request.url.path, exc)
        payload = ErrorResponse(error="ollama_response_error", message=str(exc), details=None)
        return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload.model_dump())

    @app.exception_handler(OllamaClientError)
    async def ollama_client_exception_handler(request: Request, exc: OllamaClientError) -> JSONResponse:
        logger.warning("Ollama client error on %s %s: %s", request.method, request.url.path, exc)
        payload = ErrorResponse(error="ollama_client_error", message=str(exc), details=None)
        return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload.model_dump())

    @app.exception_handler(ReviewParseError)
    async def review_parse_exception_handler(request: Request, exc: ReviewParseError) -> JSONResponse:
        logger.warning("Review parse error on %s %s: %s", request.method, request.url.path, exc)
        payload = ErrorResponse(error="review_parse_error", message=str(exc), details=None)
        return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload.model_dump())