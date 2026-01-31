"""
Main Application Module

This is the core FastAPI application that handles all HTTP requests.
It includes all API routes and HTML page handlers.
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app import models, schemas
from app.database import get_db, init_db, check_db_connection
from app.utils import (
    generate_paste_id,
    get_current_time,
    calculate_expiry_time,
    format_datetime_iso,
    build_paste_url
)

# Initialize FastAPI application
app = FastAPI(
    title="Pastebin-Lite API",
    description="A simple pastebin service for storing and sharing text",
    version="1.0.0"
)

# Set up Jinja2 templates for HTML pages
# Use absolute path to ensure it works in all environments
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Mount static files (CSS, JS, images)
# app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize database when application starts.
    
    This creates all database tables if they don't exist.
    """
    print("=" * 60)
    print("Starting Pastebin-Lite Application")
    print("=" * 60)
    init_db()
    print("✓ Application started successfully")
    print("=" * 60)


# ============================================================================
# API ROUTES
# ============================================================================

@app.get(
    "/api/healthz",
    response_model=schemas.HealthResponse,
    summary="Health Check",
    description="Check if the application and database are healthy"
)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    This endpoint verifies that:
    1. The application is running
    2. The database connection is working
    
    Returns:
        JSON: {"ok": true} if healthy, {"ok": false} if unhealthy
    
    Example:
        GET /api/healthz
        
        Response 200:
        {
            "ok": true
        }
    """
    try:
        # Try to execute a simple database query
        db.execute("SELECT 1")
        return JSONResponse(content={"ok": True}, status_code=200)
    except Exception as e:
        print(f"Health check failed: {e}")
        return JSONResponse(content={"ok": False}, status_code=200)


@app.post(
    "/api/pastes",
    response_model=schemas.PasteResponse,
    status_code=200,
    summary="Create Paste",
    description="Create a new paste with optional TTL and view limit"
)
async def create_paste(
    paste_data: schemas.PasteCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create a new paste.
    
    This endpoint:
    1. Validates the input data
    2. Generates a unique paste ID
    3. Calculates expiry time if TTL is provided
    4. Stores the paste in the database
    5. Returns the paste ID and shareable URL
    
    Args:
        paste_data (PasteCreate): Paste content and optional constraints
        request (Request): HTTP request object
        db (Session): Database session
    
    Returns:
        JSON: Paste ID and URL
    
    Raises:
        HTTPException 400: If validation fails
    
    Example:
        POST /api/pastes
        {
            "content": "Hello, World!",
            "ttl_seconds": 3600,
            "max_views": 10
        }
        
        Response 200:
        {
            "id": "abc123",
            "url": "https://pastebin-lite.onrender.com/p/abc123"
        }
    """
    try:
        # Generate unique paste ID
        paste_id = generate_paste_id()
        
        # Get current time for created_at
        created_at = get_current_time(request)
        
        # Calculate expiry time if TTL is provided
        expires_at = None
        if paste_data.ttl_seconds:
            expires_at = calculate_expiry_time(created_at, paste_data.ttl_seconds)
        
        # Create new paste object
        new_paste = models.Paste(
            id=paste_id,
            content=paste_data.content,
            ttl_seconds=paste_data.ttl_seconds,
            max_views=paste_data.max_views,
            current_views=0,
            created_at=created_at,
            expires_at=expires_at,
            is_active=True
        )
        
        # Save to database
        db.add(new_paste)
        db.commit()
        db.refresh(new_paste)
        
        # Build shareable URL
        paste_url = build_paste_url(request, paste_id)
        
        # Return response
        return JSONResponse(
            content={
                "id": paste_id,
                "url": paste_url
            },
            status_code=200
        )
    
    except ValueError as e:
        # Validation error from Pydantic
        return JSONResponse(
            content={"error": str(e)},
            status_code=400
        )
    except Exception as e:
        # Unexpected error
        print(f"Error creating paste: {e}")
        return JSONResponse(
            content={"error": "Internal server error"},
            status_code=500
        )


