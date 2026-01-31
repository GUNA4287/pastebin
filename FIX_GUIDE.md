# 🔧 FIX GUIDE - 500 Error on /p/ Route

## Problem

You're getting a **500 Internal Server Error** when trying to view pastes at URLs like:
```
https://pastebin-lite-izo3.onrender.com/p/PVSz1nmBmt0
```

The paste is created successfully in the database, but viewing it fails.

## Root Cause

The issue is with the **templates directory path** in `app/main.py`.

**Current code (Line 33):**
```python
templates = Jinja2Templates(directory="templates")
```

**Problem:** 
- On Render, when the app runs via `gunicorn app.main:app`, the working directory is the project root
- The relative path `"templates"` works locally but fails on Render because Python's working directory context is different
- This causes Jinja2 to fail when trying to load `view_paste.html`

## Solution

Replace the templates initialization with an **absolute path**:

### Step 1: Open `app/main.py`

Find line 33 which says:
```python
templates = Jinja2Templates(directory="templates")
```

### Step 2: Replace with absolute path code

Replace it with:
```python
# Set up Jinja2 templates for HTML pages
# Use absolute path to ensure it works in all environments
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
```

### Step 3: Also improve error logging (Optional but recommended)

Find the exception handler around line 390:
```python
except Exception as e:
    print(f"Error viewing paste: {e}")
    return HTMLResponse(
        content="<html><body><h1>500 - Internal Server Error</h1></body></html>",
        status_code=500
    )
```

Replace with:
```python
except Exception as e:
    # Log the full error for debugging
    import traceback
    print(f"Error viewing paste: {e}")
    print(traceback.format_exc())
    return HTMLResponse(
        content=f"<html><body><h1>500 - Internal Server Error</h1><p>Error: {str(e)}</p></body></html>",
        status_code=500
    )
```

This will show you the actual error message in the browser, making debugging easier.

## How to Deploy the Fix

### Method 1: Push to GitHub (Recommended)

```bash
# Navigate to your project
cd pastebin-main

# Stage the changes
git add app/main.py

# Commit
git commit -m "Fix templates path for Render deployment"

# Push to GitHub
git push origin main

# Render will automatically detect the push and redeploy
# Wait 2-3 minutes for the new deployment
```

### Method 2: Manual File Edit on GitHub

1. Go to your GitHub repository
2. Navigate to `app/main.py`
3. Click the pencil icon (Edit)
4. Make the changes above
5. Commit directly to `main` branch
6. Render will auto-deploy

## Verification

After deployment, test the fix:

1. **Create a new paste:**
   ```bash
   curl -X POST https://pastebin-lite-izo3.onrender.com/api/pastes \
     -H "Content-Type: application/json" \
     -d '{"content":"Testing the fix!"}'
   ```

2. **Copy the URL from the response**

3. **Open it in your browser**
   - Should now show the paste content
   - No more 500 error!

## Why This Fix Works

```python
# OLD (relative path):
templates = Jinja2Templates(directory="templates")
# Looks for: <current_working_directory>/templates
# On Render: Fails because working directory is unpredictable

# NEW (absolute path):
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Gets: /app (parent of app/main.py)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
# Looks for: /app/templates
# Works everywhere: local, Render, Docker, etc.
```

**Explanation:**
- `__file__` → `/app/app/main.py` (absolute path to current file)
- `os.path.abspath(__file__)` → ensures it's absolute
- `os.path.dirname(...)` (first) → `/app/app` (parent directory)
- `os.path.dirname(...)` (second) → `/app` (grandparent directory)
- `os.path.join(BASE_DIR, "templates")` → `/app/templates` ✅

## Additional Tips

### Check Render Logs

1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Look for error messages like:
   ```
   jinja2.exceptions.TemplateNotFound: view_paste.html
   ```

### Test Locally First

Before deploying, test locally:

```bash
# Run the app
uvicorn app.main:app --reload

# Test in browser
http://localhost:8000/p/test_id

# Should work now!
```

### Common Related Issues

**Issue:** Still getting 500 error after fix
**Solution:** 
- Clear browser cache
- Wait 5 minutes for Render to fully deploy
- Check Render logs for other errors

**Issue:** Home page works but /p/ doesn't
**Solution:** 
- Verify `templates/view_paste.html` exists in your repo
- Check file permissions (should be readable)

**Issue:** Different error now
**Solution:**
- Check the new error message (now visible with improved logging)
- Look in Render logs for stack trace

## Prevention

To prevent similar issues in the future:

1. **Always use absolute paths** for file system operations
2. **Test in production-like environment** before deploying
3. **Add comprehensive error logging** to catch issues early
4. **Check Render logs** immediately after deployment

## Complete Fixed main.py Section

Here's how the top of your `app/main.py` should look after the fix:

```python
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
```

## Summary

**Problem:** Templates directory not found on Render  
**Cause:** Relative path doesn't work in production  
**Solution:** Use absolute path with `os.path` methods  
**Deploy:** Push to GitHub, Render auto-deploys  
**Result:** /p/ routes now work! ✅

---

**Need more help?** Check Render logs or the error message in the browser (with improved logging).
