#!/bin/bash
# Start server without auto-reload to avoid false reloads

cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

