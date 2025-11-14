"""
Command-line interface for Taiga MCP Server.

Provides a rich CLI with options for:
- Authentication setup (login command)
- Transport mode (stdio/sse)
- Port configuration
- Logging levels and output
- Host binding
"""

import argparse
import sys
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the Taiga MCP server.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="pytaiga-mcp",
        description="Taiga MCP Bridge - Model Context Protocol server for Taiga",
        epilog="Examples:\n"
        "  %(prog)s login                    # Interactive login to create .env\n"
        "  %(prog)s                          # Start with stdio (default)\n"
        "  %(prog)s --transport sse          # Start SSE server on port 8000\n"
        "  %(prog)s --transport sse --port 5000  # Custom port\n"
        "  %(prog)s --log-level DEBUG        # Debug logging to console\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser(
        "login", help="Interactive login to generate .env file with authentication token"
    )
    login_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .env file without prompting",
    )

    # Transport options
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol: stdio (default, process-based) or sse (HTTP-based)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        metavar="PORT",
        help="Port for SSE transport (default: 8000). Only used with --transport sse",
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        metavar="HOST",
        help="Host to bind SSE server (default: 0.0.0.0). Only used with --transport sse",
    )

    # Logging options
    logging_group = parser.add_argument_group("logging options")

    logging_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    logging_group.add_argument(
        "--log-file",
        type=str,
        metavar="FILE",
        help="Log to file (supports rotation). If not specified, logs only to console",
    )

    logging_group.add_argument(
        "--log-max-bytes",
        type=int,
        default=10 * 1024 * 1024,  # 10MB
        metavar="BYTES",
        help="Maximum log file size before rotation (default: 10MB)",
    )

    logging_group.add_argument(
        "--log-backup-count",
        type=int,
        default=5,
        metavar="COUNT",
        help="Number of rotated log files to keep (default: 5)",
    )

    logging_group.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress console output (only log to file if --log-file specified)",
    )

    logging_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (equivalent to --log-level DEBUG)",
    )

    # Version
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments.

    Args:
        args: Parsed arguments

    Raises:
        SystemExit: If validation fails
    """
    # Validate port range
    if args.port < 1024 or args.port > 65535:
        print(f"Error: Port must be between 1024 and 65535 (got {args.port})", file=sys.stderr)
        sys.exit(1)

    # Check for conflicting options
    if args.quiet and args.verbose:
        print("Error: Cannot use --quiet and --verbose together", file=sys.stderr)
        sys.exit(1)

    # Warn if port/host specified without SSE
    if args.transport != "sse":
        if args.port != 8000:
            print(
                f"Warning: --port {args.port} ignored (only used with --transport sse)",
                file=sys.stderr,
            )
        if args.host != "0.0.0.0":
            print(
                f"Warning: --host {args.host} ignored (only used with --transport sse)",
                file=sys.stderr,
            )

    # Verbose overrides log level
    if args.verbose:
        args.log_level = "DEBUG"

    # Quiet requires log file
    if args.quiet and not args.log_file:
        print("Warning: --quiet without --log-file will suppress all output", file=sys.stderr)

    # Create log directory if needed
    if args.log_file:
        log_path = Path(args.log_file)
        if not log_path.parent.exists():
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"Error: Cannot create log directory: {e}", file=sys.stderr)
                sys.exit(1)


def print_startup_info(args: argparse.Namespace) -> None:
    """
    Print server startup information.

    Args:
        args: Parsed arguments
    """
    if args.quiet:
        return

    print("=" * 70)
    print("Taiga MCP Bridge")
    print("=" * 70)
    print(f"Transport:    {args.transport.upper()}")

    if args.transport == "sse":
        print(f"Address:      http://{args.host}:{args.port}")
        print("Endpoints:    /sse (events), /messages (POST)")
    else:
        print("Mode:         Process-based (stdin/stdout)")

    print(f"Log Level:    {args.log_level}")

    if args.log_file:
        print(f"Log File:     {args.log_file}")
        print(f"Max Size:     {args.log_max_bytes / 1024 / 1024:.1f} MB")
        print(f"Backup Count: {args.log_backup_count}")
    else:
        print("Log File:     None (console only)")

    print("=" * 70)
    print()

    if args.transport == "stdio":
        print("Server ready for stdio communication...")
        print("(Waiting for MCP client to connect)")
    else:
        print(f"Starting SSE server on {args.host}:{args.port}...")
        print("(Press Ctrl+C to stop)")

    print()


def parse_args(argv: list | None = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])

    Returns:
        Parsed arguments namespace
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Handle login command separately (no validation needed)
    if args.command == "login":
        return args

    validate_args(args)
    return args


def handle_login_command(args: argparse.Namespace) -> int:
    """
    Handle the login command.

    Args:
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    from pytaiga_mcp.auth_setup import interactive_login

    # Check if .env exists
    env_path = Path(".env")
    if env_path.exists() and not args.force:
        print(f"Warning: {env_path.absolute()} already exists!")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            print("Cancelled.")
            return 0

    try:
        interactive_login()
        return 0
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        return 130
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return 1
