#!/bin/bash

# Run the Taiga MCP server
# Usage: ./scripts/run.sh [--sse]

if [ "$1" == "--sse" ]; then
    poetry run python -m pytaiga_mcp.server --transport sse
else
    poetry run python -m pytaiga_mcp.server
fi
