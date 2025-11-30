#!/bin/bash
# Kill existing server and start new one without reload

echo "🔍 Checking for existing server on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

echo "🚀 Starting server..."
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

