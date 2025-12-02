#!/bin/bash
# Simple script to run EkaCare dataset integration

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Check if .env file exists and source it
if [ -f "backend/.env" ]; then
    echo "📋 Loading environment from backend/.env"
    export $(grep -v '^#' backend/.env | xargs)
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set"
    echo "💡 Set it in backend/.env or export GEMINI_API_KEY=your_key"
    exit 1
fi

# Check if datasets is installed
if ! python3 -c "import datasets" 2>/dev/null; then
    echo "📦 Installing datasets library..."
    pip3 install datasets huggingface_hub --quiet
fi

# Run the script
echo "🚀 Running EkaCare dataset integration..."
python3 backend/scripts/integrate_eka_dataset.py

