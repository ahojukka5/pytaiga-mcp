"""
Taiga MCP Server - Main entry point.

This is the refactored main server file that imports all functionality
from the modular server/ package. All tools and functions are organized
into domain-specific modules:

- server/common.py: Session management and shared utilities
- server/auth.py: Authentication and session management
- server/projects.py: Project CRUD and member management
- server/user_stories.py: User story operations
- server/tasks.py: Task operations
- server/issues.py: Issue operations
- server/epics.py: Epic operations
- server/milestones.py: Milestone/sprint operations
- server/wiki.py: Wiki page operations

All functions are imported and the MCP server instance is ready to run.
"""


def main():
    """
    Main entry point for the Taiga MCP server.

    This function can be called via:
    - Command line: pytaiga-mcp
    - Python module: python -m pytaiga_mcp.server
    - Direct execution: python server.py
    """
    import os
    import sys

    from pytaiga_mcp.cli import handle_login_command, parse_args, print_startup_info
    from pytaiga_mcp.logging_config import get_logger, setup_logging

    # Parse CLI arguments FIRST to check for login command
    args = parse_args()

    # Handle login command - exit early before initializing the server
    if args.command == "login":
        sys.exit(handle_login_command(args))

    # Set FastMCP environment variables BEFORE importing server modules
    if args.transport == "sse":
        os.environ["FASTMCP_HOST"] = args.host
        os.environ["FASTMCP_PORT"] = str(args.port)

    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file=args.log_file,
        log_to_console=not args.quiet,
        max_bytes=args.log_max_bytes,
        backup_count=args.log_backup_count,
    )

    # Get logger
    logger = get_logger(__name__)

    # Print startup info
    print_startup_info(args)

    # Log startup
    logger.info("=" * 50)
    logger.info("Taiga MCP Bridge starting")
    logger.info(f"Transport: {args.transport}")
    if args.transport == "sse":
        logger.info(f"Server address: http://{args.host}:{args.port}")
    logger.info(f"Log level: {args.log_level}")
    logger.info("=" * 50)

    # Run the server with appropriate transport
    try:
        # Import mcp here after env vars are set
        from pytaiga_mcp.server.common import mcp

        if args.transport == "sse":
            logger.info(f"Starting SSE server on {args.host}:{args.port}")
            mcp.run(transport="sse")
        else:
            # stdio transport (default)
            logger.info("Starting stdio transport")
            logger.debug("Listening on stdin/stdout")
            mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
