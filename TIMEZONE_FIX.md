# 🔧 TIMEZONE FIX - Complete Solution

## Error Message

```
500 - Internal Server Error
Error: can't compare offset-naive and offset-aware datetimes
```

## Problem Explanation

The error occurs when comparing:
- **Timezone-aware datetime** (from your code: `datetime.now(timezone.utc)`)
- **Timezone-naive datetime** (from PostgreSQL database)

Even though the database columns are defined as `TIMESTAMP(timezone=True)`, PostgreSQL might return them as **naive** datetimes depending on how SQLAlchemy retrieves them.

---

## The Complete Fix

You need to update **TWO files**:

### 1. Fix `app/main.py` (Templates Path - From Previous Issue)

**Line 33 - Change from:**
```python
templates = Jinja2Templates(directory="templates")
```

**To:**
```python
# Set up Jinja2 templates for HTML pages
# Use absolute path to ensure it works in all environments
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
```

### 2. Fix `app/models.py` (Timezone Comparison)

**Find the `is_expired` method (around line 80):**

**Change from:**
```python
def is_expired(self, current_time=None):
    """
    Check if the paste has expired based on TTL.
    """
    if not self.expires_at:
        return False
    
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    return current_time >= self.expires_at
```

**To:**
```python
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
    
    # Ensure both datetimes are timezone-aware for comparison
    expires_at = self.expires_at
    if expires_at.tzinfo is None:
        # Database stored as naive, make it UTC-aware
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if current_time.tzinfo is None:
        # Make current_time UTC-aware if it's naive
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    return current_time >= expires_at
```

---

## Step-by-Step Application

### Option 1: Manual Fix (Recommended)

1. **Open your project folder**
   ```bash
   cd pastebin-main
   ```

2. **Edit `app/main.py`**
   - Find line 33
   - Replace with templates fix from above
   - Save file

3. **Edit `app/models.py`**
   - Find the `is_expired` method (around line 80)
   - Replace entire method with fixed version above
   - Save file

4. **Commit and push**
   ```bash
   git add app/main.py app/models.py
   git commit -m "Fix templates path and timezone comparison"
   git push origin main
   ```

5. **Wait 2-3 minutes for Render to redeploy**

6. **Test your URL**
   ```
   https://pastebin-lite-izo3.onrender.com/p/lT8vRNYkuYo
   ```
   Should work now! ✅

### Option 2: Use the Fixed Files

I've provided complete fixed files in the ZIP. Just replace:
- `app/main.py`
- `app/models.py`

Then push to GitHub.

---

## Why This Fix Works

### The Problem:
```python
# PostgreSQL returns: 2024-01-31 10:00:00 (naive - no timezone)
# Your code uses: 2024-01-31 10:00:00+00:00 (aware - has UTC)

# Comparison fails:
current_time >= self.expires_at
# TypeError: can't compare offset-naive and offset-aware datetimes
```

### The Solution:
```python
# Check if expires_at is naive
if expires_at.tzinfo is None:
    # Add UTC timezone
    expires_at = expires_at.replace(tzinfo=timezone.utc)

# Check if current_time is naive
if current_time.tzinfo is None:
    # Add UTC timezone
    current_time = current_time.replace(tzinfo=timezone.utc)

# Now both are aware → comparison works! ✅
```

---

## After the Fix - Test It

1. **Create a new paste:**
   ```bash
   curl -X POST https://pastebin-lite-izo3.onrender.com/api/pastes \
     -H "Content-Type: application/json" \
     -d '{"content":"Timezone fix test!", "ttl_seconds": 3600}'
   ```

2. **Get the URL from response**

3. **Open in browser** → Should work! ✅

4. **Test your existing paste:**
   ```
   https://pastebin-lite-izo3.onrender.com/p/lT8vRNYkuYo
   ```
   Should also work now! ✅

---

## Verification Checklist

After applying both fixes:

- [ ] Edit `app/main.py` (templates path)
- [ ] Edit `app/models.py` (timezone comparison)
- [ ] Test locally (optional): `uvicorn app.main:app --reload`
- [ ] Create test paste locally, visit /p/ route → Should work
- [ ] Commit both files
- [ ] Push to GitHub
- [ ] Wait for Render deployment
- [ ] Test live paste URLs → Should work! ✅

---

## Additional Safety Improvement (Optional)

You can also add timezone handling to the `utils.py` get_current_time function:

**In `app/utils.py`, find `get_current_time` function and ensure it always returns timezone-aware datetime:**

```python
def get_current_time(request: Request) -> datetime:
    """
    Get the current time, with support for deterministic testing.
    Always returns timezone-aware datetime in UTC.
    """
    test_mode = os.environ.get("TEST_MODE") == "1"
    
    if test_mode:
        test_time_ms = request.headers.get("x-test-now-ms")
        if test_time_ms:
            try:
                timestamp_seconds = int(test_time_ms) / 1000
                return datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
            except (ValueError, OSError):
                pass
    
    # Always return timezone-aware datetime
    return datetime.now(timezone.utc)
```

This is already correct in your code, so no change needed!

---

## Common Questions

### Q: Why does this happen on Render but not locally?

**A:** PostgreSQL on Neon (production) might have different timezone settings than your local PostgreSQL. The database columns store timestamps, but how SQLAlchemy retrieves them can vary.

### Q: Will this affect existing pastes?

**A:** No! The fix handles both naive and aware datetimes, so existing pastes will work fine.

### Q: What if I have pastes with no expiry?

**A:** The fix checks `if not self.expires_at` first, so pastes without expiry won't be affected.

---

## Summary

**Two fixes needed:**

1. **Templates path** (`app/main.py` line 33)
   - Use absolute path instead of relative path

2. **Timezone comparison** (`app/models.py` is_expired method)
   - Handle both naive and aware datetimes

**Deploy:**
```bash
git add app/main.py app/models.py
git commit -m "Fix templates and timezone issues"
git push origin main
```

**Result:** All paste URLs will work! ✅

---

## Troubleshooting

### Still getting timezone error?

1. **Check the error message carefully**
   - Look for which line is causing the issue
   - The improved error logging will show you

2. **Verify the fix was applied**
   - Open `app/models.py` on GitHub
   - Check the `is_expired` method has the new code

3. **Clear your database and recreate pastes**
   - Old pastes might have inconsistent data
   - Create fresh test pastes after deployment

### Different error now?

With the improved error logging in `main.py`, you'll see the exact error. Check:
- Render logs
- Browser error message (now shows details)

---

**After applying both fixes, your application will work perfectly!** 🎉
