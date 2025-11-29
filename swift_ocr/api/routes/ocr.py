"""
OCR API endpoints.

Provides endpoints for PDF to Markdown conversion.
"""

import asyncio
import time
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from swift_ocr.api.deps import OCRServiceDep, PDFServiceDep, SettingsDep
from swift_ocr.core.exceptions import (
    OCRProcessingError,
    PDFConversionError,
    PDFDownloadError,
    SwiftOCRError,
    ValidationError,
)
from swift_ocr.core.logging import get_logger
from swift_ocr.schemas import OCRRequest, OCRResponse, OCRStatus

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/ocr",
    response_model=OCRResponse,
    summary="Extract Text from PDF",
    description="Convert a PDF document to Markdown text using OCR. "
                "Provide either a file upload or a URL to a PDF.",
    responses={
        200: {"description": "Successfully extracted text"},
        400: {"description": "Invalid input (no file/URL or invalid PDF)"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal processing error"},
        504: {"description": "Timeout during processing"},
    },
)
async def ocr_endpoint(
    settings: SettingsDep,
    pdf_service: PDFServiceDep,
    ocr_service: OCRServiceDep,
    file: Optional[UploadFile] = File(None, description="PDF file to process"),
    url: Optional[str] = Form(None, description="URL of PDF to process"),
) -> OCRResponse:
    """
    Perform OCR on a PDF document.
    
    Accepts either:
    - A PDF file upload via multipart/form-data
    - A URL pointing to a PDF file
    
    Returns the extracted text in Markdown format.
    """
    start_time = time.perf_counter()
    
    try:
        # Validate input
        pdf_bytes = await _get_pdf_bytes(pdf_service, file, url)
        
        # Convert PDF to images
        logger.info("Converting PDF to images...")
        loop = asyncio.get_event_loop()
        pages = await loop.run_in_executor(
            None,
            pdf_service.convert_to_images,
            pdf_bytes,
        )
        
        if not pages:
            raise ValidationError("PDF contains no pages")
        
        # Encode images to base64
        page_images = pdf_service.encode_pages_to_base64(pages)
        
        # Perform OCR
        logger.info(f"Starting OCR on {len(page_images)} pages...")
        extracted_text = await ocr_service.process_pages(page_images)
        
        if not extracted_text:
            raise OCRProcessingError("OCR completed but no text was extracted")
        
        # Calculate processing time
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        logger.info(
            f"OCR complete: {len(extracted_text):,} chars from {len(pages)} pages "
            f"in {processing_time_ms}ms"
        )
        
        return OCRResponse(
            text=extracted_text,
            status=OCRStatus.SUCCESS,
            pages_processed=len(pages),
            processing_time_ms=processing_time_ms,
        )
        
    except SwiftOCRError as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in OCR endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during OCR processing",
        )


async def _get_pdf_bytes(
    pdf_service: PDFServiceDep,
    file: Optional[UploadFile],
    url: Optional[str],
) -> bytes:
    """
    Get PDF bytes from either file upload or URL.
    
    Args:
        pdf_service: PDF service instance
        file: Uploaded file (optional)
        url: URL to download from (optional)
        
    Returns:
        PDF file content as bytes
        
    Raises:
        ValidationError: If input is invalid
        PDFDownloadError: If download fails
    """
    # Validate that exactly one input is provided
    if not file and not url:
        raise ValidationError(
            "No PDF provided. Please upload a file or provide a URL.",
            field="file/url",
        )
    
    if file and url:
        raise ValidationError(
            "Please provide either a file or a URL, not both.",
            field="file/url",
        )
    
    if file:
        return await _read_uploaded_file(file)
    else:
        return pdf_service.download_pdf(url)


async def _read_uploaded_file(file: UploadFile) -> bytes:
    """
    Read and validate an uploaded PDF file.
    
    Args:
        file: Uploaded file
        
    Returns:
        PDF content as bytes
        
    Raises:
        ValidationError: If file is invalid
    """
    # Check content type
    content_type = file.content_type or ""
    if content_type and "pdf" not in content_type.lower():
        # Some clients don't send correct content-type, so we'll also check magic bytes
        pass
    
    try:
        pdf_bytes = await file.read()
    except Exception as e:
        raise ValidationError(
            f"Failed to read uploaded file: {e}",
            field="file",
        )
    
    if not pdf_bytes:
        raise ValidationError(
            "Uploaded file is empty",
            field="file",
        )
    
    # Check PDF magic bytes
    if not pdf_bytes.startswith(b"%PDF"):
        raise ValidationError(
            "Uploaded file is not a valid PDF",
            field="file",
        )
    
    logger.info(f"Read uploaded PDF: {len(pdf_bytes):,} bytes")
    return pdf_bytes
