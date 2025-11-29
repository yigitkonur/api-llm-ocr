"""
Entry point for running Swift OCR as a module.

Usage:
    python -m swift_ocr
    python -m swift_ocr --host 0.0.0.0 --port 8080
"""

import argparse
import sys


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="swift-ocr",
        description="Swift OCR - LLM-powered PDF to Markdown converter",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )
    
    args = parser.parse_args()
    
    if args.version:
        from swift_ocr import __version__
        print(f"Swift OCR v{__version__}")
        return 0
    
    try:
        import uvicorn
        
        uvicorn.run(
            "swift_ocr.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level="info",
        )
        return 0
    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
