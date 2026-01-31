#!/bin/bash

# Quick Fix Script - Two Specific Issues Only
# Fix #1: Copy button
# Fix #2: View count increment

echo "🔧 Applying Two Specific Fixes"
echo "=============================="
echo ""

# Check files exist
if [ ! -f "templates/index.html" ] || [ ! -f "app/main.py" ]; then
    echo "❌ Error: Required files not found"
    echo "Run this from project root directory"
    exit 1
fi

echo "✅ Files found"
echo ""

# Backup
echo "📦 Creating backups..."
cp templates/index.html templates/index.html.backup
cp app/main.py app/main.py.backup
echo "✅ Backups created"
echo ""

# Fix #1: Copy Button (index.html)
echo "🔨 Fix #1: Copy button event parameter..."

# Fix the onclick attribute
sed -i.tmp 's|onclick="copyUrl()"|onclick="copyUrl(event)"|g' templates/index.html

# Fix the function definition
sed -i.tmp 's|function copyUrl() {|function copyUrl(event) {|g' templates/index.html

rm -f templates/index.html.tmp

echo "✅ Fix #1 applied: Copy button now receives event parameter"
echo ""

# Fix #2: View Count (main.py)
echo "🔨 Fix #2: View count increment..."

python3 << 'EOF'
import re

with open('app/main.py', 'r') as f:
    content = f.read()

# Find the section to replace
old_section = '''        # Render the paste view page
        # Jinja2 automatically escapes HTML to prevent XSS
        return templates.TemplateResponse(
            "view_paste.html",
            {
                "request": request,
                "paste_id": paste_id,
                "content": paste.content
            }
        )'''

new_section = '''        # Increment view count for HTML views
        paste.current_views += 1
        
        # Check if this view reached the limit
        if paste.is_view_limit_reached():
            paste.is_active = False
        
        db.commit()
        db.refresh(paste)
        
        # Render the paste view page
        # Jinja2 automatically escapes HTML to prevent XSS
        return templates.TemplateResponse(
            "view_paste.html",
            {
                "request": request,
                "paste_id": paste_id,
                "content": paste.content
            }
        )'''

content = content.replace(old_section, new_section)

with open('app/main.py', 'w') as f:
    f.write(content)

print("✅ Fix #2 applied: View count now increments on HTML views")
EOF

echo ""
echo "=============================="
echo "✅ Both fixes applied!"
echo "=============================="
echo ""
echo "📝 What was fixed:"
echo "  1. Copy button - Now passes event parameter"
echo "  2. View count - Now increments on every HTML view"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Review changes:"
echo "   git diff templates/index.html"
echo "   git diff app/main.py"
echo ""
echo "2. Test locally (optional):"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Commit and deploy:"
echo "   git add templates/index.html app/main.py"
echo '   git commit -m "Fix copy button and view count"'
echo "   git push origin main"
echo ""
echo "4. Wait for deployment (2-3 min)"
echo ""
echo "🎉 Done!"
