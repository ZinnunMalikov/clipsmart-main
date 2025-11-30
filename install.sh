#!/bin/bash

# ClipSmart Installation Script
# This script installs ClipSmart and its dependencies

set -e

echo "Installing ClipSmart..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3.8+ is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Python $PYTHON_VERSION detected"
else
    echo "Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Create virtual environment (optional but recommended)
read -p "Create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv clipsmart-env
    source clipsmart-env/bin/activate
    echo "Virtual environment activated"
    echo "To activate later, run: source clipsmart-env/bin/activate"
fi

# Install ClipSmart
echo "Installing ClipSmart package..."
pip3 install -e .

echo ""
echo "ClipSmart installed successfully!"
echo ""
echo "Next steps:"
echo "1. Set your API keys in environment variables:"
echo "   export GENAI_API_KEY='your-gemini-api-key'"
echo "   export AWS_ACCESS_KEY_ID='your-aws-key'"
echo "   export AWS_SECRET_ACCESS_KEY='your-aws-secret'"
echo ""
echo "2. Start the server:"
echo "   uvicorn backend.processing.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "3. Access the API at: http://localhost:8000"
echo ""
echo "For more information, see the README.md file"