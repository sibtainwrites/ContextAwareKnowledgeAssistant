"""
Upload routes for the RAG Knowledge Assistant.

This module provides API endpoints for uploading and managing documents
and YouTube transcripts in the knowledge base.
"""

import logging
from typing import List
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from modules.pdf_processor import validate_pdf, extract_text_from_pdf
from modules.youtube_processor import validate_youtube_url, extract_youtube_transcript
from modules.chunker import chunk_documents
from modules.vector_store import store_chunks, list_sources, delete_source

logger = logging.getLogger(__name__)

router = APIRouter()


class YoutubeUploadRequest(BaseModel):
    """Request model for YouTube URL uploads."""
    url: str


class UploadResponse(BaseModel):
    """Response model for upload operations."""
    success: bool
    source: str
    chunks_stored: int
    message: str


class SourcesResponse(BaseModel):
    """Response model for listing sources."""
    sources: List[str]


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    success: bool
    deleted: str
    message: str


@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.

    Validates the PDF file, extracts text content, chunks it, and stores
    the embeddings in the vector database.

    Args:
        file: The uploaded PDF file.

    Returns:
        UploadResponse with processing results.

    Raises:
        HTTPException: For invalid files, processing errors, or empty content.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        # Read file contents
        contents = await file.read()

        # Validate PDF
        is_valid, error_msg = validate_pdf(contents)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Extract text
        pages = extract_text_from_pdf(contents, file.filename)
        if not pages:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text. File may be image-based."
            )

        # Chunk documents
        chunks = chunk_documents(pages)

        # Store chunks
        chunks_stored = store_chunks(chunks)

        return UploadResponse(
            success=True,
            source=file.filename,
            chunks_stored=chunks_stored,
            message=f"Successfully processed {file.filename}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during PDF processing: {str(e)}"
        )


@router.post("/youtube", response_model=UploadResponse)
async def upload_youtube(request: YoutubeUploadRequest):
    """
    Upload and process a YouTube video transcript.

    Validates the YouTube URL, extracts the transcript, chunks it, and stores
    the embeddings in the vector database.

    Args:
        request: YouTube URL upload request.

    Returns:
        UploadResponse with processing results.

    Raises:
        HTTPException: For invalid URLs, transcript errors, or processing failures.
    """
    try:
        # Validate URL
        is_valid, video_id_or_error = validate_youtube_url(request.url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=video_id_or_error)

        # Extract transcript
        try:
            segments = extract_youtube_transcript(request.url)
        except ValueError as e:
            if "disabled" in str(e).lower() or "transcript" in str(e).lower():
                raise HTTPException(status_code=422, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch transcript: {str(e)}"
            )

        # Chunk documents
        chunks = chunk_documents(segments)

        # Store chunks
        chunks_stored = store_chunks(chunks)

        return UploadResponse(
            success=True,
            source=request.url,
            chunks_stored=chunks_stored,
            message=f"Successfully processed YouTube video"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during YouTube processing: {str(e)}"
        )


@router.get("/sources", response_model=SourcesResponse)
def get_sources():
    """
    Get a list of all uploaded sources.

    Returns a list of unique source identifiers currently stored
    in the knowledge base.

    Returns:
        SourcesResponse with list of sources.

    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        sources = list_sources()
        return SourcesResponse(sources=sources)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve sources"
        )


@router.delete("/source/{source_name}", response_model=DeleteResponse)
def delete_source_endpoint(source_name: str):
    """
    Delete all chunks associated with a specific source.

    Removes all document chunks and embeddings for the given source
    from the knowledge base.

    Args:
        source_name: URL-encoded source identifier to delete.

    Returns:
        DeleteResponse with deletion results.

    Raises:
        HTTPException: If source not found or deletion fails.
    """
    try:
        # URL decode the source name
        decoded_source = unquote(source_name)

        # Attempt deletion
        success = delete_source(decoded_source)

        if success:
            return DeleteResponse(
                success=True,
                deleted=decoded_source,
                message=f"Deleted {decoded_source}"
            )
        else:
            raise HTTPException(status_code=404, detail="Source not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete source"
        )

# TODO: Implement upload endpoints
