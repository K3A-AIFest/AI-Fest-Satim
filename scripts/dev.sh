#!/bin/bash
# Development helper scripts for uv

case "$1" in
    "install")
        echo "📦 Installing dependencies with uv..."
        uv sync
        ;;
    "run")
        echo "🚀 Running RAG system..."
        uv run python src/main.py
        ;;
    "shell")
        echo "🐚 Activating virtual environment..."
        echo "Run: source .venv/bin/activate"
        ;;
    "test")
        echo "🧪 Running tests..."
        uv run pytest tests/
        ;;
    "format")
        echo "🎨 Formatting code..."
        uv run black src/
        uv run ruff check src/ --fix
        ;;
    "stats")
        echo "📊 Project statistics:"
        echo "Python version: $(uv run python --version)"
        echo "Installed packages:"
        uv tree
        ;;
    *)
        echo "🛠️  Available commands:"
        echo "  ./scripts/dev.sh install  - Install dependencies"
        echo "  ./scripts/dev.sh run      - Run the RAG system"
        echo "  ./scripts/dev.sh shell    - Activate virtual environment"
        echo "  ./scripts/dev.sh test     - Run tests"
        echo "  ./scripts/dev.sh format   - Format code"
        echo "  ./scripts/dev.sh stats    - Show project stats"
        ;;
esac