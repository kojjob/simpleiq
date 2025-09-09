#!/bin/bash

# SimpleIQ Backend Setup Script using UV

echo "🚀 Setting up SimpleIQ Backend with UV..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "✅ UV is installed: $(uv --version)"

# Create virtual environment
echo "🔧 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
uv pip install -e ".[dev]"

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual configuration values"
fi

echo "✅ Backend setup complete!"
echo ""
echo "To start developing:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Start the development server: uvicorn app.main:app --reload"
echo "3. View API docs at: http://localhost:8000/api/v1/docs"