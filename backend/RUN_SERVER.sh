#!/bin/bash
# Start MedScribe AI Backend Server with PDF Support

# Navigate to the correct backend directory
cd "/Users/saisharan.v/Desktop/new project/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Error: venv directory not found!"
    echo "📍 Current directory: $(pwd)"
    echo "Please make sure you're in the correct backend directory."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set library paths for WeasyPrint/PDF generation
export DYLD_LIBRARY_PATH="/usr/local/lib:/usr/local/opt/glib/lib:/usr/local/opt/pango/lib:/usr/local/opt/cairo/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/usr/local/opt/glib/lib/pkgconfig:/usr/local/opt/pango/lib/pkgconfig:/usr/local/opt/cairo/lib/pkgconfig:$PKG_CONFIG_PATH"
export GI_TYPELIB_PATH="/usr/local/lib/girepository-1.0:$GI_TYPELIB_PATH"

echo "🚀 Starting MedScribe AI Backend Server..."
echo "📍 URL: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "📄 PDF: Enabled (with library paths)"
echo "🔧 Library paths set for WeasyPrint"
echo "📁 Working directory: $(pwd)"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000

