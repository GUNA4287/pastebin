# Project Explanation - Pastebin-Lite

## 📖 Complete Project Walkthrough

This document explains every aspect of the Pastebin-Lite project in simple, understandable terms.

---

## 🎯 What is Pastebin-Lite?

Pastebin-Lite is a web application that allows users to:
1. **Create** text pastes (like notes or code snippets)
2. **Share** them via unique URLs
3. **Set expiry** time (optional)
4. **Limit views** (optional)

Think of it like a simple, temporary text sharing service.

---

## 🏗️ Architecture Overview

### High-Level Flow

```
User's Browser
    ↓
    ↓ (HTTPS Request)
    ↓
Render.com Server
    ↓
    ↓ (FastAPI Application)
    ↓
PostgreSQL Database (Neon)
```

### Component Breakdown

1. **Frontend (What user sees)**
   - HTML pages (templates/)
   - CSS styling (embedded in HTML)
   - JavaScript (for form submission)

2. **Backend (Application logic)**
   - FastAPI web framework (app/main.py)
   - Database models (app/models.py)
   - Request validation (app/schemas.py)
   - Utility functions (app/utils.py)

3. **Database (Data storage)**
   - PostgreSQL database on Neon
   - Stores all paste data
   - Handles queries efficiently

4. **Hosting**
   - Render.com (application hosting)
   - Neon.tech (database hosting)

---

## 📁 Project Structure Explained

```
pastebin-lite-aganitha/
│
├── app/                          # Main application code
│   ├── __init__.py              # Makes 'app' a Python package
│   ├── main.py                  # FastAPI app with all routes
│   ├── database.py              # Database connection setup
│   ├── models.py                # Database table definitions
│   ├── schemas.py               # Request/response validation
│   └── utils.py                 # Helper functions
│
├── templates/                    # HTML templates
│   ├── index.html               # Home page (create paste)
│   └── view_paste.html          # View paste page
│
├── requirements.txt             # Python packages needed
├── Procfile                     # Tells Render how to run app
├── runtime.txt                  # Specifies Python version
├── .env.example                 # Example environment variables
├── .gitignore                   # Files to ignore in git
└── README.md                    # Project documentation
```

---

## 🔍 How Each File Works

### app/main.py - The Core Application

**Purpose:** This is the heart of the application. It handles all HTTP requests.

**What it does:**
1. **Receives requests** from users' browsers
2. **Validates input** (is the paste content valid?)
3. **Saves to database** (store the paste)
4. **Returns responses** (send back the paste URL)

**Key Routes:**
```python
@app.get("/")                    # Home page
@app.get("/p/{paste_id}")        # View paste
@app.post("/api/pastes")         # Create paste
@app.get("/api/pastes/{id}")     # Fetch paste (API)
@app.get("/api/healthz")         # Health check
```

**Example Flow:**
```
User clicks "Create Paste"
    ↓
Browser sends POST to /api/pastes
    ↓
main.py receives request
    ↓
Validates data with schemas.py
    ↓
Generates unique ID with utils.py
    ↓
Saves to database with models.py
    ↓
Returns {"id": "abc123", "url": "..."}
```

---

### app/database.py - Database Connection

**Purpose:** Manages connection to PostgreSQL database.

**What it does:**
1. **Connects to database** using SQLAlchemy
2. **Creates sessions** for each request
3. **Initializes tables** on application startup

**Key Functions:**

```python
get_db()
# Returns a database session
# Used in routes like: db: Session = Depends(get_db)

init_db()
# Creates all database tables
# Called when app starts

check_db_connection()
# Tests if database is reachable
# Used in health check endpoint
```

**Connection Flow:**
```
Application starts
    ↓
Reads DATABASE_URL from environment
    ↓
Creates SQLAlchemy engine
    ↓
Creates session factory
    ↓
Ready to handle requests!
```

---

### app/models.py - Database Schema

**Purpose:** Defines the structure of data in the database.

**The Paste Model:**
```python
class Paste(Base):
    id              # Unique identifier (e.g., "abc123")
    content         # The actual text
    ttl_seconds     # Time-to-live (optional)
    max_views       # View limit (optional)
    current_views   # How many times viewed
    created_at      # When created
    expires_at      # When it expires
    is_active       # Is it still available?
```

