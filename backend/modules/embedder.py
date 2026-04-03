"""
Embedding module for the RAG Knowledge Assistant.

This module provides text embedding functionality using Google Generative AI
embeddings model. Implements singleton pattern for model reuse and includes
retry logic for robust API interactions.
"""

import logging
from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_settings

logger = logging.getLogger(__name__)

# Global embeddings model instance (singleton)
_embeddings_instance: GoogleGenerativeAIEmbeddings | None = None


def get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    """
    Get or create the singleton Google Generative AI embeddings model.

    Uses lazy initialization to create the embeddings model only when first needed.
    Configures the model with the specified embedding model and API key from settings.

    Returns:
        GoogleGenerativeAIEmbeddings: Configured embeddings model instance.

    Raises:
        RuntimeError: If model initialization fails due to invalid API key or configuration.
    """
    global _embeddings_instance

    if _embeddings_instance is not None:
        return _embeddings_instance

    try:
        settings = get_settings()
        _embeddings_instance = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.gemini_api_key
        )
        return _embeddings_instance
    except Exception as e:
        raise RuntimeError(f"Failed to initialize embeddings model: {str(e)}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings.

    Uses the Google Generative AI embeddings model with automatic retry logic
    for handling transient API failures.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors, each as a list of floats (3072 dimensions).

    Raises:
        Exception: Re-raises any embedding API errors after retries are exhausted.
    """
    logger.info(f"Embedding {len(texts)} texts...")

    model = get_embeddings_model()
    embeddings = model.embed_documents(texts)

    logger.info(f"Embeddings complete, dimension=3072")
    return embeddings


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def embed_query(text: str) -> List[float]:
    """
    Generate embedding for a single query text string.

    Uses the Google Generative AI embeddings model with automatic retry logic
    for handling transient API failures. Optimized for query embedding.

    Args:
        text: Query text string to embed.

    Returns:
        Embedding vector as a list of floats (3072 dimensions).

    Raises:
        Exception: Re-raises any embedding API errors after retries are exhausted.
    """
    model = get_embeddings_model()
    embedding = model.embed_query(text)

    return embedding