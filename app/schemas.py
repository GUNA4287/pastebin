"""
Pydantic Schemas Module

This module defines Pydantic models for request/response validation.
These schemas ensure data is valid before it reaches the database.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class PasteCreate(BaseModel):
    """
    Schema for creating a new paste.
    
    This validates the incoming POST request to /api/pastes
    
    Fields:
        content (str): The paste content (required, non-empty)
        ttl_seconds (int, optional): Time-to-live in seconds (must be >= 1)
        max_views (int, optional): Maximum views allowed (must be >= 1)
    
    Example:
        {
            "content": "Hello, World!",
            "ttl_seconds": 3600,
            "max_views": 10
        }
    """
    
    content: str = Field(..., description="The paste content")
    ttl_seconds: Optional[int] = Field(None, description="Time-to-live in seconds")
    max_views: Optional[int] = Field(None, description="Maximum number of views")
    
    @validator('content')
    def content_not_empty(cls, v):
        """
        Validate that content is not empty or just whitespace.
        
        Args:
            v (str): The content to validate
        
        Returns:
            str: The validated content
        
        Raises:
            ValueError: If content is empty or whitespace
        """
        if not v or not v.strip():
            raise ValueError('content must be a non-empty string')
        return v
    
    @validator('ttl_seconds')
    def ttl_positive(cls, v):
        """
        Validate that TTL is a positive integer.
        
        Args:
            v (int): The TTL value to validate
        
        Returns:
            int: The validated TTL
        
        Raises:
            ValueError: If TTL is less than 1
        """
        if v is not None and v < 1:
            raise ValueError('ttl_seconds must be >= 1')
        return v
    
    @validator('max_views')
    def max_views_positive(cls, v):
        """
        Validate that max_views is a positive integer.
        
        Args:
            v (int): The max_views value to validate
        
        Returns:
            int: The validated max_views
        
        Raises:
            ValueError: If max_views is less than 1
        """
        if v is not None and v < 1:
            raise ValueError('max_views must be >= 1')
        return v
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "content": "This is a sample paste",
                "ttl_seconds": 3600,
                "max_views": 5
            }
        }


class PasteResponse(BaseModel):
    """
    Schema for paste creation response.
    
    This is returned when a paste is successfully created.
    
    Fields:
        id (str): The unique paste identifier
        url (str): The full shareable URL
    
    Example:
        {
            "id": "abc123",
            "url": "https://your-app.onrender.com/p/abc123"
        }
    """
    
    id: str = Field(..., description="Unique paste identifier")
    url: str = Field(..., description="Shareable URL for the paste")
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "id": "abc123xyz",
                "url": "https://pastebin-lite.onrender.com/p/abc123xyz"
            }
        }


class PasteFetch(BaseModel):
    """
    Schema for paste fetch response.
    
    This is returned when fetching a paste via /api/pastes/:id
    
    Fields:
        content (str): The paste content
        remaining_views (int, optional): Remaining views (null if unlimited)
        expires_at (str, optional): ISO timestamp of expiry (null if no expiry)
    
    Example:
        {
            "content": "Hello, World!",
            "remaining_views": 4,
            "expires_at": "2026-01-31T12:00:00.000Z"
        }
    """
    
    content: str = Field(..., description="The paste content")
    remaining_views: Optional[int] = Field(None, description="Remaining views")
    expires_at: Optional[str] = Field(None, description="Expiry timestamp (ISO format)")
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "content": "This is the paste content",
                "remaining_views": 4,
                "expires_at": "2026-01-31T12:00:00.000Z"
            }
        }


class HealthResponse(BaseModel):
    """
    Schema for health check response.
    
    This is returned by /api/healthz endpoint.
    
    Fields:
        ok (bool): Whether the service is healthy
    
    Example:
        {"ok": true}
    """
    
    ok: bool = Field(..., description="Health status")
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "ok": True
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    
    This is returned for all error cases (4xx, 5xx).
    
    Fields:
        error (str): Error message
    
    Example:
        {"error": "Paste not found"}
    """
    
    error: str = Field(..., description="Error message")
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "error": "Paste not found"
            }
        }
