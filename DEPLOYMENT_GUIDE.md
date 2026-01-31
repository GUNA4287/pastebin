# Complete Deployment Guide - Render + GitHub + Neon

This guide provides step-by-step instructions for deploying Pastebin-Lite to Render with PostgreSQL from Neon.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Database (Neon)](#step-1-setup-database-neon)
3. [Upload Code to GitHub](#step-2-upload-code-to-github)
4. [Deploy on Render](#step-3-deploy-on-render)
5. [Verification](#step-4-verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ GitHub account (free) - https://github.com/signup
- ✅ Render account (free) - https://dashboard.render.com/register
- ✅ Neon account (free) - https://console.neon.tech/signup
- ✅ Project code ready (this repository)

**Estimated Time:** 15-20 minutes

---

## Step 1: Setup Database (Neon)

### 1.1 Create Neon Account

1. Go to https://neon.tech
2. Click "Sign Up" or "Get Started"
3. Sign up with GitHub (recommended) or email
4. Verify your email if required

### 1.2 Create PostgreSQL Database

1. **After login**, you'll see the Neon Console
2. Click **"Create Project"** button
3. Fill in the details:
   - **Project Name:** `pastebin-lite`
   - **PostgreSQL Version:** 15 (latest stable)
   - **Region:** Choose closest to your target users
     - US East (N. Virginia) - For US users
     - EU West (Frankfurt) - For EU users
     - Asia Pacific (Singapore) - For Asia users
4. Click **"Create Project"**

### 1.3 Get Connection String

1. After project is created, you'll see the **Connection Details** page
2. Find the **Connection String** section
3. Copy the **Connection String** (it looks like this):
   ```
   postgresql://username:password@ep-xxxx-xxxx.region.aws.neon.tech/neondb?sslmode=require
   ```
4. **IMPORTANT:** Save this somewhere safe - you'll need it for Render!

### 1.4 Test Connection (Optional)

If you want to verify your database works:

```bash
# Install psql (PostgreSQL client)
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql-client

# Connect to your database
psql "postgresql://username:password@ep-xxxx-xxxx.region.aws.neon.tech/neondb?sslmode=require"

# You should see a postgres prompt
# Type \q to quit
```

---

## Step 2: Upload Code to GitHub

### 2.1 Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in details:
   - **Repository name:** `pastebin-lite-aganitha`
   - **Description:** "Pastebin-Lite web application for Aganitha take-home assignment"
   - **Visibility:** Public
   - **Do NOT** initialize with README (we already have one)
4. Click **"Create repository"**

### 2.2 Push Code to GitHub

Open terminal in your project directory and run:

```bash
# Navigate to project directory
cd pastebin-lite-aganitha

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Pastebin-Lite application"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/pastebin-lite-aganitha.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2.3 Verify Upload

1. Go to your repository on GitHub
2. You should see all your files:
   - `app/` folder
   - `templates/` folder
   - `README.md`
   - `requirements.txt`
   - `Procfile`
   - etc.

---

## Step 3: Deploy on Render

### 3.1 Create Render Account

1. Go to https://dashboard.render.com/register
2. Sign up with GitHub (recommended) - this makes repo connection easier
3. Authorize Render to access your GitHub account

### 3.2 Create New Web Service

1. **In Render Dashboard**, click **"New +"** (top right)
2. Select **"Web Service"**

### 3.3 Connect GitHub Repository

1. You'll see **"Connect a repository"** page
2. If you signed up with GitHub:
   - You'll see a list of your repositories
   - Find `pastebin-lite-aganitha`
   - Click **"Connect"**
3. If you didn't sign up with GitHub:
   - Click **"Configure account"**
   - Connect your GitHub account
   - Then find and connect your repository

### 3.4 Configure Web Service

Fill in the deployment configuration:

**Basic Settings:**
- **Name:** `pastebin-lite` (or your preferred name)
  - This will be part of your URL: `pastebin-lite.onrender.com`
- **Region:** Choose same region as your Neon database
- **Branch:** `main`
- **Root Directory:** (leave empty)

**Build & Deploy:**
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

**Instance Type:**
- Select **"Free"** (for testing and low traffic)
- Note: Free tier services sleep after 15 min of inactivity

### 3.5 Set Environment Variables

1. Scroll down to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add the following:

   **Variable 1:**
   - **Key:** `DATABASE_URL`
   - **Value:** [Your Neon connection string from Step 1.3]
   
   **Variable 2 (Optional - only for testing):**
   - **Key:** `TEST_MODE`
   - **Value:** `0`

4. Click **"Create Web Service"**

### 3.6 Wait for Deployment

1. Render will now:
   - Clone your repository
   - Install dependencies
   - Start your application
2. This usually takes **2-5 minutes**
3. You'll see build logs in real-time
4. Wait for the status to show **"Live"** (green)

### 3.7 Get Your URL

Once deployed, you'll see your app URL at the top:
```
https://pastebin-lite-xxxx.onrender.com
```

---

## Step 4: Verification

### 4.1 Test Health Check

```bash
# Replace with your actual Render URL
curl https://pastebin-lite-xxxx.onrender.com/api/healthz

# Expected response:
# {"ok":true}
```

### 4.2 Test Creating a Paste

```bash
curl -X POST https://pastebin-lite-xxxx.onrender.com/api/pastes \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello from deployed app!",
    "ttl_seconds": 3600,
    "max_views": 10
  }'

# Expected response:
# {"id":"abc123xyz","url":"https://pastebin-lite-xxxx.onrender.com/p/abc123xyz"}
```

### 4.3 Test Viewing Paste

1. Copy the URL from the previous response
2. Open it in your browser
3. You should see your paste content displayed nicely

### 4.4 Test the Web Interface

1. Go to `https://pastebin-lite-xxxx.onrender.com`
2. You should see the paste creation form
3. Create a paste using the form
4. Verify you get a shareable URL
5. Click the URL to view your paste

---

## 🎉 Success!

If all tests pass, your application is successfully deployed!

**Your URLs:**
- **Home Page:** `https://pastebin-lite-xxxx.onrender.com`
- **API Health:** `https://pastebin-lite-xxxx.onrender.com/api/healthz`
- **API Docs:** `https://pastebin-lite-xxxx.onrender.com/docs` (auto-generated)

---

## Troubleshooting

### Issue: Build Failed

**Symptoms:** Red "Deploy failed" message

**Solutions:**
1. Check build logs for specific error
2. Verify `requirements.txt` has all dependencies
3. Ensure `runtime.txt` specifies Python 3.11+
4. Check that `Procfile` exists and has correct start command

**Common Fixes:**
```bash
# Make sure all files are committed and pushed
git add .
git commit -m "Fix deployment"
git push origin main

# Render will auto-deploy on push
```

### Issue: Application Starts but Crashes

**Symptoms:** "Service unavailable" or 502 error

**Solutions:**
1. Check Render logs (Dashboard → Your Service → Logs)
2. Common causes:
   - Invalid `DATABASE_URL`
   - Missing environment variables
   - Port binding issues

**Fixes:**
1. Verify `DATABASE_URL` is correct (copy from Neon again)
2. Ensure Procfile uses `$PORT` variable:
   ```
   --bind 0.0.0.0:$PORT
   ```

### Issue: Database Connection Failed

**Symptoms:** `{"ok":false}` from health check

**Solutions:**
1. Verify Neon database is active
2. Check DATABASE_URL has `?sslmode=require` at the end
3. Test connection locally:
   ```bash
   export DATABASE_URL="your_neon_url"
   python -c "from app.database import check_db_connection; print(check_db_connection())"
   ```

### Issue: 404 Not Found for All Routes

**Symptoms:** All endpoints return 404

**Solutions:**
1. Check Procfile has correct module path: `app.main:app`
2. Verify folder structure:
   ```
   /app
     ├── __init__.py
     ├── main.py
     └── ...
   ```

### Issue: Free Tier Sleep

**Symptoms:** First request is very slow (15+ seconds)

**Explanation:** Free tier services sleep after 15 minutes of inactivity

**Solutions:**
1. Upgrade to paid tier ($7/month) for always-on service
2. Use a ping service to keep it awake:
   - https://uptimerobot.com (free)
   - Configure to ping your `/api/healthz` every 5 minutes

### Issue: SSL Certificate Error

**Symptoms:** Browser shows "Not Secure" warning

**Solutions:**
1. Wait a few minutes - SSL certificates take time to provision
2. Render provides free SSL automatically
3. Force HTTPS by accessing `https://` URL

---

## Continuous Deployment

After initial setup, Render automatically deploys when you push to GitHub:

```bash
# Make changes to your code
nano app/main.py

# Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# Render automatically detects the push and deploys!
# Check deployment status in Render dashboard
```

---

## Monitoring & Logs

### View Logs

1. Go to Render Dashboard
2. Click on your service
3. Click **"Logs"** tab
4. See real-time application logs

### View Metrics

1. In your service dashboard
2. Click **"Metrics"** tab
3. See:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

---

## Scaling (Optional)

When your app gets more traffic:

### Upgrade Plan

1. Go to service settings
2. Change from "Free" to "Starter" ($7/month)
3. Benefits:
   - Always on (no sleep)
   - More resources
   - Better performance

### Database Scaling

1. Go to Neon console
2. Upgrade plan for:
   - More storage
   - More compute
   - Higher connection limits

---

## Cost Breakdown

**Free Tier (Good for Development/Demo):**
- Render Free: $0/month
- Neon Free: $0/month
- **Total: $0/month**

**Production (Recommended):**
- Render Starter: $7/month
- Neon Pro: $19/month (or keep free tier)
- **Total: $7-26/month**

---

## Security Checklist

Before sharing your deployment:

- ✅ Verify DATABASE_URL is set in Render (not hardcoded)
- ✅ Check .gitignore includes .env
- ✅ Ensure no secrets in GitHub repository
- ✅ Test all API endpoints
- ✅ Verify HTTPS is working
- ✅ Check error handling works

---

## Next Steps

1. **Update README.md** with your live URL
2. **Test all features** thoroughly
3. **Share your deployment** with Aganitha
4. **Monitor logs** for any issues

---

## Getting Help

**Render Documentation:** https://render.com/docs  
**Neon Documentation:** https://neon.tech/docs  
**FastAPI Documentation:** https://fastapi.tiangolo.com

**Questions?** Check the logs first - they usually have the answer!

---

**Good luck with your deployment! 🚀**
