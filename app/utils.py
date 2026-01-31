"""
Utility Functions Module

This module contains helper functions used throughout the application.
"""

import secrets
import os
from datetime import datetime, timezone, timedelta
from fastapi import Request


def generate_paste_id(length: int = 8) -> str:
    """
    Generate a cryptographically secure random paste ID.
    
    Uses secrets.token_urlsafe() which is safe for security-sensitive operations.
    The ID is URL-safe and contains only alphanumeric characters, hyphens, and underscores.
    
    Args:
        length (int): Approximate length of the ID (default: 8)
    
    Returns:
        str: A random URL-safe string
    
    Example:
        >>> generate_paste_id()
        'x4K_9mPq'
    """
    return secrets.token_urlsafe(length)


def get_current_time(request: Request) -> datetime:
    """
    Get the current time, with support for deterministic testing.
    
    When TEST_MODE environment variable is set to "1", this function
    checks for the x-test-now-ms header in the request. If present,
    it uses that timestamp instead of the actual current time.
    
    This allows automated tests to verify time-based expiry without
    waiting for actual time to pass.
    
    Args:
        request (Request): FastAPI request object
    
    Returns:
        datetime: Current time (or test time) in UTC timezone
    
    Example:
        # Normal usage (returns actual time)
        current = get_current_time(request)
        
        # In test mode with header x-test-now-ms: 1704067200000
        # Returns: datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    """
    # Check if we're in test mode
    test_mode = os.environ.get("TEST_MODE") == "1"
    
    if test_mode:
        # Look for test time in request headers
        test_time_ms = request.headers.get("x-test-now-ms")
        
        if test_time_ms:
            try:
                # Convert milliseconds to seconds and create datetime
                timestamp_seconds = int(test_time_ms) / 1000
                return datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
            except (ValueError, OSError):
                # If conversion fails, fall through to real time
                pass
    
    # Return actual current time in UTC
    return datetime.now(timezone.utc)


def calculate_expiry_time(created_at: datetime, ttl_seconds: int) -> datetime:
    """
    Calculate when a paste will expire based on TTL.
    
    Args:
        created_at (datetime): When the paste was created
        ttl_seconds (int): Time-to-live in seconds
    
    Returns:
        datetime: Expiry timestamp in UTC
    
    Example:
        >>> created = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> expiry = calculate_expiry_time(created, 3600)
        >>> expiry
        datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    """
    return created_at + timedelta(seconds=ttl_seconds)


def format_datetime_iso(dt: datetime) -> str:
    """
    Format a datetime object to ISO 8601 string with 'Z' suffix.
    
    The API specification requires timestamps in this format:
    "2026-01-01T00:00:00.000Z"
    
    Args:
        dt (datetime): Datetime object to format
    
    Returns:
        str: ISO formatted string with milliseconds and 'Z' suffix
    
    Example:
        >>> dt = datetime(2024, 1, 1, 12, 30, 45, 123456, tzinfo=timezone.utc)
        >>> format_datetime_iso(dt)
        '2024-01-01T12:30:45.123Z'
    """
    # Convert to ISO format and replace +00:00 with Z
    iso_string = dt.isoformat(timespec='milliseconds')
    return iso_string.replace('+00:00', 'Z')


def get_base_url(request: Request) -> str:
    """
    Get the base URL from the request.
    
    This constructs the base URL from the request's scheme and host.
    Handles both HTTP and HTTPS, and various port configurations.
    
    Args:
        request (Request): FastAPI request object
    
    Returns:
        str: Base URL (e.g., "https://pastebin-lite.onrender.com")
    
    Example:
        >>> get_base_url(request)
        'https://pastebin-lite.onrender.com'
    """
    # Get base URL from request and remove trailing slash
    base_url = str(request.base_url).rstrip('/')
    return base_url


def build_paste_url(request: Request, paste_id: str) -> str:
    """
    Build the full shareable URL for a paste.
    
    Args:
        request (Request): FastAPI request object
        paste_id (str): The paste ID
    
    Returns:
        str: Full URL to view the paste
    
    Example:
        >>> build_paste_url(request, "abc123")
        'https://pastebin-lite.onrender.com/p/abc123'
    """
    base_url = get_base_url(request)
    return f"{base_url}/p/{paste_id}"
