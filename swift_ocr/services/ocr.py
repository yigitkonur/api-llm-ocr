"""
OCR service using OpenAI Vision API.

Handles text extraction from images using GPT-4 Vision.
"""

import asyncio
from typing import List, Optional

from openai import AsyncAzureOpenAI, OpenAIError

from swift_ocr.config import Settings
from swift_ocr.core.exceptions import OCRProcessingError, RateLimitError
from swift_ocr.core.logging import get_logger
from swift_ocr.core.retry import retry_with_backoff
from swift_ocr.schemas import PageImage

logger = get_logger(__name__)


# System prompt for OCR
SYSTEM_PROMPT = """You are an OCR assistant. Extract all text from the provided images (Describe images as if you're explaining them to a blind person eg: `[Image: In this picture, 8 people are posed hugging each other]`), which are attached to the document. Use markdown formatting for:

- Headings (# for main, ## for sub)
- Lists (- for unordered, 1. for ordered)
- Emphasis (* for italics, ** for bold)
- Links ([text](URL))
- Tables (use markdown table format)

For non-text elements, describe them: [Image: Brief description]

Maintain logical flow and use horizontal rules (---) to separate sections if needed. Adjust formatting to preserve readability.

Note any issues or ambiguities at the end of your output.

Be thorough and accurate in transcribing all text content."""

USER_PROMPT = """Never skip any context! Convert document as is be creative to use markdown effectively to reproduce the same document by using markdown. Translate image text to markdown sequentially. Preserve order and completeness. Separate images with `---`. No skips or comments. Start with first image immediately."""


class OCRService:
    """
    Service for OCR processing using OpenAI Vision API.
    
    Handles batching, retry logic, and text extraction.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize OCR service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self._client: Optional[AsyncAzureOpenAI] = None
    
    @property
    def client(self) -> AsyncAzureOpenAI:
        """Get or create the OpenAI client (lazy initialization)."""
        if self._client is None:
            self._client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_version=self.settings.openai_api_version,
                api_key=self.settings.openai_api_key,
            )
        return self._client
    
    async def process_pages(
        self,
        pages: List[PageImage],
        *,
        batch_size: Optional[int] = None,
    ) -> str:
        """
        Process multiple pages and extract text.
        
        Args:
            pages: List of page images to process
            batch_size: Number of pages per OCR request (default from settings)
            
        Returns:
            Extracted text in Markdown format
            
        Raises:
            OCRProcessingError: If text extraction fails
        """
        batch_size = batch_size or self.settings.batch_size
        batches = self._create_batches(pages, batch_size)
        
        logger.info(f"Processing {len(pages)} pages in {len(batches)} batches")
        
        # Process batches with concurrency limit
        semaphore = asyncio.Semaphore(self.settings.max_concurrent_ocr_requests)
        
        async def process_with_semaphore(batch: List[PageImage]) -> str:
            async with semaphore:
                return await self._process_batch(batch)
        
        tasks = [
            asyncio.create_task(process_with_semaphore(batch))
            for batch in batches
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error processing batches: {e}")
            raise OCRProcessingError(f"Batch processing failed: {e}")
        
        # Check for exceptions in results
        texts: List[str] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch {i + 1} failed: {result}")
                raise OCRProcessingError(
                    f"Batch {i + 1} failed",
                    batch_info=f"pages {batches[i][0].page_number}-{batches[i][-1].page_number}",
                    context={"error": str(result)},
                )
            texts.append(result)
        
        # Concatenate results
        final_text = "\n\n".join(texts)
        logger.info(f"OCR complete: {len(final_text):,} characters extracted")
        
        return final_text
    
    async def _process_batch(self, batch: List[PageImage]) -> str:
        """
        Process a single batch of pages with retry logic.
        
        Args:
            batch: List of page images in this batch
            
        Returns:
            Extracted text from the batch
        """
        page_range = f"{batch[0].page_number}-{batch[-1].page_number}"
        logger.debug(f"Processing batch: pages {page_range}")
        
        async def make_request() -> str:
            return await self._call_openai_api(batch)
        
        return await retry_with_backoff(
            make_request,
            max_retries=self.settings.max_retries,
            base_delay=self.settings.retry_base_delay,
            max_delay=self.settings.retry_max_delay,
            retryable_exceptions=(RateLimitError, asyncio.TimeoutError),
        )
    
    async def _call_openai_api(self, batch: List[PageImage]) -> str:
        """
        Make the actual API call to OpenAI.
        
        Args:
            batch: List of page images to process
            
        Returns:
            Extracted text
            
        Raises:
            RateLimitError: If rate limited
            OCRProcessingError: If API call fails
        """
        messages = self._build_messages(batch)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_deployment_id,
                messages=messages,
                temperature=self.settings.ocr_temperature,
                max_tokens=self.settings.ocr_max_tokens,
                top_p=self.settings.ocr_top_p,
                frequency_penalty=0,
                presence_penalty=0,
            )
            
            return self._extract_text_from_response(response)
            
        except OpenAIError as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                raise RateLimitError(
                    "OpenAI rate limit exceeded",
                    context={"error": str(e)},
                )
            
            logger.error(f"OpenAI API error: {e}")
            raise OCRProcessingError(
                f"OCR API call failed: {e}",
                status_code=502,
            )
        except asyncio.TimeoutError:
            raise  # Let retry logic handle this
        except Exception as e:
            logger.exception(f"Unexpected error during OCR: {e}")
            raise OCRProcessingError(f"Unexpected OCR error: {e}")
    
    def _build_messages(self, batch: List[PageImage]) -> List[dict]:
        """
        Build the message payload for the OpenAI API.
        
        Args:
            batch: List of page images
            
        Returns:
            List of message dictionaries
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ]
        
        if len(batch) == 1:
            # Single page: simple format
            page = batch[0]
            messages.append({
                "role": "user",
                "content": f"Page {page.page_number}:",
            })
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": page.data_url}}
                ],
            })
        else:
            # Multiple pages: include page numbers in content
            messages.append({
                "role": "user",
                "content": "Please perform OCR on the following images. "
                          "Ensure that the extracted text includes the corresponding page numbers.",
            })
            
            content = []
            for page in batch:
                content.append({"type": "text", "text": f"Page {page.page_number}:"})
                content.append({"type": "image_url", "image_url": {"url": page.data_url}})
            
            messages.append({"role": "user", "content": content})
        
        return messages
    
    def _extract_text_from_response(self, response) -> str:
        """
        Extract text content from the API response.
        
        Args:
            response: OpenAI API response
            
        Returns:
            Extracted text
            
        Raises:
            OCRProcessingError: If no text was extracted
        """
        if (
            not response.choices
            or not hasattr(response.choices[0].message, "content")
            or not response.choices[0].message.content
        ):
            raise OCRProcessingError("No text extracted from OCR response")
        
        text = response.choices[0].message.content.strip()
        logger.debug(f"Extracted {len(text):,} characters from response")
        return text
    
    def _create_batches(
        self,
        items: List[PageImage],
        batch_size: int,
    ) -> List[List[PageImage]]:
        """Split items into batches of specified size."""
        batches = [
            items[i:i + batch_size]
            for i in range(0, len(items), batch_size)
        ]
        return batches
    
    async def close(self) -> None:
        """Close the OpenAI client."""
        if self._client is not None:
            await self._client.close()
            self._client = None
