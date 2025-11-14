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

# Import all tools and the MCP instance from the server package
from pytaiga_mcp.server import *  # noqa: F401, F403


def main():
    """
    Main entry point for the Taiga MCP server.

    This function can be called via:
    - Command line: pytaiga-mcp
    - Python module: python -m pytaiga_mcp.server
    - Direct execution: python server.py
    """
    from pytaiga_mcp.cli import handle_login_command, parse_args

    # Parse CLI arguments
    args = parse_args()

    # Handle login command
    if args.command == "login":
        import sys

        sys.exit(handle_login_command(args))

    # Run the server
    from pytaiga_mcp.server import mcp

    mcp.run()


if __name__ == "__main__":
    main()
