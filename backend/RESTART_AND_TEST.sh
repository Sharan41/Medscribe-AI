#!/bin/bash
# Complete server restart script for PDF formatting fix

echo "🛑 Stopping server..."
pkill -9 -f "uvicorn" 2>/dev/null || true
sleep 2

echo "🧹 Clearing Python cache..."
cd "$(dirname "$0")"
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Cache cleared"
echo ""
echo "🚀 Starting server..."
echo "   After server starts, test PDF generation"
echo "   Check logs for: 'SOAP markdown BEFORE/AFTER conversion'"
echo ""

./START_SERVER_WITH_PDF.sh
