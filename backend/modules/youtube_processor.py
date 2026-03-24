"""
YouTube processing module for the RAG Knowledge Assistant.

This module provides functionality to validate YouTube URLs and extract
transcript content from YouTube videos for use in the retrieval-augmented
generation system.
"""

import logging
import re
from typing import List, Dict, Tuple

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)


def validate_youtube_url(url: str) -> Tuple[bool, str]:
    """
    Validate a YouTube URL and extract the video ID.

    Supports various YouTube URL formats including youtube.com, youtu.be,
    and mobile versions. Uses regex to extract the 11-character video ID.

    Args:
        url: The YouTube URL to validate.

    Returns:
        Tuple of (is_valid: bool, video_id_or_error: str).
        Returns (True, video_id) if valid, (False, "error message") if invalid.
    """
    def extract_video_id(url: str) -> str | None:
        """Extract video ID from YouTube URL using regex."""
        # Pattern matches video ID in various YouTube URL formats
        pattern = r'(?:v=|\/)([a-zA-Z0-9_-]{11})(?:[&\?]|$)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    video_id = extract_video_id(url)
    if video_id and len(video_id) == 11:
        return True, video_id
    else:
        return False, "Invalid YouTube URL format or video ID not found"


def seconds_to_timestamp(seconds: int) -> str:
    """
    Convert seconds to human-readable timestamp format.

    Converts raw seconds into HH:MM:SS or MM:SS format depending on duration.

    Args:
        seconds: Number of seconds to convert.

    Returns:
        Timestamp string in "H:MM:SS" or "MM:SS" format.

    Examples:
        0 -> "0:00"
        83 -> "1:23"
        3661 -> "1:01:01"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def extract_youtube_transcript(url: str) -> List[Dict]:
    """
    Extract transcript content from a YouTube video.

    Validates the URL, retrieves the transcript using youtube-transcript-api,
    cleans the text content, and returns structured data with metadata.

    Args:
        url: The YouTube URL to extract transcript from.

    Returns:
        List of dictionaries containing transcript segments with metadata.
        Each dict has 'text' and 'metadata' keys.

    Raises:
        ValueError: If URL is invalid, transcripts are disabled, or no transcript found.
    """
    is_valid, video_id_or_error = validate_youtube_url(url)
    if not is_valid:
        raise ValueError(video_id_or_error)

    video_id = video_id_or_error

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        results = []

        for entry in transcript:
            text = entry['text'].strip()

            # Remove bracketed tags like [Music], [Applause], etc.
            text = re.sub(r'\[.*?\]', '', text).strip()

            # Skip empty entries after cleaning
            if not text:
                continue

            timestamp = seconds_to_timestamp(int(entry['start']))

            results.append({
                "text": text,
                "metadata": {
                    "source": url,
                    "type": "youtube",
                    "timestamp": timestamp,
                    "seconds": int(entry['start'])
                }
            })

        logger.info(f"Extracted {len(results)} transcript segments from {url}")
        return results

    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video")
    except NoTranscriptFound:
        raise ValueError("No transcript found. Try a video with captions enabled.")
    except Exception as e:
        raise ValueError(f"Error extracting transcript: {str(e)}")