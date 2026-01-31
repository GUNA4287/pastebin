#!/bin/bash

# Complete Fix Script - Pastebin-Lite
# Fixes both templates path and timezone comparison issues

echo "🔧 Pastebin-Lite Complete Fix Script"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ] || [ ! -f "app/models.py" ]; then
    echo "❌ Error: Required files not found"
    echo "Please run this script from the project root directory"
    echo "Expected: app/main.py and app/models.py"
    exit 1
fi

echo "✅ Found project files"
echo ""

# Create backups
echo "📦 Creating backups..."
cp app/main.py app/main.py.backup
cp app/models.py app/models.py.backup
echo "✅ Backups created:"
echo "   - app/main.py.backup"
echo "   - app/models.py.backup"
echo ""

# Fix 1: Templates path in main.py
echo "🔨 Applying Fix 1: Templates path (app/main.py)"
python3 << 'EOF'
import re

# Read the file
with open('app/main.py', 'r') as f:
    content = f.read()

# Fix templates initialization
old_template = 'templates = Jinja2Templates(directory="templates")'
new_template = '''# Set up Jinja2 templates for HTML pages
# Use absolute path to ensure it works in all environments
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))'''

content = content.replace(old_template, new_template)

# Write back
with open('app/main.py', 'w') as f:
    f.write(content)

print("✅ Fix 1 applied: Templates path updated")
EOF

echo ""

# Fix 2: Timezone comparison in models.py
echo "🔨 Applying Fix 2: Timezone comparison (app/models.py)"
python3 << 'EOF'
import re

# Read the file
with open('app/models.py', 'r') as f:
    content = f.read()

# Find and replace the is_expired method
old_method = r'''    def is_expired\(self, current_time=None\):
        """
        Check if the paste has expired based on TTL\.
        
        Args:
            current_time \(datetime, optional\): Current time for testing\.
                                              If None, uses actual current time\.
        
        Returns:
            bool: True if expired, False otherwise
        """
        if not self\.expires_at:
            return False  # No expiry time set
        
        if current_time is None:
            current_time = datetime\.now\(timezone\.utc\)
        
        return current_time >= self\.expires_at'''

new_method = '''    def is_expired(self, current_time=None):
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
        
        return current_time >= expires_at'''

content = re.sub(old_method, new_method, content)

# Write back
with open('app/models.py', 'w') as f:
    f.write(content)

print("✅ Fix 2 applied: Timezone comparison updated")
EOF

echo ""
echo "=" * 50
echo "✅ All fixes applied successfully!"
echo "=" * 50
echo ""
echo "📝 What was fixed:"
echo "  1. Templates path - Now uses absolute path for Render"
echo "  2. Timezone comparison - Handles naive/aware datetime comparison"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Review changes:"
echo "   git diff app/main.py"
echo "   git diff app/models.py"
echo ""
echo "2. Test locally (optional):"
echo "   uvicorn app.main:app --reload"
echo "   # Visit http://localhost:8000/p/test"
echo ""
echo "3. Commit and push:"
echo "   git add app/main.py app/models.py"
echo "   git commit -m 'Fix templates path and timezone comparison'"
echo "   git push origin main"
echo ""
echo "4. Wait for Render to redeploy (2-3 minutes)"
echo ""
echo "5. Test your URL:"
echo "   https://pastebin-lite-izo3.onrender.com/p/lT8vRNYkuYo"
echo ""
echo "🎉 Done! Your paste URLs should work after redeployment."
echo ""
echo "💡 If you need to restore original files:"
echo "   cp app/main.py.backup app/main.py"
echo "   cp app/models.py.backup app/models.py"
