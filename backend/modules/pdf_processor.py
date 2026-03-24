"""
PDF processing module for the RAG Knowledge Assistant.

This module provides functionality to validate and extract text content
from PDF documents for use in the retrieval-augmented generation system.
"""

import io
import logging
import re
from typing import List, Dict, Tuple

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def validate_pdf(file_bytes: bytes) -> Tuple[bool, str]:
    """
    Validate a PDF file based on basic criteria.

    Performs basic validation checks on PDF file bytes without using
    full PDF parsing libraries. Checks file signature and size limits.

    Args:
        file_bytes: The raw bytes of the PDF file.

    Returns:
        Tuple of (is_valid: bool, error_message: str).
        Returns (True, "") if valid, (False, "error reason") if invalid.

    Raises:
        No exceptions are raised; all errors are caught and returned as strings.
    """
    try:
        # Check PDF magic bytes
        if not file_bytes.startswith(b'%PDF-'):
            return False, "File does not start with PDF magic bytes"

        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if len(file_bytes) > max_size:
            return False, f"File size ({len(file_bytes)} bytes) exceeds 10MB limit"

        return True, ""

    except Exception as e:
        return False, f"Error validating PDF: {str(e)}"


def extract_text_from_pdf(file_bytes: bytes, source_name: str) -> List[Dict]:
    """
    Extract text content from a PDF file.

    Uses pypdf to read the PDF and extract text from each page.
    Handles encrypted PDFs by skipping them. Cleans extracted text
    and returns structured data with metadata.

    Args:
        file_bytes: The raw bytes of the PDF file.
        source_name: Name/identifier of the source document.

    Returns:
        List of dictionaries containing extracted text and metadata.
        Each dict has 'text' and 'metadata' keys. Returns empty list
        on failure or if PDF is encrypted.

    Raises:
        No exceptions are raised; all errors are logged and empty list returned.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            logger.warning(f"PDF {source_name} is encrypted, skipping extraction")
            return []

        results = []
        total_pages = len(reader.pages)
        extracted_pages = 0

        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()

            # Skip pages with insufficient text (likely images or blank)
            if text is None or len(text.strip()) < 50:
                continue

            # Clean the extracted text
            # Replace multiple whitespace with single space
            text = re.sub(r'\s+', ' ', text)
            # Replace 3+ newlines with double newline
            text = re.sub(r'\n{3,}', '\n\n', text)
            # Strip leading/trailing whitespace
            text = text.strip()

            results.append({
                "text": text,
                "metadata": {
                    "source": source_name,
                    "type": "pdf",
                    "page": page_num,
                    "total_pages": total_pages
                }
            })
            extracted_pages += 1

        logger.info(f"Extracted text from {extracted_pages} pages of {source_name}")
        return results

    except Exception as e:
        logger.error(f"Error extracting text from PDF {source_name}: {str(e)}")
        return []