"""
API router aggregating all route modules.
"""

from fastapi import APIRouter

from swift_ocr.api.routes import health, ocr

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(ocr.router, tags=["OCR"])
