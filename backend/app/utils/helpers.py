"""
Helper utility functions for the Agno chatbot application.
"""

import uuid
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any


def generate_uuid() -> str:
    """
    Generate a UUID string.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def format_timestamp(dt: datetime, include_timezone: bool = True) -> str:
    """
    Format a datetime object to ISO format.
    
    Args:
        dt: Datetime object
        include_timezone: Whether to include timezone information
        
    Returns:
        Formatted timestamp string
    """
    if include_timezone and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (optional)
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    sanitized = " ".join(text.split())
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
    
    return sanitized


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract basic entities from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary of extracted entities
    """
    entities = {
        "urls": [],
        "emails": [],
        "mentions": [],
        "hashtags": []
    }
    
    # Extract URLs
    url_pattern = r'https?://[^\s]+'
    entities["urls"] = re.findall(url_pattern, text)
    
    # Extract emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = re.findall(email_pattern, text)
    
    # Extract mentions (@username)
    mention_pattern = r'@(\w+)'
    entities["mentions"] = re.findall(mention_pattern, text)
    
    # Extract hashtags (#tag)
    hashtag_pattern = r'#(\w+)'
    entities["hashtags"] = re.findall(hashtag_pattern, text)
    
    return entities


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using Jaccard similarity.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at word boundary
        if end < len(text):
            # Look for the last space before the end
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space
        
        chunks.append(text[start:end].strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_file_size(bytes_size: int) -> str:
    """
    Format file size in bytes to human-readable string.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}TB"


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary.
    
    Args:
        dictionary: Dictionary to search
        key: Key to look for
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    return dictionary.get(key, default)


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries, with dict2 taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def is_valid_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not session_id:
        return False
    
    # Check if it's a valid UUID
    try:
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False


def generate_session_id() -> str:
    """
    Generate a new session ID.
    
    Returns:
        Session ID string
    """
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """
    Get current UTC timestamp.
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc) 