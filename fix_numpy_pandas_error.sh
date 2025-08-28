#!/bin/bash
# Fix NumPy/Pandas Binary Compatibility Error
# Run this script on your server to resolve the error

echo "🔧 Fixing NumPy/Pandas Binary Compatibility Error..."
echo "=================================================="

# Method 1: Uninstall and reinstall with compatible versions
echo "📦 Method 1: Clean installation with compatible versions"
pip uninstall -y numpy pandas
pip install numpy==1.24.3
pip install pandas==2.0.3

echo "✅ Method 1 complete"
echo ""

# Method 2: Alternative - Use server-safe requirements (no pandas)
echo "📦 Method 2: Server-safe installation (no pandas/numpy)"
echo "This method eliminates the error completely by not using pandas"
echo "CSV export will use Python's built-in csv module"
echo ""
echo "To use this method:"
echo "pip uninstall -y numpy pandas"
echo "pip install -r requirements-server.txt"
echo ""

# Method 3: Force reinstall all packages
echo "📦 Method 3: Force reinstall all packages"
echo "pip install --force-reinstall --no-cache-dir -r requirements.txt"
echo ""

# Method 4: Use virtual environment
echo "📦 Method 4: Clean virtual environment"
echo "python3 -m venv fresh_venv"
echo "source fresh_venv/bin/activate"
echo "pip install -r requirements.txt"
echo ""

echo "🎯 Recommended for production servers:"
echo "Use requirements-server.txt (no pandas) for maximum compatibility"
echo "pip install -r requirements-server.txt"
echo ""

echo "🔍 Test your installation:"
echo "python -c \"import pandas; print('✅ Pandas working')\" 2>/dev/null || echo '⚠️ Pandas not available (using basic CSV)'"
echo ""

echo "🚀 Start your application:"
echo "python app.py"
echo "# or for production:"
echo "gunicorn app:app"
