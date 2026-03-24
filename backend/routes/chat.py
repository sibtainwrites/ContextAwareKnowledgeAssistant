"""
Chat routes for the RAG Knowledge Assistant.

This module provides API endpoints for question-answering using
the RAG pipeline with retrieved document context.
"""

import logging
import time
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.rag_pipeline import generate_answer

logger = logging.getLogger(__name__)

router = APIRouter()


class CitationModel(BaseModel):
    """Citation information for answer sources."""
    source: str
    type: str  # "pdf" or "youtube"
    page: Optional[int] = None
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat questions."""
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=6, ge=1, le=20)


class ChatResponse(BaseModel):
    """Response model for chat answers."""
    answer: str
    citations: List[CitationModel]
    chunks_used: int
    response_time_ms: int
    error: Optional[str] = None


@router.post("/ask", response_model=ChatResponse)
def ask_question(request: ChatRequest):
    """
    Answer a question using RAG retrieval and generation.

    Processes the question through the RAG pipeline: retrieves relevant
    document chunks, formats context, and generates an answer using
    the language model.

    Args:
        request: Chat request with question and retrieval parameters.

    Returns:
        ChatResponse with answer, citations, and performance metrics.

    Raises:
        HTTPException: For invalid input or processing errors.
    """
    # Validate question content
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start_time = time.time()

    try:
        # Generate answer using RAG pipeline
        result = generate_answer(request.question.strip(), request.top_k)

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Add timing to result
        result["response_time_ms"] = response_time_ms

        logger.info(f"Answered question in {response_time_ms}ms using {result['chunks_used']} chunks")

        return ChatResponse(**result)

    except Exception as e:
        # Return error response with 200 status (don't fail the request)
        error_msg = str(e)
        logger.error(f"Error processing question: {error_msg}")

        response_time_ms = int((time.time() - start_time) * 1000)

        return ChatResponse(
            answer="An error occurred while processing your question.",
            citations=[],
            chunks_used=0,
            response_time_ms=response_time_ms,
            error=error_msg
        )


@router.get("/health")
def chat_health():
    """
    Health check for the chat service.

    Returns the status of the chat service and its dependencies.

    Returns:
        Dictionary with service status and component information.
    """
    return {
        "status": "ok",
        "model": "gemini-1.5-flash",
        "retrieval": "qdrant"
    }

# TODO: Implement chat endpoints