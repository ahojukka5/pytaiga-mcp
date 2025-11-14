#!/bin/bash

# Installation script for Taiga MCP Bridge
# Supports Poetry package manager

set -e

echo "========================================="
echo "Taiga MCP Bridge - Installation"
echo "========================================="
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed."
    echo "Please install Poetry first: https://python-poetry.org/docs/#installation"
    echo ""
    echo "Quick install:"
    echo "  curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "✓ Poetry found: $(poetry --version)"
echo ""

# Check if we should install dev dependencies
if [ "$1" = "--dev" ]; then
    echo "Installing with development dependencies..."
    poetry install
else
    echo "Installing production dependencies only..."
    poetry install --no-dev
fi

echo ""
echo "========================================="
echo "✓ Installation complete!"
echo "========================================="
echo ""
echo "To run the server:"
echo "  poetry run python -m pytaiga_mcp.server"
echo ""
echo "Or with options:"
echo "  poetry run python -m pytaiga_mcp.server --help"
echo ""
echo "Using helper scripts:"
echo "  ./scripts/run.sh              # stdio mode"
echo "  ./scripts/run.sh --sse        # SSE mode"
echo ""
