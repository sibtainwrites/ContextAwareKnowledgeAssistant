"""
Main FastAPI application for the RAG Knowledge Assistant.

This module sets up the FastAPI application with CORS middleware,
includes API routers, and defines health and root endpoints.
"""

import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from middleware.error_handler import (
    RequestLoggingMiddleware,
    global_exception_handler,
    validation_exception_handler,
    value_error_handler,
    file_not_found_handler
)
from routes.upload import router as upload_router
from routes.chat import router as chat_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG Knowledge Assistant API",
    description="A FastAPI backend for Retrieval-Augmented Generation knowledge assistant",
    version="1.0.0"
)

# Get settings
settings = get_settings()

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(FileNotFoundError, file_not_found_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router, prefix="/api/upload", tags=["upload"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Returns the current status of the service.

    Returns:
        dict: Status information including version and service name.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "RAG Knowledge Assistant"
    }


@app.get("/")
def root():
    """
    Root endpoint.

    Provides basic information about the API and links to documentation.

    Returns:
        dict: Welcome message and documentation link.
    """
    return {
        "message": "RAG Knowledge Assistant API",
        "docs": "/docs"
    }


@app.on_event("startup")
def startup_event():
    """
    Application startup event handler.

    Validates that all required environment variables are loaded
    and logs successful startup.
    """
    try:
        # Validate settings by loading them
        settings = get_settings()
        logger.info("RAG Knowledge Assistant started successfully")
    except Exception as e:
        error_msg = f"Failed to load required environment variables: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
