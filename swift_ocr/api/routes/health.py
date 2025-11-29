"""
Health check endpoints.

Provides endpoints for monitoring application health.
"""

from datetime import datetime

from fastapi import APIRouter

from swift_ocr import __version__
from swift_ocr.api.deps import SettingsDep
from swift_ocr.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the service is healthy and properly configured.",
)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """
    Perform a health check.
    
    Returns:
        HealthResponse with current status and configuration info.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow(),
        openai_configured=bool(
            settings.openai_api_key
            and settings.azure_openai_endpoint
            and settings.openai_deployment_id
        ),
    )


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Root Health Check",
    description="Root endpoint returning health status.",
    include_in_schema=False,
)
async def root_health(settings: SettingsDep) -> HealthResponse:
    """Root endpoint redirecting to health check."""
    return await health_check(settings)
