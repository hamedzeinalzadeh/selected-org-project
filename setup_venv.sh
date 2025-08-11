#!/bin/bash

# Virtual Environment Setup Script for Travel Itinerary Generator
# This script sets up a Python virtual environment for local development

set -e

echo "🐍 Setting up Python Virtual Environment for Travel Itinerary Generator"
echo "========================================================================"

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.11 or higher from: https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python $PYTHON_VERSION is installed, but Python 3.8+ is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Virtual environment setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate the virtual environment:"
echo "      source venv/bin/activate"
echo ""
echo "   2. Copy environment variables:"
echo "      cp env.local .env"
echo "      # Edit .env file with your OpenAI API key"
echo ""
echo "   3. Start MongoDB (choose one option):"
echo "      # Option A: Using Docker"
echo "      docker run -d -p 27017:27017 --name mongodb mongo:7.0"
echo ""
echo "      # Option B: Install MongoDB locally"
echo "      # Follow instructions at: https://docs.mongodb.com/manual/installation/"
echo ""
echo "   4. Run the application:"
echo "      python main.py"
echo ""
echo "   5. Run the Streamlit interface (in another terminal):"
echo "      streamlit run streamlit_app.py"
echo ""
echo "🌐 Application URLs:"
echo "   FastAPI API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Streamlit UI: http://localhost:8501"
echo ""
echo "🧪 Test the setup:"
echo "   python test_setup.py"

# Deactivate virtual environment
deactivate

echo ""
echo "🎉 Setup completed! Don't forget to activate the virtual environment before running the application." 