**Helpful Methods:**
```python
paste.is_expired()
# Returns True if paste has expired

paste.is_view_limit_reached()
# Returns True if all views used up

paste.is_available()
# Returns True if paste can still be viewed

paste.get_remaining_views()
# Returns number of views left
```

**Example in Database:**
```sql
id: "x4K_9mPq"
content: "Hello, World!"
ttl_seconds: 3600
max_views: 10
current_views: 3
created_at: 2026-01-30 10:00:00
expires_at: 2026-01-30 11:00:00
is_active: true
```

---

### app/schemas.py - Input/Output Validation

**Purpose:** Ensures data is valid before processing.

**Request Schemas (Input):**
```python
PasteCreate
# Validates when creating a paste
# Checks: content is not empty, ttl >= 1, max_views >= 1
```

**Response Schemas (Output):**
```python
PasteResponse
# {"id": "...", "url": "..."}

PasteFetch
# {"content": "...", "remaining_views": 5, "expires_at": "..."}

HealthResponse
# {"ok": true}
```

**How Validation Works:**
```
User sends:
{
  "content": "",      ← Invalid (empty)
  "ttl_seconds": -1   ← Invalid (negative)
}

Pydantic validates:
    ↓
Raises error:
    ↓
Returns 400 Bad Request:
{
  "error": "content must be a non-empty string"
}
```

---

### app/utils.py - Helper Functions

**Purpose:** Reusable functions used throughout the app.

**Key Functions:**

```python
generate_paste_id()
# Creates random secure ID like "x4K_9mPq"
# Uses Python's secrets module (cryptographically secure)

get_current_time(request)
# Returns current time
# In TEST_MODE, uses x-test-now-ms header

calculate_expiry_time(created_at, ttl_seconds)
# Adds TTL to creation time
# Returns when paste will expire

format_datetime_iso(datetime)
# Converts datetime to "2026-01-30T12:00:00.000Z"
# Standard format for API responses

build_paste_url(request, paste_id)
# Creates full URL like "https://app.com/p/abc123"
```

---

### templates/index.html - Home Page

**Purpose:** The main page where users create pastes.

**Structure:**
```html
<form>
    <textarea>        ← User types paste content
    <input ttl>       ← Optional: expiry time
    <input views>     ← Optional: view limit
    <button>          ← Submit button
</form>

<script>
    // Handles form submission
    // Sends POST to /api/pastes
    // Displays result
</script>
```

**User Journey:**
1. User types text in textarea
2. Optionally sets TTL and max views
3. Clicks "Create Paste"
4. JavaScript sends request to API
5. Receives paste URL
6. Displays URL with copy button

---

### templates/view_paste.html - View Paste

**Purpose:** Displays paste content to users.

**Structure:**
```html
<h1>Paste Viewer</h1>

<div class="paste-info">
    Paste ID: {{ paste_id }}
</div>

<div class="paste-content">
    <pre>{{ content }}</pre>  ← Auto-escaped by Jinja2
</div>

<button onclick="copyContent()">
    Copy Content
</button>
```

**Security Note:**
```python
{{ content }}
# Jinja2 automatically escapes HTML
# Prevents XSS attacks

If content = "<script>alert('hack')</script>"
# Displayed as text, not executed:
# &lt;script&gt;alert('hack')&lt;/script&gt;
```

---

## 🔄 Request Flow Examples

### Example 1: Creating a Paste

**User Action:** Fills form and clicks "Create Paste"

**Backend Flow:**
```
1. Browser: POST /api/pastes
   Body: {
     "content": "Hello, World!",
     "ttl_seconds": 3600,
     "max_views": 10
   }

2. FastAPI receives request

3. Pydantic validates (schemas.PasteCreate)
   ✓ Content is not empty
   ✓ TTL is >= 1
   ✓ Max views is >= 1

4. main.create_paste() executes:
   - Generate ID: "x4K_9mPq" (utils.generate_paste_id)
   - Get current time: 2026-01-30 10:00:00
   - Calculate expiry: 2026-01-30 11:00:00
   - Create Paste object
   - Save to database

5. Build response:
   {
     "id": "x4K_9mPq",
     "url": "https://app.com/p/x4K_9mPq"
   }

6. Return to browser

7. JavaScript displays URL
```

---

### Example 2: Fetching a Paste (API)

**User Action:** API client sends GET request

