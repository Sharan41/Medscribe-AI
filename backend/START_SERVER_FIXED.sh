#!/bin/bash
# Fixed Server Start Script - Always uses venv

cd "$(dirname "$0")"

echo "🔍 Checking virtual environment..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3.11 -m venv venv
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Activate virtual environment
source venv/bin/activate

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_PATH=$(which python)

echo "✅ Using Python: $PYTHON_VERSION"
echo "📍 Python path: $PYTHON_PATH"

# Verify it's the venv Python (not system)
if [[ ! "$PYTHON_PATH" == *"backend/venv"* ]]; then
    echo "⚠️  WARNING: Not using venv Python!"
    echo "Please activate venv manually: source venv/bin/activate"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
python -c "import supabase; import fastapi; import groq; print('✅ All dependencies available')" || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

# Kill any existing server on port 8000
echo "🧹 Cleaning up port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1

# Start server
echo ""
echo "🚀 Starting MedScribe AI Backend..."
echo "📍 Server: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

