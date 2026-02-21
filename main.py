"""
api-llm-ocr - Entry point for backward compatibility.

This file provides backward compatibility with the original API.
The main code is in the swift_ocr package.

Usage:
    uvicorn main:app --reload
    
Or use the new package directly:
    uvicorn swift_ocr.app:app --reload
    python -m swift_ocr
"""

from swift_ocr.app import app

__all__ = ["app"]
