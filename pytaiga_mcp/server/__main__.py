"""
Entry point for running pytaiga_mcp.server as a module.

Usage:
    python -m pytaiga_mcp.server [OPTIONS]

Examples:
    python -m pytaiga_mcp.server
    python -m pytaiga_mcp.server --help
    python -m pytaiga_mcp.server --transport sse --port 5000
    python -m pytaiga_mcp.server --log-level DEBUG --log-file debug.log
"""

# Environment variables are set in __init__.py before package imports
# This ensures FastMCP is configured correctly based on CLI arguments

if __name__ == "__main__":
    from pytaiga_mcp.server import main

    main()
