#!/bin/bash
# MCP Inspector Script for Taiga MCP Bridge
#
# Usage examples:
# stdio mode: 
#   npx -y @modelcontextprotocol/inspector poetry run python -m pytaiga_mcp.server
# sse mode:
#   npx -y @modelcontextprotocol/inspector poetry run python -m pytaiga_mcp.server --transport sse --port 5001


# Help/usage function
show_help() {
    echo "Usage: ./scripts/inspect.sh [OPTIONS]"
    echo ""
    echo "Run the Taiga MCP server with the MCP Inspector for debugging."
    echo ""
    echo "Options:"
    echo "  --transport <stdio|sse>  Transport protocol (default: stdio)"
    echo "  --port <port>            SSE port (default: 8000)"
    echo "  --log-level <level>      Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)"
    echo "  --log-file <filename>    Log file path (default: server.log)"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/inspect.sh"
    echo "  ./scripts/inspect.sh --transport sse --port 5001"
    echo "  ./scripts/inspect.sh --log-level DEBUG --log-file debug.log"
}

# Default values
TRANSPORT="stdio"
PORT=8000
LOG_LEVEL="INFO"
LOG_FILE="server.log"

# Get directory where script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"


# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --transport)
            TRANSPORT="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate transport
if [[ "$TRANSPORT" != "stdio" && "$TRANSPORT" != "sse" ]]; then
    echo "Error: Invalid transport '$TRANSPORT'. Must be 'stdio' or 'sse'."
    exit 1
fi

# Validate log level
case "$LOG_LEVEL" in
    DEBUG|INFO|WARNING|ERROR|CRITICAL) ;;
    *)
        echo "Error: Invalid log level '$LOG_LEVEL'."
        echo "Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        exit 1
        ;;
esac

# Validate port
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid port '$PORT'. Must be a number."
    exit 1
fi

if [[ "$PORT" -lt 1024 || "$PORT" -gt 65535 ]]; then
    echo "Error: Port must be between 1024 and 65535, got: $PORT"
    exit 1
fi

# Build command
cd "$PROJECT_ROOT" || exit 1

echo "========================================="
echo "Starting MCP Inspector"
echo "========================================="
echo "Transport:  $TRANSPORT"
echo "Port:       $PORT (used only for SSE)"
echo "Log Level:  $LOG_LEVEL"
echo "Log File:   $LOG_FILE"
echo "Directory:  $PROJECT_ROOT"
echo "========================================="
echo ""

# Run with MCP Inspector
if [[ "$TRANSPORT" == "stdio" ]]; then
    echo "Running in stdio mode..."
    npx -y @modelcontextprotocol/inspector \
        poetry --directory "$PROJECT_ROOT" run \
        python -m pytaiga_mcp.server \
        --log-level "$LOG_LEVEL" \
        --log-file "$LOG_FILE"
elif [[ "$TRANSPORT" == "sse" ]]; then
    echo "Running in SSE mode on port $PORT..."
    npx -y @modelcontextprotocol/inspector \
        poetry --directory "$PROJECT_ROOT" run \
        python -m pytaiga_mcp.server \
        --transport sse \
        --port "$PORT" \
        --log-level "$LOG_LEVEL" \
        --log-file "$LOG_FILE"
fi
