"""
Error handling and logging middleware for the RAG Knowledge Assistant.

This module provides comprehensive exception handling and request logging
middleware for the FastAPI application.
"""

import logging
import time
from typing import Callable

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests.

    Logs request method, path, response status code, and duration
    for monitoring and debugging purposes.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        Process the request and log its details.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/request handler in the chain.

        Returns:
            The response from the next handler.
        """
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log the request
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)")

        return response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.

    Catches all unhandled exceptions, logs the full traceback,
    and returns a standardized error response.

    Args:
        request: The HTTP request that caused the exception.
        exc: The exception that was raised.

    Returns:
        JSONResponse with error details and 500 status code.
    """
    # Log the full exception with traceback
    logger.exception(f"Unhandled exception in {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected error occurred",
            "detail": type(exc).__name__,
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors.

    Provides detailed field-level validation error messages.

    Args:
        request: The HTTP request with validation errors.
        exc: The validation exception with error details.

    Returns:
        JSONResponse with validation errors and 422 status code.
    """
    logger.warning(f"Validation error in {request.url.path}: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation error",
            "detail": exc.errors(),
            "path": str(request.url.path)
        }
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handler for ValueError exceptions.

    Returns the error message with 400 status code.

    Args:
        request: The HTTP request that caused the error.
        exc: The ValueError exception.

    Returns:
        JSONResponse with error message and 400 status code.
    """
    logger.warning(f"Value error in {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=400,
        content={
            "error": True,
            "message": str(exc),
            "detail": "ValueError",
            "path": str(request.url.path)
        }
    )


async def file_not_found_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
    """
    Handler for FileNotFoundError exceptions.

    Returns file not found error with 404 status code.

    Args:
        request: The HTTP request that caused the error.
        exc: The FileNotFoundError exception.

    Returns:
        JSONResponse with error message and 404 status code.
    """
    logger.warning(f"File not found in {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=404,
        content={
            "error": True,
            "message": "File not found",
            "detail": str(exc),
            "path": str(request.url.path)
        }
    )


# Registration instructions for main.py:
"""
To register these handlers and middleware in main.py, add the following code
after creating the FastAPI app instance:

from middleware.error_handler import (
    RequestLoggingMiddleware,
    global_exception_handler,
    validation_exception_handler,
    value_error_handler,
    file_not_found_handler
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(FileNotFoundError, file_not_found_handler)
"""
