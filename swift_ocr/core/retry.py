"""
Retry utilities with exponential backoff.

Provides decorators and functions for retrying failed operations.
"""

import asyncio
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

from swift_ocr.core.exceptions import ApiLlmOcrError, RateLimitError
from swift_ocr.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 10,
    base_delay: float = 1.0,
    max_delay: float = 120.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (RateLimitError, asyncio.TimeoutError),
    **kwargs: Any,
) -> Any:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: The async function to retry
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        retryable_exceptions: Tuple of exceptions that should trigger a retry
        **kwargs: Keyword arguments for the function
        
    Returns:
        The result of the function if successful
        
    Raises:
        The last exception if all retries fail
    """
    last_exception: Optional[Exception] = None
    
    for attempt in range(1, max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(
                    f"Max retries ({max_retries}) exceeded for {func.__name__}",
                    extra={"error": str(e)},
                )
                raise
            
            # Calculate delay with exponential backoff
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            
            # If it's a rate limit error with retry_after, use that instead
            if isinstance(e, RateLimitError) and e.context.get("retry_after"):
                delay = e.context["retry_after"]
            
            logger.warning(
                f"Attempt {attempt}/{max_retries} failed for {func.__name__}. "
                f"Retrying in {delay:.1f}s...",
                extra={"error": str(e), "delay": delay},
            )
            
            await asyncio.sleep(delay)
        except Exception as e:
            # Non-retryable exception, raise immediately
            logger.error(
                f"Non-retryable error in {func.__name__}: {e}",
                extra={"error_type": type(e).__name__},
            )
            raise
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Retry loop completed without result for {func.__name__}")


def with_retry(
    max_retries: int = 10,
    base_delay: float = 1.0,
    max_delay: float = 120.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (RateLimitError, asyncio.TimeoutError),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for adding retry logic to async functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        retryable_exceptions: Tuple of exceptions that should trigger a retry
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @with_retry(max_retries=5, base_delay=2.0)
        async def call_api():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_with_backoff(
                func,
                *args,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                retryable_exceptions=retryable_exceptions,
                **kwargs,
            )
        return wrapper
    return decorator
