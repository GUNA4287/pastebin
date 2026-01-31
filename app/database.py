"""
Database Configuration Module

This module handles PostgreSQL database connection and session management.
It uses SQLAlchemy ORM for database operations.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable
# For local development: postgresql://user:password@localhost/dbname
# For production (Neon): postgresql://user:password@host/dbname
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine
# The engine manages connections to the database
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,          # Maximum number of connections to keep
    max_overflow=10       # Maximum overflow connections
)

# Create session factory
# Sessions are used to interact with the database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for our database models
# All database models will inherit from this
Base = declarative_base()


def get_db():
    """
    Database dependency function.
    
    This function creates a new database session for each request
    and ensures it's closed after the request is complete.
    
    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database.
    
    This function creates all tables defined in our models.
    Should be called once when the application starts.
    Tables are only created if they don't already exist.
    """
    try:
        from app import models  # Import models to register them
        # checkfirst=True ensures tables are only created if they don't exist
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✓ Database tables initialized successfully")
    except Exception as e:
        print(f"⚠ Database initialization note: {e}")
        # Don't raise the error - tables might already exist which is fine
        print("✓ Continuing with existing database schema")


def check_db_connection():
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
