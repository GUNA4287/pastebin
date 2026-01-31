#!/bin/bash

# Quick Fix Script for Pastebin-Lite Templates Error
# This script applies the fix automatically

echo "🔧 Applying fix for templates directory issue..."
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: app/main.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Create backup
echo "📦 Creating backup of app/main.py..."
cp app/main.py app/main.py.backup
echo "✅ Backup created: app/main.py.backup"
echo ""

# Apply the fix
echo "🔨 Applying the fix..."

# Fix 1: Update templates initialization
sed -i.tmp '33s|.*|# Set up Jinja2 templates for HTML pages\
# Use absolute path to ensure it works in all environments\
import os\
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))|' app/main.py

rm -f app/main.py.tmp

echo "✅ Fix applied successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Review the changes: git diff app/main.py"
echo "2. Test locally: uvicorn app.main:app --reload"
echo "3. Commit and push:"
echo "   git add app/main.py"
echo "   git commit -m 'Fix templates path for production'"
echo "   git push origin main"
echo ""
echo "4. Render will automatically redeploy (2-3 minutes)"
echo ""
echo "🎉 Done! Your /p/ route should work after redeployment."