**Backend Flow:**
```
1. Request: GET /api/pastes/x4K_9mPq

2. main.fetch_paste() executes:
   - Get current time (respects TEST_MODE)
   - Query database for paste
   
3. Check if paste exists
   - If not found → 404

4. Check if expired
   - Compare current time vs expires_at
   - If expired → Mark inactive → 404

5. Check if view limit reached
   - Compare current_views vs max_views
   - If reached → Mark inactive → 404

6. Increment view count
   - current_views += 1
   - Save to database

7. Build response:
   {
     "content": "Hello, World!",
     "remaining_views": 9,
     "expires_at": "2026-01-30T11:00:00.000Z"
   }

8. Return JSON
```

---

### Example 3: Viewing Paste (HTML)

**User Action:** Opens paste URL in browser

**Backend Flow:**
```
1. Request: GET /p/x4K_9mPq

2. main.view_paste() executes:
   - Same checks as API fetch
   - BUT does NOT increment view count

3. If available:
   - Render view_paste.html template
   - Pass paste_id and content
   - Jinja2 auto-escapes content

4. If not available:
   - Return 404 HTML page
   - Show friendly error message

5. Browser receives HTML
   - Displays formatted paste
   - Shows copy button
```

---

## 🧪 Testing Features

### Deterministic Time Testing

**Problem:** How to test TTL expiry without waiting?

**Solution:** TEST_MODE with x-test-now-ms header

**How it works:**
```
1. Set environment variable:
   TEST_MODE=1

2. Send request with header:
   x-test-now-ms: 1704067200000

3. get_current_time() function:
   if TEST_MODE == "1":
       use header value
   else:
       use actual current time

4. Expiry calculation uses test time
   - Can simulate future without waiting!
```

**Example Test:**
```bash
# Create paste with 60 second TTL
curl POST /api/pastes -d '{"content":"test","ttl_seconds":60}'
# Response: {"id":"abc123",...}

# Fetch immediately (works)
curl GET /api/pastes/abc123
# Response: 200 OK

# Fetch 70 seconds later (simulated)
curl -H "x-test-now-ms:1704067270000" GET /api/pastes/abc123
# Response: 404 (expired)
```

---

## 🔐 Security Measures

### 1. XSS Prevention

**Problem:** User could inject malicious JavaScript

**Solution:** Jinja2 auto-escaping

```python
# Malicious input:
content = '<script>alert("XSS")</script>'

# In template:
{{ content }}

# Rendered as:
&lt;script&gt;alert("XSS")&lt;/script&gt;

# Displays as text, doesn't execute!
```

### 2. SQL Injection Prevention

**Problem:** User could inject SQL commands

**Solution:** SQLAlchemy ORM with parameterized queries

```python
# BAD (vulnerable):
db.execute(f"SELECT * FROM pastes WHERE id = '{paste_id}'")

# GOOD (safe):
db.query(Paste).filter(Paste.id == paste_id).first()

# SQLAlchemy automatically escapes and parameterizes
```

### 3. Secure ID Generation

**Problem:** Predictable IDs could be guessed

**Solution:** cryptographically secure random IDs

```python
import secrets

def generate_paste_id():
    return secrets.token_urlsafe(8)
    # Returns: "x4K_9mPq" (impossible to guess)
```

### 4. Input Validation

**Problem:** Invalid data could crash the app

**Solution:** Pydantic models validate all input

```python
class PasteCreate(BaseModel):
    content: str
    ttl_seconds: Optional[int]
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('content must be non-empty')
        return v
```

---

## 📊 Database Design

### Why PostgreSQL?

1. **ACID Compliance**
   - Atomicity: All-or-nothing transactions
   - Consistency: Data always valid
   - Isolation: Concurrent requests don't interfere
   - Durability: Data persists after save

2. **Indexing**
   - Primary key on `id` column
   - Fast lookups: O(log n) instead of O(n)
   - Crucial for performance

3. **Scalability**
   - Can handle millions of pastes
   - Connection pooling
   - Efficient queries

### Schema Design

**Single Table Approach:**
```sql
CREATE TABLE pastes (
    id VARCHAR(50) PRIMARY KEY,      -- Indexed automatically
    content TEXT NOT NULL,            -- No length limit
    ttl_seconds INTEGER,              -- NULL = no expiry
    max_views INTEGER,                -- NULL = unlimited
    current_views INTEGER DEFAULT 0,  -- Incremented on fetch
    created_at TIMESTAMP NOT NULL,    -- For auditing
    expires_at TIMESTAMP,             -- Pre-calculated
    is_active BOOLEAN DEFAULT TRUE    -- Soft delete
);
```