@app.get(
    "/api/pastes/{paste_id}",
    response_model=schemas.PasteFetch,
    summary="Fetch Paste",
    description="Fetch a paste by ID (counts as a view)"
)
async def fetch_paste(
    paste_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Fetch a paste by ID.
    
    This endpoint:
    1. Retrieves the paste from database
    2. Checks if it's expired (using TEST_MODE if enabled)
    3. Checks if view limit is reached
    4. Increments the view count
    5. Returns the paste data
    
    Important: Each API fetch counts as a view!
    
    Args:
        paste_id (str): The paste ID
        request (Request): HTTP request object
        db (Session): Database session
    
    Returns:
        JSON: Paste content, remaining views, expiry time
    
    Raises:
        HTTPException 404: If paste not found, expired, or view limit reached
    
    Example:
        GET /api/pastes/abc123
        
        Response 200:
        {
            "content": "Hello, World!",
            "remaining_views": 9,
            "expires_at": "2026-01-31T12:00:00.000Z"
        }
        
        Response 404:
        {
            "error": "Paste not found"
        }
    """
    try:
        # Get current time (respects TEST_MODE)
        current_time = get_current_time(request)
        
        # Fetch paste from database
        paste = db.query(models.Paste).filter(models.Paste.id == paste_id).first()
        
        # Check if paste exists
        if not paste:
            return JSONResponse(
                content={"error": "Paste not found"},
                status_code=404
            )
        
        # Check if paste is available
        if not paste.is_available(current_time):
            # Mark as inactive and save
            paste.is_active = False
            db.commit()
            
            # Determine error message
            if paste.is_expired(current_time):
                error_msg = "Paste has expired"
            elif paste.is_view_limit_reached():
                error_msg = "View limit exceeded"
            else:
                error_msg = "Paste not available"
            
            return JSONResponse(
                content={"error": error_msg},
                status_code=404
            )
        
        # Increment view count
        paste.current_views += 1
        
        # Check if this view reached the limit
        if paste.is_view_limit_reached():
            paste.is_active = False
        
        db.commit()
        db.refresh(paste)
        
        # Build response
        response_data = {
            "content": paste.content,
            "remaining_views": paste.get_remaining_views(),
            "expires_at": format_datetime_iso(paste.expires_at) if paste.expires_at else None
        }
        
        return JSONResponse(content=response_data, status_code=200)
    
    except Exception as e:
        print(f"Error fetching paste: {e}")
        return JSONResponse(
            content={"error": "Internal server error"},
            status_code=500
        )


# ============================================================================
# HTML PAGE ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse, summary="Home Page")
async def home_page(request: Request):
    """
    Render the home page with paste creation form.
    
    This is the main landing page where users can create new pastes.
    
    Returns:
        HTML: Home page with form
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/p/{paste_id}", response_class=HTMLResponse, summary="View Paste")
async def view_paste(
    paste_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    View a paste as HTML.
    
    This endpoint displays the paste content in a web page.
    Note: This does NOT count as a view (unlike the API endpoint).
    
    Args:
        paste_id (str): The paste ID
        request (Request): HTTP request object
        db (Session): Database session
    
    Returns:
        HTML: Page displaying paste content
        HTML 404: If paste not found or unavailable
    """
    try:
        # Get current time (respects TEST_MODE)
        current_time = get_current_time(request)
        
        # Fetch paste from database
        paste = db.query(models.Paste).filter(models.Paste.id == paste_id).first()
        
        # Check if paste exists
        if not paste:
            return HTMLResponse(
                content="<html><body><h1>404 - Paste Not Found</h1></body></html>",
                status_code=404
            )
        
        # Check if paste is available
        if not paste.is_available(current_time):
            # Mark as inactive
            paste.is_active = False
            db.commit()
            
            # Determine error message
            if paste.is_expired(current_time):
                error_msg = "Paste Has Expired"
            elif paste.is_view_limit_reached():
                error_msg = "View Limit Exceeded"
            else:
                error_msg = "Paste Not Available"
            
            return HTMLResponse(
                content=f"<html><body><h1>404 - {error_msg}</h1></body></html>",
                status_code=404
            )
        
        # Render the paste view page
        # Jinja2 automatically escapes HTML to prevent XSS
        return templates.TemplateResponse(
            "view_paste.html",
            {
                "request": request,
                "paste_id": paste_id,
                "content": paste.content
            }
        )
    
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error viewing paste: {e}")
        print(traceback.format_exc())
        return HTMLResponse(
            content=f"<html><body><h1>500 - Internal Server Error</h1><p>Error: {str(e)}</p></body></html>",
            status_code=500
        )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """
    Handle Pydantic validation errors.
    
    Returns a 400 Bad Request with error details.
    """
    return JSONResponse(
        content={"error": "Invalid input"},
        status_code=400
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """
    Handle internal server errors.
    
    Returns a 500 Internal Server Error.
    """
    return JSONResponse(
        content={"error": "Internal server error"},
        status_code=500
    )
