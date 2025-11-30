#!/bin/bash
# Start MedScribe AI Backend Server with PDF Support

cd "$(dirname "$0")"
source venv/bin/activate

# Set library paths for WeasyPrint/PDF generation
# Add Homebrew library paths
export DYLD_LIBRARY_PATH="/usr/local/lib:/usr/local/opt/glib/lib:/usr/local/opt/pango/lib:/usr/local/opt/cairo/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/usr/local/opt/glib/lib/pkgconfig:/usr/local/opt/pango/lib/pkgconfig:/usr/local/opt/cairo/lib/pkgconfig:$PKG_CONFIG_PATH"
export GI_TYPELIB_PATH="/usr/local/lib/girepository-1.0:$GI_TYPELIB_PATH"

echo "🚀 Starting MedScribe AI Backend Server..."
echo "📍 URL: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "📄 PDF: Enabled (with library paths)"
echo "🔧 Library paths set for WeasyPrint"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000

