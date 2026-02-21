"""
Logging configuration for api-llm-ocr.

Provides structured logging with configurable levels and formats.
"""

import logging
import sys
from functools import lru_cache
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for terminals."""
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color to levelname
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: int = logging.INFO,
    *,
    use_colors: bool = True,
    log_format: Optional[str] = None,
) -> None:
    """
    Configure application logging.
    
    Args:
        level: Logging level (default: INFO)
        use_colors: Enable colored output in terminals
        log_format: Custom log format string
    """
    format_str = log_format or "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Use colored formatter if enabled and stdout is a TTY
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        formatter = logging.Formatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


@lru_cache
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Uses lru_cache to avoid creating multiple loggers for the same name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
