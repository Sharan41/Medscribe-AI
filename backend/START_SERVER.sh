#!/bin/bash
# Start MedScribe AI Backend Server

cd "$(dirname "$0")"
source venv/bin/activate

echo "🚀 Starting MedScribe AI Backend Server..."
echo "📍 URL: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000
