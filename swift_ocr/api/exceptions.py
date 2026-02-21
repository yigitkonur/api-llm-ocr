"""
Exception handlers for FastAPI.

Provides consistent error responses across the application.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from swift_ocr.core.exceptions import ApiLlmOcrError
from swift_ocr.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(ApiLlmOcrError)
    async def api_llm_ocr_error_handler(
        request: Request,
        exc: ApiLlmOcrError,
    ) -> JSONResponse:
        """Handle api-llm-ocr custom exceptions."""
        logger.error(
            f"ApiLlmOcrError: {exc.message}",
            extra={"context": exc.context, "status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error": {
                    "message": exc.message,
                    "type": type(exc).__name__,
                    "context": exc.context if exc.context else None,
                },
            },
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions."""
        logger.error(f"HTTPException: {exc.detail}", extra={"status_code": exc.status_code})
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_handler(
        request: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.error(f"ValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
            },
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle any unhandled exceptions."""
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred. Please try again later.",
            },
        )
