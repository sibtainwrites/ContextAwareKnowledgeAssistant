"""
Vector store module for the RAG Knowledge Assistant using Qdrant Cloud.

This module provides vector database operations for storing and retrieving
text embeddings using Qdrant Cloud. Implements singleton client pattern
and comprehensive CRUD operations for document chunks.
"""

import logging
import uuid
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from config import get_settings
from modules.embedder import embed_texts, embed_query

logger = logging.getLogger(__name__)

# Global client instance (singleton)
_client: QdrantClient | None = None
COLLECTION_NAME: str
VECTOR_SIZE = 3072


def get_client() -> QdrantClient:
    """
    Get or create the singleton Qdrant client.

    Uses lazy initialization to create the Qdrant client only when first needed.
    Automatically ensures the collection exists on first initialization.

    Returns:
        QdrantClient: Configured Qdrant client instance.

    Raises:
        RuntimeError: If client initialization fails.
    """
    global _client, COLLECTION_NAME

    if _client is not None:
        return _client

    try:
        settings = get_settings()
        COLLECTION_NAME = settings.collection_name

        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30.0
        )

        # Ensure collection exists
        _ensure_collection_exists()

        return _client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Qdrant client: {str(e)}")


def _ensure_collection_exists() -> None:
    """
    Ensure the Qdrant collection exists, creating it if necessary.

    Checks if the configured collection exists and creates it with
    appropriate vector parameters if it doesn't exist.
    """
    client = get_client()

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Collection created: {COLLECTION_NAME}")
    else:
        logger.info(f"Collection already exists: {COLLECTION_NAME}")


def store_chunks(chunks: List[Dict]) -> int:
    """
    Store text chunks with their embeddings in Qdrant.

    Embeds the chunk texts and stores them as points in the vector database
    with associated metadata.

    Args:
        chunks: List of chunk dictionaries with 'text' and 'metadata' keys.

    Returns:
        Number of chunks successfully stored.

    Raises:
        RuntimeError: If embedding or storage fails.
    """
    if not chunks:
        return 0

    try:
        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings
        vectors = embed_texts(texts)

        # Create points for Qdrant
        points = []
        for chunk, vector in zip(chunks, vectors):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk["text"],
                    "source": chunk["metadata"]["source"],
                    "type": chunk["metadata"]["type"],
                    "page": chunk["metadata"].get("page"),
                    "timestamp": chunk["metadata"].get("timestamp"),
                    "chunk_index": chunk["metadata"].get("chunk_index", 0)
                }
            )
            points.append(point)

        # Store in Qdrant
        client = get_client()
        client.upsert(collection_name=COLLECTION_NAME, points=points)

        logger.info(f"Stored {len(points)} chunks in Qdrant")
        return len(points)

    except Exception as e:
        raise RuntimeError(f"Failed to store chunks: {str(e)}")


def search_similar(query: str, top_k: int = 6) -> List[Dict]:
    """
    Search for similar chunks using vector similarity.

    Embeds the query and searches for the most similar chunks in the database.

    Args:
        query: Search query string.
        top_k: Number of top results to return (default: 6).

    Returns:
        List of similar chunks with scores and metadata, sorted by score descending.

    Raises:
        RuntimeError: If search fails.
    """
    try:
        # Embed the query
        query_vector = embed_query(query)

        # Search Qdrant
        client = get_client()
        search_response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            score_threshold=0.4,
            with_payload=True
        )

        # Convert to standardized format
        results = []
        for hit in search_response.points:
            result = {
                "text": hit.payload["text"],
                "score": hit.score,
                "metadata": {
                    "source": hit.payload["source"],
                    "type": hit.payload["type"],
                    "page": hit.payload.get("page"),
                    "timestamp": hit.payload.get("timestamp")
                }
            }
            results.append(result)

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"Found {len(results)} similar chunks for query")
        return results

    except Exception as e:
        raise RuntimeError(f"Failed to search similar chunks: {str(e)}")


def list_sources() -> List[str]:
    """
    Get a list of all unique source identifiers in the collection.

    Returns:
        Sorted list of unique source names.

    Raises:
        RuntimeError: If retrieval fails.
    """
    try:
        client = get_client()
        sources = set()

        # Scroll through all points to collect sources
        # Note: For large collections, this might need pagination
        scroll_result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10000,  # Adjust based on collection size
            with_payload=True
        )

        for point in scroll_result[0]:  # scroll_result is (points, next_offset)
            if "source" in point.payload:
                sources.add(point.payload["source"])

        return sorted(list(sources))

    except Exception as e:
        raise RuntimeError(f"Failed to list sources: {str(e)}")


def delete_source(source_name: str) -> bool:
    """
    Delete all chunks associated with a specific source.

    Args:
        source_name: Name of the source to delete.

    Returns:
        True if deletion was successful, False otherwise.
    """
    try:
        client = get_client()

        # Create filter for the source
        source_filter = Filter(
            must=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=source_name)
                )
            ]
        )

        # Delete points matching the filter
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=source_filter
        )

        logger.info(f"Deleted all chunks for source: {source_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to delete source {source_name}: {str(e)}")
        return False


def get_collection_stats() -> Dict:
    """
    Get statistics about the Qdrant collection.

    Returns:
        Dictionary containing collection statistics.

    Raises:
        RuntimeError: If retrieval fails.
    """
    try:
        client = get_client()
        collection_info = client.get_collection(COLLECTION_NAME)

        return {
            "total_vectors": collection_info.vectors_count,
            "collection_name": COLLECTION_NAME,
            "status": "active" if collection_info.status == "green" else "inactive"
        }

    except Exception as e:
        raise RuntimeError(f"Failed to get collection stats: {str(e)}")