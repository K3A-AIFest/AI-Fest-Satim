#!/bin/bash

echo "🚀 Setting up Regulatory RAG System with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create project structure
echo "📁 Creating project structure..."
mkdir -p src
mkdir -p policies
mkdir -p standards  
mkdir -p faiss_store
mkdir -p tests

# Create __init__.py files if they don't exist
if [ ! -f "src/__init__.py" ]; then
    echo "📝 Creating src/__init__.py..."
    cat > src/__init__.py << 'EOF'
"""
Regulatory Document RAG System

A specialized RAG system for processing regulatory documents.
"""

__version__ = "0.1.0"
__author__ = "Chamiln17"

# Import main classes when available
try:
    from .faiss_store import FAISSVectorStore
    from .embedding_generator import EmbeddingGenerator
    
    __all__ = [
        "FAISSVectorStore",
        "EmbeddingGenerator",
    ]
except ImportError:
    # During setup, modules might not be available yet
    __all__ = []
EOF
fi

touch tests/__init__.py

# Create .env template
echo "📝 Creating .env template..."
cat > .env.template << 'EOF'
# API Keys (optional - only needed if using OpenAI or Cohere)
OPENAI_API_KEY=your_openai_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# Development settings
PYTHONPATH=${PYTHONPATH}:./src
LOG_LEVEL=INFO
EOF

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "📄 Created .env file from template"
fi

echo "✅ Project structure created!"
echo ""
echo "🎯 Next steps:"
echo "1. Install dependencies: uv sync"
echo "2. Add your PDF files to the policies/ and standards/ folders"
echo "3. Run the system: uv run python src/main.py"
echo ""
echo "📊 Current project structure:"
if command -v tree &> /dev/null; then
    tree -L 2 -a
else
    find . -type d -name ".git" -prune -o -type d -print | head -20
fi