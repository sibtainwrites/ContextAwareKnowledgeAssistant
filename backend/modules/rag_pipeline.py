"""
RAG Pipeline module for the Context-Aware Knowledge Assistant.

This module implements the core Retrieval-Augmented Generation logic,
combining vector search with LLM generation to provide accurate answers
based on uploaded document content.
"""

import logging
import time
from typing import List, Dict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import get_settings
from modules.vector_store import search_similar

logger = logging.getLogger(__name__)

# System prompt for the LLM
SYSTEM_PROMPT = """You are a precise and helpful AI assistant.
Your ONLY job is to answer questions based on the provided context from uploaded documents.

Rules you must follow:
1. Answer ONLY using information from the provided context
2. If the answer is not clearly present in the context, respond with exactly:
   "I don't have enough information in the uploaded documents to answer this question."
3. Never make up or infer information not present in the context
4. Be concise and clear
5. When citing information, naturally reference the source"""

# Global LLM instance (singleton)
_llm_instance: ChatGoogleGenerativeAI | None = None


def _get_llm() -> ChatGoogleGenerativeAI:
    """
    Get or create the singleton ChatGoogleGenerativeAI instance.

    Uses lazy initialization to create the LLM only when first needed.
    Configured for precise, factual responses with controlled output length.

    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance.
    """
    global _llm_instance

    if _llm_instance is not None:
        return _llm_instance

    settings = get_settings()
    _llm_instance = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=settings.gemini_api_key,
        temperature=0.1,
        max_output_tokens=1024
    )

    return _llm_instance


def _build_context_string(chunks: List[Dict]) -> str:
    """
    Build a formatted context string from retrieved chunks.

    Formats each chunk with source information and metadata for
    clear presentation to the LLM.

    Args:
        chunks: List of chunk dictionaries from vector search.

    Returns:
        Formatted context string with source attribution.
    """
    context_parts = []

    for chunk in chunks:
        metadata = chunk["metadata"]
        source = metadata["source"]
        chunk_type = metadata["type"]

        # Build location info
        location = ""
        if chunk_type == "pdf" and metadata.get("page"):
            location = f"Page: {metadata['page']}"
        elif chunk_type == "youtube" and metadata.get("timestamp"):
            location = f"Timestamp: {metadata['timestamp']}"

        # Format chunk header
        header = f"--- Source: {source} | Type: {chunk_type}"
        if location:
            header += f" | {location}"
        header += " ---"

        # Add formatted chunk
        context_parts.append(f"{header}\n{chunk['text']}")

    return "\n\n".join(context_parts)


def _extract_citations(chunks: List[Dict]) -> List[Dict]:
    """
    Extract unique citation information from retrieved chunks.

    Deduplicates citations based on source and location to avoid
    redundant references in the response.

    Args:
        chunks: List of chunk dictionaries from vector search.

    Returns:
        List of unique citation dictionaries.
    """
    citations = []
    seen = set()

    for chunk in chunks:
        metadata = chunk["metadata"]
        source = metadata["source"]
        chunk_type = metadata["type"]

        # Create unique key for deduplication
        if chunk_type == "pdf":
            key = (source, metadata.get("page"))
        elif chunk_type == "youtube":
            key = (source, metadata.get("timestamp"))
        else:
            key = (source, None)

        if key not in seen:
            citation = {
                "source": source,
                "type": chunk_type
            }

            if chunk_type == "pdf" and metadata.get("page"):
                citation["page"] = metadata["page"]
            elif chunk_type == "youtube" and metadata.get("timestamp"):
                citation["timestamp"] = metadata["timestamp"]

            citations.append(citation)
            seen.add(key)

    return citations


def generate_answer(question: str, top_k: int = 6) -> Dict:
    """
    Generate an answer to a question using RAG pipeline.

    Retrieves relevant document chunks, formats context, and uses LLM
    to generate a precise answer based only on the provided context.

    Args:
        question: The user's question string.
        top_k: Number of top similar chunks to retrieve (default: 6).

    Returns:
        Dictionary containing:
        - answer: Generated answer text
        - citations: List of source citations
        - chunks_used: Number of chunks used
        - error: Error message if any (None on success)
    """
    start_time = time.time()

    try:
        # Step 1: Retrieve similar chunks
        chunks = search_similar(question, top_k)

        # Step 2: Handle no documents case
        if not chunks:
            return {
                "answer": "No documents have been uploaded yet. Please upload PDFs or YouTube links first.",
                "citations": [],
                "chunks_used": 0,
                "error": None
            }

        # Step 3: Build context string
        context = _build_context_string(chunks)

        # Step 4: Build user message
        user_message = f"Context from uploaded documents:\n\n{context}\n\n---\n\nQuestion: {question}"

        # Step 5: Call LLM
        llm = _get_llm()
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message)
        ]
        response = llm.invoke(messages)

        # Step 6: Extract answer
        answer_text = response.content.strip()

        # Step 7: Extract citations
        citations = _extract_citations(chunks)

        # Step 8: Return result
        result = {
            "answer": answer_text,
            "citations": citations,
            "chunks_used": len(chunks),
            "error": None
        }

        # Log performance
        elapsed_ms = (time.time() - start_time) * 1000
        question_preview = question[:100] + "..." if len(question) > 100 else question
        logger.info(f"Generated answer for '{question_preview}' in {elapsed_ms:.1f}ms using {len(chunks)} chunks")

        return result

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating answer for question '{question[:50]}...': {error_msg}")

        return {
            "answer": "An error occurred while generating the answer.",
            "citations": [],
            "chunks_used": 0,
            "error": error_msg
        }