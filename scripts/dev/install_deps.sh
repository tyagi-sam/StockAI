#!/bin/bash

# Install Backend Dependencies Script
# This script installs the required Python packages for local testing

# Always run from the repo root so relative paths (backend/requirements.txt) resolve
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🔧 Installing StockAI Backend Dependencies..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: You're not in a virtual environment."
    echo "   It's recommended to create one first:"
    echo "   python -m venv env"
    echo "   source env/bin/activate  # On macOS/Linux"
    echo "   or"
    echo "   env\\Scripts\\activate  # On Windows"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if requirements.txt exists
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt not found!"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python packages..."
pip install -r backend/requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🔍 You can now run: python test_setup.py"
    echo "🚀 Or start the backend directly: cd backend && python -m uvicorn app.main:app --reload"
else
    echo ""
    echo "❌ Failed to install dependencies!"
    echo "🔍 Check the error messages above."
    exit 1
fi 