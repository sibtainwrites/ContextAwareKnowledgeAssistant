"""
Text chunking module for the RAG Knowledge Assistant.

This module provides functionality to split document text into manageable chunks
for embedding and retrieval in the RAG system. Uses LangChain's
RecursiveCharacterTextSplitter for intelligent text segmentation.
"""

import logging
from collections import defaultdict
from typing import List, Dict

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def chunk_documents(
    pages: List[Dict],
    chunk_size: int = 800,
    chunk_overlap: int = 200
) -> List[Dict]:
    """
    Split document pages into overlapping text chunks.

    Uses RecursiveCharacterTextSplitter to create chunks with intelligent
    splitting based on natural text boundaries. Default chunk_size=800 and
    chunk_overlap=200 provide good balance between context preservation and
    retrieval granularity - chunks are large enough to maintain semantic
    meaning while overlap ensures continuity across chunk boundaries.

    Args:
        pages: List of page/segment dictionaries from processors.
               Each dict must have 'text' and 'metadata' keys.
        chunk_size: Maximum characters per chunk (default: 800).
        chunk_overlap: Characters to overlap between chunks (default: 200).

    Returns:
        List of chunk dictionaries with text and enhanced metadata.
        Each chunk includes chunk_index and char_count in metadata.
    """
    # Create text splitter with hierarchical separators for natural splitting
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],  # Prefer paragraph, then sentence, then word breaks
        length_function=len
    )

    chunks = []
    source_chunk_counts = defaultdict(int)

    for page in pages:
        text = page["text"]
        metadata = page["metadata"].copy()  # Avoid mutating original

        # Split the page text into chunks
        page_chunks = splitter.split_text(text)

        chunk_index = 0
        for chunk_text in page_chunks:
            char_count = len(chunk_text)

            # Skip chunks that are too short (likely noise or fragments)
            if char_count < 50:
                continue

            # Create chunk metadata with additional fields
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_index
            chunk_metadata["char_count"] = char_count

            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })

            chunk_index += 1
            source_chunk_counts[metadata["source"]] += 1

    # Log chunk counts per source
    for source, count in source_chunk_counts.items():
        logger.info(f"Created {count} chunks from source: {source}")

    return chunks


def get_chunk_stats(chunks: List[Dict]) -> Dict:
    """
    Calculate statistics about a collection of text chunks.

    Provides insights into chunk distribution and characteristics
    for monitoring and optimization of the chunking process.

    Args:
        chunks: List of chunk dictionaries from chunk_documents().

    Returns:
        Dictionary containing chunk statistics:
        - total_chunks: Total number of chunks
        - avg_chunk_size: Average characters per chunk
        - min_chunk_size: Smallest chunk size
        - max_chunk_size: Largest chunk size
        - sources: List of unique source identifiers
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
            "sources": []
        }

    total_chunks = len(chunks)
    sizes = [chunk["metadata"]["char_count"] for chunk in chunks]
    sources = list(set(chunk["metadata"]["source"] for chunk in chunks))

    return {
        "total_chunks": total_chunks,
        "avg_chunk_size": round(sum(sizes) / len(sizes), 1),
        "min_chunk_size": min(sizes),
        "max_chunk_size": max(sizes),
        "sources": sources
    }
