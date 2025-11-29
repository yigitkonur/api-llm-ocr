"""
FastAPI application factory.

Creates and configures the FastAPI application instance.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from swift_ocr import __version__
from swift_ocr.api.exceptions import register_exception_handlers
from swift_ocr.api.router import api_router
from swift_ocr.config import get_settings
from swift_ocr.core.logging import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    log_level = logging.DEBUG if settings.debug else logging.INFO
    setup_logging(level=log_level)
    
    logger.info(f"Starting Swift OCR v{__version__}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"OpenAI endpoint: {settings.azure_openai_endpoint}")
    logger.info(f"Batch size: {settings.batch_size}")
    logger.info(f"Max concurrent OCR requests: {settings.max_concurrent_ocr_requests}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Swift OCR")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title="Swift OCR API",
        description=(
            "LLM-powered OCR API that converts PDFs to beautifully formatted Markdown. "
            "Uses GPT-4 Vision for human-level text extraction with table preservation, "
            "header detection, and image descriptions."
        ),
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include API routes
    app.include_router(api_router)
    
    return app


# Create default app instance for uvicorn
app = create_app()
