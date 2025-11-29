"""
FastAPI dependencies for dependency injection.

Provides service instances and settings to route handlers.
"""

from functools import lru_cache
from typing import Annotated, Generator

from fastapi import Depends

from swift_ocr.config import Settings
from swift_ocr.config.settings import get_settings as _get_settings
from swift_ocr.services.ocr import OCRService
from swift_ocr.services.pdf import PDFService


def get_settings() -> Settings:
    """Get application settings."""
    return _get_settings()


@lru_cache
def get_pdf_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PDFService:
    """
    Get PDF service instance.
    
    Uses lru_cache to ensure single instance per settings configuration.
    """
    return PDFService(settings)


@lru_cache
def get_ocr_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> OCRService:
    """
    Get OCR service instance.
    
    Uses lru_cache to ensure single instance per settings configuration.
    """
    return OCRService(settings)


# Type aliases for cleaner dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
PDFServiceDep = Annotated[PDFService, Depends(get_pdf_service)]
OCRServiceDep = Annotated[OCRService, Depends(get_ocr_service)]
