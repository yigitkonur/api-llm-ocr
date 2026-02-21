"""Core utilities for api-llm-ocr."""

from swift_ocr.core.exceptions import (
    ApiLlmOcrError,
    PDFDownloadError,
    PDFConversionError,
    OCRProcessingError,
    RateLimitError,
    ValidationError,
)
from swift_ocr.core.logging import get_logger, setup_logging
from swift_ocr.core.retry import retry_with_backoff

__all__ = [
    "ApiLlmOcrError",
    "PDFDownloadError",
    "PDFConversionError",
    "OCRProcessingError",
    "RateLimitError",
    "ValidationError",
    "get_logger",
    "setup_logging",
    "retry_with_backoff",
]
