"""
Pydantic schemas for OCR requests and responses.

Provides validated data models for the API.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class OCRStatus(str, Enum):
    """OCR processing status."""
    
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class OCRRequest(BaseModel):
    """Request model for OCR endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/document.pdf"
            }
        }
    )
    
    url: Optional[HttpUrl] = Field(
        default=None,
        description="URL of the PDF to process. Provide either this or upload a file."
    )


class PageImage(BaseModel):
    """Represents a single page image with metadata."""
    
    page_number: int = Field(..., ge=1, description="1-indexed page number")
    data_url: str = Field(..., description="Base64-encoded image data URL")
    
    @property
    def image_size(self) -> int:
        """Get approximate size of the image in bytes."""
        # Base64 encoding increases size by ~33%
        return int(len(self.data_url) * 0.75)


class OCRResponse(BaseModel):
    """Response model for successful OCR processing."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "# Document Title\n\nExtracted content...",
                "status": "success",
                "pages_processed": 5,
                "processing_time_ms": 1234
            }
        }
    )
    
    text: str = Field(..., description="Extracted text in Markdown format")
    status: OCRStatus = Field(
        default=OCRStatus.SUCCESS,
        description="Processing status"
    )
    pages_processed: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of pages processed"
    )
    processing_time_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Processing time in milliseconds"
    )


class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(default=None, description="Error code")
    context: Optional[dict] = Field(default=None, description="Additional context")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "No PDF file or URL provided",
                "error": {
                    "message": "No PDF file or URL provided",
                    "code": "VALIDATION_ERROR"
                }
            }
        }
    )
    
    detail: str = Field(..., description="Error message")
    error: Optional[ErrorDetail] = Field(default=None, description="Detailed error info")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    )
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Current server time"
    )
    openai_configured: bool = Field(
        default=True,
        description="Whether OpenAI is properly configured"
    )
