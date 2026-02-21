"""
Custom exceptions for api-llm-ocr.

Provides a hierarchy of exceptions for better error handling and reporting.
"""

from typing import Any, Optional


class ApiLlmOcrError(Exception):
    """Base exception for all api-llm-ocr errors."""
    
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        detail: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.context:
            return f"{self.message} (context: {self.context})"
        return self.message


class ValidationError(ApiLlmOcrError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        ctx = context or {}
        if field:
            ctx["field"] = field
        super().__init__(message, status_code=400, context=ctx)


class PDFDownloadError(ApiLlmOcrError):
    """Raised when PDF download fails."""
    
    def __init__(
        self,
        message: str,
        *,
        url: Optional[str] = None,
        status_code: int = 400,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        ctx = context or {}
        if url:
            ctx["url"] = url
        super().__init__(message, status_code=status_code, context=ctx)


class PDFConversionError(ApiLlmOcrError):
    """Raised when PDF to image conversion fails."""
    
    def __init__(
        self,
        message: str,
        *,
        page_number: Optional[int] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        ctx = context or {}
        if page_number is not None:
            ctx["page_number"] = page_number
        super().__init__(message, status_code=500, context=ctx)


class OCRProcessingError(ApiLlmOcrError):
    """Raised when OCR processing fails."""
    
    def __init__(
        self,
        message: str,
        *,
        batch_info: Optional[str] = None,
        status_code: int = 500,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        ctx = context or {}
        if batch_info:
            ctx["batch_info"] = batch_info
        super().__init__(message, status_code=status_code, context=ctx)


class RateLimitError(ApiLlmOcrError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: Optional[float] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        ctx = context or {}
        if retry_after is not None:
            ctx["retry_after"] = retry_after
        super().__init__(message, status_code=429, context=ctx)


class TimeoutError(ApiLlmOcrError):
    """Raised when an operation times out."""
    
    def __init__(
        self,
        message: str = "Operation timed out",
        *,
        timeout_seconds: Optional[float] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        ctx = context or {}
        if timeout_seconds is not None:
            ctx["timeout_seconds"] = timeout_seconds
        super().__init__(message, status_code=504, context=ctx)
