"""
Database Models Module

This module defines the database schema using SQLAlchemy ORM.
Each model class represents a table in the PostgreSQL database.
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from sqlalchemy.types import TIMESTAMP
from datetime import datetime, timezone
from app.database import Base


class Paste(Base):
    """
    Paste Model - Represents a text paste in the database
    
    Table: pastes
    
    Columns:
        id (str): Unique identifier for the paste (primary key)
        content (str): The actual text content of the paste
        ttl_seconds (int, optional): Time-to-live in seconds (null = no expiry)
        max_views (int, optional): Maximum number of views allowed (null = unlimited)
        current_views (int): Current number of times this paste has been viewed
        created_at (datetime): When the paste was created
        expires_at (datetime, optional): When the paste will expire (null = no expiry)
        is_active (bool): Whether the paste is still available
    
    Example:
        # Create a new paste
        paste = Paste(
            id="abc123",
            content="Hello, World!",
            ttl_seconds=3600,
            max_views=10
        )
    """
    
    # Table name in PostgreSQL
    __tablename__ = "pastes"
    
    # Primary key - unique identifier for each paste
    # We'll generate this using secrets.token_urlsafe()
    id = Column(String(50), primary_key=True, index=True)
    
    # The actual paste content - can be very large text
    content = Column(Text, nullable=False)
    
    # Optional TTL (time-to-live) in seconds
    # If null, the paste never expires based on time
    ttl_seconds = Column(Integer, nullable=True)
    
    # Optional maximum number of views
    # If null, the paste has unlimited views
    max_views = Column(Integer, nullable=True)
    
    # Current view count - starts at 0
    # This is incremented each time the paste is fetched via API
    current_views = Column(Integer, default=0, nullable=False)
    
    # Timestamp when the paste was created (timezone-aware)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Calculated expiry timestamp (if TTL is set) - timezone-aware
    # This is set when the paste is created: created_at + ttl_seconds
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Flag to mark if paste is still active
    # Set to False when paste is expired or view limit is reached
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        """
        String representation of the Paste object.
        Useful for debugging and logging.
        """
        return f"<Paste(id={self.id}, views={self.current_views}/{self.max_views})>"
    
    def is_expired(self, current_time=None):
        """
        Check if the paste has expired based on TTL.
        
        Args:
            current_time (datetime, optional): Current time for testing.
                                              If None, uses actual current time.
        
        Returns:
            bool: True if expired, False otherwise
        """
        if not self.expires_at:
            return False  # No expiry time set
        
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        
        return current_time >= self.expires_at
    
    def is_view_limit_reached(self):
        """
        Check if the paste has reached its view limit.
        
        Returns:
            bool: True if limit reached, False otherwise
        """
        if self.max_views is None:
            return False  # No view limit set
        
        return self.current_views >= self.max_views
    
    def is_available(self, current_time=None):
        """
        Check if the paste is available (not expired and under view limit).
        
        Args:
            current_time (datetime, optional): Current time for testing
        
        Returns:
            bool: True if available, False otherwise
        """
        if not self.is_active:
            return False
        
        if self.is_expired(current_time):
            return False
        
        if self.is_view_limit_reached():
            return False
        
        return True
    
    def get_remaining_views(self):
        """
        Calculate remaining views before limit is reached.
        
        Returns:
            int or None: Number of remaining views, or None if unlimited
        """
        if self.max_views is None:
            return None
        
        remaining = self.max_views - self.current_views
        return max(0, remaining)  # Never return negative
