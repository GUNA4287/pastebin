# Pastebin-Lite

A modern, fast, and secure pastebin web application for storing and sharing text snippets with optional expiry and view limits.

## 🚀 Live Demo

**Deployed Application:** [Your Render URL will be here after deployment]

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Persistence Layer](#persistence-layer)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Design Decisions](#design-decisions)

## ✨ Features

- ✅ Create text pastes with shareable URLs
- ✅ Optional time-to-live (TTL) expiry
- ✅ Optional view count limits
- ✅ Clean, responsive web interface
- ✅ RESTful API
- ✅ Deterministic time testing support
- ✅ PostgreSQL database for persistence
- ✅ Production-ready deployment

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Modern Python with type hints
- **FastAPI** - High-performance async web framework
- **SQLAlchemy** - Powerful ORM for database operations
- **PostgreSQL** - Reliable relational database
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn/Gunicorn** - ASGI server for production

### Frontend
- **Jinja2** - Server-side HTML templating
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern responsive styling

### Deployment
- **Render** - Cloud hosting platform
- **Neon** - Serverless PostgreSQL database

## 🗄️ Persistence Layer

This application uses **PostgreSQL** as its persistence layer.

### Why PostgreSQL?

1. **Reliability**: ACID-compliant relational database
2. **Scalability**: Handles millions of pastes efficiently
3. **Free Tier**: Neon provides generous free PostgreSQL hosting
4. **Rich Features**: Advanced querying, indexing, and constraints
5. **Industry Standard**: Well-documented and widely supported

### Database Schema

The application uses a single table: `pastes`

```sql
CREATE TABLE pastes (
    id VARCHAR(50) PRIMARY KEY,           -- Unique paste identifier
    content TEXT NOT NULL,                -- Paste content
    ttl_seconds INTEGER,                  -- Optional TTL in seconds
    max_views INTEGER,                    -- Optional view limit
    current_views INTEGER DEFAULT 0,      -- Current view count
    created_at TIMESTAMP NOT NULL,        -- Creation timestamp
    expires_at TIMESTAMP,                 -- Expiry timestamp
    is_active BOOLEAN DEFAULT TRUE        -- Active status
);
```

### For Local Development
- Use local PostgreSQL instance
- Or use free Neon database

### For Production
- **Neon PostgreSQL** (Recommended - Free tier available)
- Automatically managed backups
- Built-in connection pooling
- High availability

## 📁 Project Structure

```
pastebin-lite-aganitha/
│
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application & routes
│   ├── database.py              # Database configuration
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   └── utils.py                 # Utility functions
│
├── templates/                    # HTML templates
│   ├── index.html               # Home page (create paste)
│   └── view_paste.html          # View paste page
│
├── requirements.txt             # Python dependencies
├── Procfile                     # Render deployment config
├── runtime.txt                  # Python version
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🚀 Local Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 12+ (or Neon account)
- pip (Python package manager)
- git

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/pastebin-lite-aganitha.git
cd pastebin-lite-aganitha
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Database

**Option A: Local PostgreSQL**

```bash
# Install PostgreSQL (if not installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# Create database
createdb pastebin_db

# Set DATABASE_URL
export DATABASE_URL="postgresql://username:password@localhost:5432/pastebin_db"
```

**Option B: Neon (Recommended)**

1. Go to https://neon.tech and sign up (free)
2. Create a new project
3. Copy the connection string
4. Set environment variable:

```bash
export DATABASE_URL="postgresql://username:password@endpoint.neon.tech/database"
```

### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your DATABASE_URL
# nano .env
```

### Step 6: Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Web Interface:** http://localhost:8000
- **API:** http://localhost:8000/api/
- **Health Check:** http://localhost:8000/api/healthz

## 📡 API Documentation

### 1. Health Check

**Endpoint:** `GET /api/healthz`

**Description:** Check application and database health

**Response 200:**
```json
{
  "ok": true
}
```

**Example:**
```bash
curl http://localhost:8000/api/healthz
```

---

### 2. Create Paste

**Endpoint:** `POST /api/pastes`

**Description:** Create a new paste with optional constraints

**Request Body:**
```json
{
  "content": "string",          // Required: paste content
  "ttl_seconds": 3600,          // Optional: TTL in seconds (>=1)
  "max_views": 10               // Optional: max views (>=1)
}
```

**Response 200:**
```json
{
  "id": "abc123xyz",
  "url": "https://your-app.onrender.com/p/abc123xyz"
}
```

**Response 400 (Invalid Input):**
```json
{
  "error": "content must be a non-empty string"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/pastes \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, World!",
    "ttl_seconds": 3600,
    "max_views": 5
  }'
```

---

### 3. Fetch Paste

**Endpoint:** `GET /api/pastes/:id`

**Description:** Fetch a paste by ID. **Note: Each API fetch counts as a view!**

**Response 200:**
```json
{
  "content": "Hello, World!",
  "remaining_views": 4,
  "expires_at": "2026-01-31T12:00:00.000Z"
}
```

**Response 404:**
```json
{
  "error": "Paste not found"
}
```

**Example:**
```bash
curl http://localhost:8000/api/pastes/abc123xyz
```

---

### 4. View Paste (HTML)

**Endpoint:** `GET /p/:id`

**Description:** View paste in browser. **This does NOT count as a view.**

**Response:** HTML page with paste content

**Example:**
```
https://your-app.onrender.com/p/abc123xyz
```

## 🧪 Testing

### Deterministic Time Testing

The application supports deterministic time testing via the `TEST_MODE` environment variable.

**Enable Test Mode:**
```bash
export TEST_MODE=1
```

**Use Test Time Header:**
```bash
curl -H "x-test-now-ms: 1704067200000" \
  http://localhost:8000/api/pastes/abc123
```

When `TEST_MODE=1`, the application uses the timestamp from `x-test-now-ms` header instead of actual system time for expiry calculations.

### Manual Testing

1. **Create a paste:**
```bash
curl -X POST http://localhost:8000/api/pastes \
  -H "Content-Type: application/json" \
  -d '{"content":"Test paste", "ttl_seconds":60, "max_views":3}'
```

2. **Fetch it via API (counts as view):**
```bash
curl http://localhost:8000/api/pastes/PASTE_ID
```

3. **View in browser (does NOT count):**
```
http://localhost:8000/p/PASTE_ID
```

## 🚀 Deployment to Render

### Prerequisites

1. GitHub account
2. Render account (https://render.com - free tier available)
3. Neon account (https://neon.tech - free tier available)

### Step 1: Set Up Database (Neon)

1. Go to https://neon.tech
2. Sign up/Login
3. Click "Create Project"
4. Choose a name and region
5. Copy the connection string (starts with `postgresql://`)

### Step 2: Push Code to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Pastebin-Lite application"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/pastebin-lite-aganitha.git

# Push
git push -u origin main
```

### Step 3: Deploy on Render

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click "New +" → "Web Service"

2. **Connect GitHub Repository**
   - Select your `pastebin-lite-aganitha` repository
   - Click "Connect"

3. **Configure Service**
   - **Name:** `pastebin-lite` (or your choice)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** Leave empty
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

4. **Set Environment Variables**
   - Click "Advanced"
   - Add environment variable:
     - **Key:** `DATABASE_URL`
     - **Value:** Your Neon PostgreSQL connection string
   
5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)

6. **Access Your App**
   - Once deployed, you'll get a URL like:
   - `https://pastebin-lite-xxxx.onrender.com`

### Step 4: Verify Deployment

```bash
# Health check
curl https://your-app.onrender.com/api/healthz

# Create a paste
curl -X POST https://your-app.onrender.com/api/pastes \
  -H "Content-Type: application/json" \
  -d '{"content":"Deployment test!"}'
```

### Continuous Deployment

After initial setup, any push to the `main` branch will automatically trigger a new deployment on Render.

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render automatically deploys!
```

## 🎨 Design Decisions

### 1. FastAPI Framework

**Decision:** Use FastAPI instead of Flask or Django

**Rationale:**
- Modern async/await support for better performance
- Automatic request/response validation with Pydantic
- Built-in API documentation (OpenAPI/Swagger)
- Type hints throughout for better code quality
- Excellent for building APIs
- Great performance (comparable to Node.js)

### 2. PostgreSQL Database

**Decision:** Use PostgreSQL instead of Redis or MongoDB

**Rationale:**
- **ACID Compliance:** Ensures data integrity
- **Relational Model:** Perfect for paste data structure
- **Indexing:** Fast lookups by paste ID
- **Free Tier:** Neon provides generous free hosting
- **Mature Ecosystem:** Well-tested, reliable
- **Scalability:** Can handle millions of pastes

### 3. SQLAlchemy ORM

**Decision:** Use SQLAlchemy instead of raw SQL

**Rationale:**
- **Type Safety:** Catches errors at development time
- **Cleaner Code:** Pythonic database operations
- **Database Agnostic:** Easy to switch databases if needed
- **Migration Support:** Alembic integration available
- **Relationship Management:** Easier to add features later

### 4. Modular Code Structure

**Decision:** Separate concerns into modules

**Rationale:**
- `database.py` - Database connection logic
- `models.py` - Database schema (single source of truth)
- `schemas.py` - Request/response validation
- `utils.py` - Helper functions
- `main.py` - Routes and business logic

This makes the code:
- Easier to understand
- Easier to test
- Easier to maintain
- Easier to extend

### 5. Deterministic Time Testing

**Decision:** Support TEST_MODE with x-test-now-ms header

**Rationale:**
- Allows automated tests to verify TTL expiry
- No need to wait for actual time to pass
- Test mode is opt-in (environment variable)
- Doesn't affect production behavior

### 6. View Counting Strategy

**Decision:** API fetches count as views, HTML views don't

**Rationale:**
- **Testing:** Automated tests need predictable view counting
- **User Experience:** Users can preview their own pastes without consuming views
- **Clear Separation:** API for programmatic access, HTML for humans

### 7. Security Measures

**Implemented:**
- **XSS Prevention:** Jinja2 auto-escaping
- **SQL Injection:** SQLAlchemy ORM parameterized queries
- **Secure IDs:** `secrets.token_urlsafe()` for unpredictable paste IDs
- **Input Validation:** Pydantic models validate all input
- **No Hardcoded Secrets:** Environment variables only

### 8. Error Handling

**Decision:** Consistent JSON error responses

**Rationale:**
- All API errors return JSON (never HTML)
- Consistent error format: `{"error": "message"}`
- Proper HTTP status codes (400, 404, 500)
- Helps automated tests and API consumers

### 9. Database Indexes

**Decision:** Index on paste `id` column (primary key)

**Rationale:**
- 99% of queries are lookups by ID
- Primary key automatically creates index
- Fast O(log n) lookups
- Essential for performance at scale

### 10. Deployment Stack

**Decision:** Render + Neon

**Rationale:**
- **Render:** Easy deployment, free tier, auto-deploys from GitHub
- **Neon:** Serverless PostgreSQL, free tier, auto-scaling
- **No DevOps:** Fully managed infrastructure
- **Cost:** Free for small/medium traffic
- **Reliability:** Professional hosting infrastructure

## 📝 Code Organization Explained

### app/database.py
Handles database connection and session management. Provides:
- `get_db()` - Dependency injection for database sessions
- `init_db()` - Creates tables on startup
- `check_db_connection()` - Health check helper

### app/models.py
Defines the database schema using SQLAlchemy ORM:
- `Paste` model represents the `pastes` table
- Methods: `is_expired()`, `is_view_limit_reached()`, `is_available()`
- Clear, documented data structure

### app/schemas.py
Pydantic models for request/response validation:
- `PasteCreate` - Validates create paste requests
- `PasteResponse` - Standardizes create responses
- `PasteFetch` - Standardizes fetch responses
- Automatic validation with helpful error messages

### app/utils.py
Helper functions used throughout the app:
- `generate_paste_id()` - Creates secure random IDs
- `get_current_time()` - Handles TEST_MODE for testing
- `calculate_expiry_time()` - TTL calculations
- `format_datetime_iso()` - Consistent timestamp formatting

### app/main.py
Core FastAPI application:
- All route handlers
- Business logic
- Error handling
- Dependency injection

## 🔍 Understanding the Code Flow

### Creating a Paste

1. User submits form → POST `/api/pastes`
2. Pydantic validates request body (`schemas.PasteCreate`)
3. Generate unique ID (`utils.generate_paste_id()`)
4. Calculate expiry if TTL set (`utils.calculate_expiry_time()`)
5. Create `Paste` object (`models.Paste`)
6. Save to database (SQLAlchemy)
7. Return ID and URL (`schemas.PasteResponse`)

### Fetching a Paste

1. Request → GET `/api/pastes/:id`
2. Get current time (respects TEST_MODE)
3. Query database for paste
4. Check if expired (`paste.is_expired()`)
5. Check if view limit reached (`paste.is_view_limit_reached()`)
6. Increment view count
7. Return paste data

### Viewing HTML

1. Request → GET `/p/:id`
2. Same checks as API fetch
3. Render Jinja2 template
4. Display content (auto-escaped for XSS protection)

## 🤝 Contributing

This project is a take-home assignment demonstration, but feel free to fork and extend it!

## 📄 License

MIT License - Free to use and modify

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- Render for easy deployment
- Neon for serverless PostgreSQL
- Aganitha for the take-home assignment

---

**Built with ❤️ for Aganitha Take-Home Assignment**

**Author:** [Your Name]  
**Date:** January 2026  
**Time Investment:** ~4 hours
