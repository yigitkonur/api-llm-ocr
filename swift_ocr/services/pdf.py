"""
PDF processing service.

Handles PDF download, conversion to images, and encoding.
"""

import base64
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
import requests

from swift_ocr.config import Settings
from swift_ocr.core.exceptions import PDFConversionError, PDFDownloadError
from swift_ocr.core.logging import get_logger
from swift_ocr.schemas import PageImage

logger = get_logger(__name__)


@dataclass
class PDFPage:
    """Represents a rendered PDF page."""
    
    page_number: int  # 1-indexed
    image_bytes: bytes
    
    @property
    def size_bytes(self) -> int:
        return len(self.image_bytes)


def _convert_single_page(args: Tuple[str, int, int]) -> Tuple[int, bytes]:
    """
    Convert a single PDF page to PNG image bytes.
    
    This function runs in a separate process for parallelization.
    
    Args:
        args: Tuple of (pdf_path, page_index, zoom_factor)
        
    Returns:
        Tuple of (page_number, image_bytes) where page_number is 1-indexed
    """
    pdf_path, page_index, zoom = args
    
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_index)
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix)
        image_bytes = pixmap.tobytes("png")
        doc.close()
        return (page_index + 1, image_bytes)  # Convert to 1-indexed
    except Exception as e:
        raise PDFConversionError(
            f"Failed to render page {page_index + 1}",
            page_number=page_index + 1,
            context={"error": str(e)},
        )


class PDFService:
    """
    Service for PDF processing operations.
    
    Handles downloading, converting to images, and encoding PDFs.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize PDF service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self._temp_files: List[str] = []
    
    def download_pdf(self, url: str) -> bytes:
        """
        Download a PDF file from a URL.
        
        Args:
            url: URL of the PDF file
            
        Returns:
            PDF file content as bytes
            
        Raises:
            PDFDownloadError: If download fails or content is not a PDF
        """
        logger.info(f"Downloading PDF from: {url}")
        
        try:
            response = requests.get(
                str(url),
                timeout=self.settings.pdf_download_timeout,
                headers={"User-Agent": "api-llm-ocr/2.0"},
            )
            response.raise_for_status()
            
            content_type = response.headers.get("Content-Type", "")
            if "application/pdf" not in content_type.lower():
                # Some servers don't set content-type correctly, check magic bytes
                if not response.content.startswith(b"%PDF"):
                    logger.warning(f"Invalid content type: {content_type}")
                    raise PDFDownloadError(
                        "URL does not point to a valid PDF file",
                        url=url,
                        context={"content_type": content_type},
                    )
            
            logger.info(f"Downloaded PDF: {len(response.content):,} bytes")
            return response.content
            
        except requests.exceptions.Timeout:
            raise PDFDownloadError(
                "Timeout while downloading PDF",
                url=url,
                status_code=504,
            )
        except requests.exceptions.HTTPError as e:
            raise PDFDownloadError(
                f"HTTP error while downloading PDF: {e}",
                url=url,
                status_code=getattr(e.response, "status_code", 400),
            )
        except requests.exceptions.RequestException as e:
            raise PDFDownloadError(
                f"Failed to download PDF: {e}",
                url=url,
            )
    
    def convert_to_images(
        self,
        pdf_bytes: bytes,
        *,
        zoom: Optional[int] = None,
    ) -> List[PDFPage]:
        """
        Convert PDF bytes to a list of page images.
        
        Uses multiprocessing for parallel conversion.
        
        Args:
            pdf_bytes: PDF file content
            zoom: Zoom factor for rendering (default from settings)
            
        Returns:
            List of PDFPage objects with rendered images
            
        Raises:
            PDFConversionError: If conversion fails
        """
        zoom = zoom or self.settings.pdf_zoom_factor
        
        # Save to temporary file for multiprocessing
        temp_path = self._save_to_temp_file(pdf_bytes)
        
        try:
            # Get page count
            doc = fitz.open(temp_path)
            page_count = doc.page_count
            doc.close()
            
            logger.info(f"Converting PDF with {page_count} pages (zoom={zoom}x)")
            
            # Prepare arguments for each page
            args_list = [(temp_path, i, zoom) for i in range(page_count)]
            pages: List[PDFPage] = []
            
            # Use multiprocessing for parallel conversion
            max_workers = min(
                self.settings.max_concurrent_pdf_conversion,
                page_count,
            )
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                future_to_page = {
                    executor.submit(_convert_single_page, args): args[1]
                    for args in args_list
                }
                
                for future in as_completed(future_to_page):
                    page_index = future_to_page[future]
                    try:
                        page_num, image_bytes = future.result()
                        pages.append(PDFPage(
                            page_number=page_num,
                            image_bytes=image_bytes,
                        ))
                    except Exception as e:
                        logger.error(f"Failed to convert page {page_index + 1}: {e}")
                        raise PDFConversionError(
                            f"Failed to convert page {page_index + 1}",
                            page_number=page_index + 1,
                            context={"error": str(e)},
                        )
            
            # Sort by page number to maintain order
            pages.sort(key=lambda p: p.page_number)
            
            total_size = sum(p.size_bytes for p in pages)
            logger.info(f"Converted {len(pages)} pages, total size: {total_size:,} bytes")
            
            return pages
            
        finally:
            self._cleanup_temp_file(temp_path)
    
    def encode_pages_to_base64(self, pages: List[PDFPage]) -> List[PageImage]:
        """
        Encode page images to base64 data URLs.
        
        Args:
            pages: List of PDF pages with image bytes
            
        Returns:
            List of PageImage objects with base64-encoded data URLs
        """
        encoded: List[PageImage] = []
        
        for page in pages:
            base64_str = base64.b64encode(page.image_bytes).decode("utf-8")
            data_url = f"data:image/png;base64,{base64_str}"
            
            encoded.append(PageImage(
                page_number=page.page_number,
                data_url=data_url,
            ))
        
        logger.debug(f"Encoded {len(encoded)} pages to base64")
        return encoded
    
    def _save_to_temp_file(self, pdf_bytes: bytes) -> str:
        """Save PDF bytes to a temporary file."""
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
            prefix="api_llm_ocr_",
        ) as f:
            f.write(pdf_bytes)
            temp_path = f.name
        
        self._temp_files.append(temp_path)
        logger.debug(f"Saved PDF to temp file: {temp_path}")
        return temp_path
    
    def _cleanup_temp_file(self, path: str) -> None:
        """Clean up a temporary file."""
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Cleaned up temp file: {path}")
            if path in self._temp_files:
                self._temp_files.remove(path)
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {path}: {e}")
    
    def cleanup_all(self) -> None:
        """Clean up all temporary files."""
        for path in list(self._temp_files):
            self._cleanup_temp_file(path)