**Why single table?**
- Simple queries (no JOINs)
- Fast operations
- Easy to understand
- Suitable for this use case

---

## 🚀 Deployment Process

### Local → GitHub → Render → Production

```
1. Develop Locally
   ↓
   - Write code
   - Test with local PostgreSQL
   - Verify all features work

2. Push to GitHub
   ↓
   git add .
   git commit -m "message"
   git push origin main

3. Render Deployment
   ↓
   - Detects push to main
   - Runs: pip install -r requirements.txt
   - Starts: gunicorn app.main:app ...
   - Connects to Neon database

4. Live in Production!
   ↓
   https://pastebin-lite-xxxx.onrender.com
```

---

## 💡 Design Decisions Explained

### Why FastAPI?

**Alternatives considered:** Flask, Django

**Chose FastAPI because:**
- Modern async/await support
- Automatic request validation
- Built-in API documentation
- Great performance
- Type safety
- Easy to learn

### Why PostgreSQL?

**Alternatives considered:** Redis, MongoDB, SQLite

**Chose PostgreSQL because:**
- ACID compliance (data integrity)
- Free tier available (Neon)
- Mature and reliable
- Perfect for structured data
- Powerful query capabilities

### Why Render?

**Alternatives considered:** Vercel, Heroku, Railway

**Chose Render because:**
- Free tier available
- Easy GitHub integration
- Auto-deploys on push
- Good for Python apps
- Simple configuration

### Why Separate API and HTML Views?

**Decision:** /api/pastes/:id (counts views) vs /p/:id (doesn't count)

**Reasoning:**
- API for programmatic access (testing, automation)
- HTML for humans (browsing, sharing)
- Keeps view counting predictable for tests
- Better user experience (preview doesn't waste views)

---

## 🎓 Learning Points

### For Understanding the Code

1. **Read in this order:**
   - app/models.py (understand data structure)
   - app/schemas.py (understand validation)
   - app/utils.py (understand helpers)
   - app/database.py (understand connections)
   - app/main.py (understand flow)

2. **Key Concepts:**
   - **ORM (SQLAlchemy):** Maps Python classes to database tables
   - **Pydantic:** Validates data using Python type hints
   - **Async/Await:** Handles multiple requests efficiently
   - **Dependency Injection:** get_db() provides database session
   - **Template Rendering:** Jinja2 generates HTML from templates

3. **Important Patterns:**
   - Request → Validation → Processing → Response
   - Separation of concerns (each file has clear purpose)
   - DRY (Don't Repeat Yourself) - utils for common functions

---

## 🔧 How to Modify

### Adding a New Feature

**Example: Add paste title**

1. **Update model (app/models.py):**
```python
class Paste(Base):
    # ... existing fields
    title = Column(String(200), nullable=True)
```

2. **Update schema (app/schemas.py):**
```python
class PasteCreate(BaseModel):
    content: str
    title: Optional[str] = None  # New field
    # ... existing fields
```

3. **Update route (app/main.py):**
```python
new_paste = models.Paste(
    title=paste_data.title,  # Add this
    # ... existing fields
)
```

4. **Update template (templates/view_paste.html):**
```html
<h2>{{ title }}</h2>
<pre>{{ content }}</pre>
```

5. **Deploy:**
```bash
git add .
git commit -m "Add paste title feature"
git push origin main
```

---

## 📝 Summary

**This project demonstrates:**
- ✅ Full-stack web development
- ✅ RESTful API design
- ✅ Database modeling
- ✅ Input validation
- ✅ Security best practices
- ✅ Deployment workflow
- ✅ Clean code organization
- ✅ Comprehensive documentation

**Technologies mastered:**
- Python & FastAPI
- PostgreSQL & SQLAlchemy
- HTML/CSS/JavaScript
- Git & GitHub
- Render deployment
- Cloud databases (Neon)

**Total project:**
- ~1,500 lines of code
- 8 Python files
- 2 HTML templates
- Complete documentation
- Production-ready

---

**This explanation should help you understand every aspect of the project!**
