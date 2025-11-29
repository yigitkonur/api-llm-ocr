"""API module for Swift OCR."""

from swift_ocr.api.deps import get_ocr_service, get_pdf_service, get_settings
from swift_ocr.api.router import api_router

__all__ = [
    "api_router",
    "get_ocr_service",
    "get_pdf_service",
    "get_settings",
]
