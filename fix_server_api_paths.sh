#!/bin/bash
# Fix API paths on Digital Ocean server
# Run this script on your server to fix the JavaScript API paths

echo "🔧 Fixing Database Viewer API Paths on Server..."
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "templates/database_viewer.html" ]; then
    echo "❌ Error: templates/database_viewer.html not found"
    echo "Please run this script from your application directory (e.g., /var/www/pathology-lab/)"
    exit 1
fi

echo "📁 Found templates/database_viewer.html"

# Create backup
cp templates/database_viewer.html templates/database_viewer.html.backup
echo "💾 Created backup: templates/database_viewer.html.backup"

# Fix API paths
echo "🔧 Fixing API endpoint paths..."

# Fix database-info endpoint
sed -i "s|fetch('/api/database-info')|fetch('/db-viewer/api/database-info')|g" templates/database_viewer.html

# Fix real-time-stats endpoint
sed -i "s|fetch('/api/real-time-stats')|fetch('/db-viewer/api/real-time-stats')|g" templates/database_viewer.html

# Fix table-data endpoint
sed -i "s|fetch(\`/api/table-data/|fetch(\`/db-viewer/api/table-data/|g" templates/database_viewer.html

# Fix search endpoint
sed -i "s|fetch(\`/api/search/|fetch(\`/db-viewer/api/search/|g" templates/database_viewer.html

# Fix export endpoint
sed -i "s|link.href = \`/api/export/|link.href = \`/db-viewer/api/export/|g" templates/database_viewer.html

echo "✅ API paths fixed in templates/database_viewer.html"

# Restart services
echo "🔄 Restarting services..."

if command -v systemctl &> /dev/null; then
    # SystemD systems
    sudo systemctl restart pathology-lab 2>/dev/null || echo "⚠️ pathology-lab service not found"
    sudo systemctl restart pathology-db-viewer 2>/dev/null || echo "⚠️ pathology-db-viewer service not found"
    sudo systemctl restart nginx 2>/dev/null || echo "⚠️ nginx service not found"
    echo "✅ Services restarted"
else
    echo "⚠️ SystemD not available - please restart your application manually"
fi

# Test the fix
echo "🧪 Testing API endpoints..."

# Test database info
if curl -s http://localhost:5000/db-viewer/api/database-info > /dev/null; then
    echo "✅ Database info endpoint working"
else
    echo "❌ Database info endpoint not responding"
fi

# Test real-time stats
if curl -s http://localhost:5000/db-viewer/api/real-time-stats > /dev/null; then
    echo "✅ Real-time stats endpoint working"
else
    echo "❌ Real-time stats endpoint not responding"
fi

echo ""
echo "🎉 Fix Complete!"
echo "==============="
echo ""
echo "✅ API paths corrected in database viewer"
echo "✅ Services restarted"
echo "✅ Ready to test"
echo ""
echo "🔗 Test your database viewer:"
echo "https://your-domain.com/db-viewer/"
echo ""
echo "📋 If issues persist:"
echo "1. Check application logs: sudo journalctl -u pathology-lab -f"
echo "2. Verify file permissions: ls -la templates/"
echo "3. Test API directly: curl http://localhost:5000/db-viewer/api/database-info"
echo ""
echo "🔄 To rollback if needed:"
echo "cp templates/database_viewer.html.backup templates/database_viewer.html"
