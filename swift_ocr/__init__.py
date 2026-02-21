"""
api-llm-ocr - LLM-powered PDF to Markdown converter.

A high-performance OCR API that uses GPT-4 Vision to convert PDFs
into beautifully formatted Markdown.
"""

__version__ = "2.0.0"
__author__ = "Yiğit Konur"
__license__ = "AGPL-3.0"

from swift_ocr.app import create_app

__all__ = ["create_app", "__version__"]
