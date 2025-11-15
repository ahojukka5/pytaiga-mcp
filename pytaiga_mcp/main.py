"""
Main entry point for pytaiga-mcp command-line tool.

This module handles the initial command routing before importing
the server package, which has side effects (FastMCP initialization).
"""

import sys


def main():
    """
    Main entry point that routes to either login/logout or server.

    This function MUST be called before importing pytaiga_mcp.server
    because that package initializes FastMCP at import time.
    """
    from pytaiga_mcp.cli import handle_login_command, handle_logout_command, parse_args

    # Parse CLI arguments FIRST to check for login/logout command
    args = parse_args()

    # Handle login command - exit early before importing server
    if args.command == "login":
        sys.exit(handle_login_command(args))

    # Handle logout command - exit early before importing server
    if args.command == "logout":
        sys.exit(handle_logout_command(args))

    # Not login/logout command - import and run the server
    from pytaiga_mcp.server import main as server_main

    server_main()


if __name__ == "__main__":
    main()
