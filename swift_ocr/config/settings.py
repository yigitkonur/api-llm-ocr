"""
Application settings using Pydantic Settings.

Supports loading from environment variables and .env files.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation.
    
    All settings can be overridden via environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # API Configuration
    app_name: str = Field(default="Swift OCR", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # OpenAI / Azure OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    azure_openai_endpoint: str = Field(..., description="Azure OpenAI endpoint URL")
    openai_deployment_id: str = Field(..., description="OpenAI deployment/model ID")
    openai_api_version: str = Field(default="2024-02-15-preview", description="OpenAI API version")
    
    # OCR Configuration
    batch_size: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of pages to process per OCR request (1-10)"
    )
    max_concurrent_ocr_requests: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum concurrent OCR API calls"
    )
    max_concurrent_pdf_conversion: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Maximum concurrent PDF page conversions"
    )
    
    # OCR Model Parameters
    ocr_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    ocr_max_tokens: int = Field(default=4000, ge=100, le=128000)
    ocr_top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    
    # Retry Configuration
    max_retries: int = Field(default=10, ge=1, le=50)
    retry_base_delay: float = Field(default=1.0, ge=0.1)
    retry_max_delay: float = Field(default=120.0, ge=1.0)
    
    # PDF Configuration
    pdf_zoom_factor: int = Field(default=2, ge=1, le=4, description="PDF rendering zoom factor")
    pdf_download_timeout: int = Field(default=30, ge=5, le=300, description="PDF download timeout in seconds")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    
    @field_validator("azure_openai_endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Ensure endpoint has proper format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Azure OpenAI endpoint must start with http:// or https://")
        return v.rstrip("/")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    Call `get_settings.cache_clear()` to reload.
    
    Returns:
        Settings: The application settings.
        
    Raises:
        ValidationError: If required settings are missing or invalid.
    """
    return Settings()
