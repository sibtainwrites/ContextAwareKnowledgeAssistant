"""
Configuration settings for the RAG Knowledge Assistant backend.

This module defines the application settings using Pydantic BaseSettings,
automatically loading configuration from environment variables and .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are automatically loaded from the .env file in the backend directory.
    Required settings must be provided, while optional settings have sensible defaults.
    """

    gemini_api_key: str
    """API key for Google Gemini AI service."""

    qdrant_url: str
    """URL of the Qdrant vector database instance."""

    qdrant_api_key: str
    """API key for authenticating with Qdrant database."""

    collection_name: str = "knowledge_base"
    """Name of the Qdrant collection for storing document embeddings."""

    max_chunk_size: int = 800
    """Maximum size of text chunks for document processing."""

    chunk_overlap: int = 200
    """Number of characters to overlap between consecutive chunks."""

    top_k_results: int = 6
    """Number of top similar results to retrieve for queries."""

    embedding_dimension: int = 768
    """Dimension of the embedding vectors."""

    cors_origin: str = "http://localhost:5173"
    """Allowed CORS origin for frontend requests."""

    class Config:
        """Pydantic configuration for settings loading."""
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.

    Returns a cached instance of Settings to ensure settings are loaded once
    and reused throughout the application lifecycle.

    Returns:
        Settings: The application configuration settings.

    Raises:
        ValidationError: If required environment variables are missing or invalid.
    """
    return Settings()
