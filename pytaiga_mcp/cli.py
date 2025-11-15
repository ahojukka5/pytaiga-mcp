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
import os
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
        "  %(prog)s login                        # Check login status or show help\n"
        "  %(prog)s login --interactive          # Interactive username/password login\n"
        "  %(prog)s login --github               # GitHub OAuth login\n"
        "  %(prog)s logout                       # Logout and clear cache\n"
        "  %(prog)s login --list-cache           # List cached tokens\n"
        "  %(prog)s                              # Start with stdio (default)\n"
        "  %(prog)s --transport sse              # Start SSE server on port 8000\n"
        "  %(prog)s --transport sse --port 5000  # Custom port\n"
        "  %(prog)s --log-level DEBUG            # Debug logging to console\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser(
        "login", help="Authenticate with Taiga (uses cache in ~/.cache/pytaiga-mcp/)"
    )
    login_parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-authentication even if already logged in",
    )
    login_parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Prompt for credentials interactively (username/password)",
    )
    login_parser.add_argument(
        "--github",
        action="store_true",
        help="Use GitHub OAuth authentication",
    )
    login_parser.add_argument(
        "--list-cache",
        action="store_true",
        help="List all cached authentication tokens",
    )

    # Logout command
    subparsers.add_parser("logout", help="Logout and clear cached authentication")

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

    # Handle login and logout commands separately (no validation needed)
    if args.command in ("login", "logout"):
        return args

    validate_args(args)
    return args


def handle_logout_command(args: argparse.Namespace) -> int:
    """
    Handle the logout command.

    Args:
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    import os

    from dotenv import load_dotenv

    from pytaiga_mcp.auth_cache import delete_token

    load_dotenv()

    # Determine host
    host = os.environ.get("TAIGA_HOST") or os.environ.get("TAIGA_API_URL")
    if host:
        # Normalize to base URL without /api/v1
        host = host.rstrip("/").replace("/api/v1", "")
    else:
        host = "https://api.taiga.io"

    if delete_token(host):
        print(f"✓ Logged out from {host}")
        print("  Cache cleared.")
        return 0
    else:
        print(f"Not logged in to {host}")
        return 1


def handle_login_command(args: argparse.Namespace) -> int:
    """
    Handle the login command.

    Flow:
    1. Check cache - if logged in and valid, report and exit
    2. Try credentials from .env (token or username/password)
    3. If --interactive, prompt for credentials
    4. If nothing available, show help message

    Args:
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """

    import httpx
    from dotenv import load_dotenv

    from pytaiga_mcp.auth_cache import (
        list_cached_hosts,
        load_token,
        save_token,
    )

    # Load .env file
    load_dotenv()

    # Determine host
    host = os.environ.get("TAIGA_HOST") or os.environ.get("TAIGA_API_URL")
    if host:
        # Normalize to base URL without /api/v1
        host = host.rstrip("/").replace("/api/v1", "")
    else:
        host = "https://api.taiga.io"

    # Handle list cached hosts
    if hasattr(args, "list_cache") and args.list_cache:
        hosts = list_cached_hosts()
        if hosts:
            print("Cached authentication tokens:")
            for h in hosts:
                print(f"  - {h}")
        else:
            print("No cached tokens found.")
        return 0

    try:
        # Step 1: Check if already logged in via cache
        cached = load_token(host)
        if cached and not args.force:
            # Verify token is still valid
            token = cached["token"]
            try:
                response = httpx.get(
                    f"{host}/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✓ Already logged in to {host}")
                    print(f"  User: {user_data.get('username', 'unknown')}")
                    print(f"  Full name: {user_data.get('full_name', 'N/A')}")
                    print()
                    print("To force re-authentication:")
                    print("  poetry run pytaiga-mcp login --force")
                    print()
                    print("To logout:")
                    print("  poetry run pytaiga-mcp logout")
                    return 0
            except Exception:
                # Token invalid, will re-authenticate
                pass

        # Step 2: Try credentials from .env
        token_from_env = os.environ.get("TAIGA_AUTH_TOKEN")
        username = os.environ.get("TAIGA_USERNAME")
        password = os.environ.get("TAIGA_PASSWORD")

        authenticated = False
        auth_token = None
        user_id = None

        if token_from_env and not (hasattr(args, "interactive") and args.interactive):
            # Try token from .env
            print(f"Attempting login to {host} with token from .env...")
            try:
                response = httpx.get(
                    f"{host}/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token_from_env}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    user_data = response.json()
                    auth_token = token_from_env
                    user_id = user_data.get("id")
                    authenticated = True
                    print(f"✓ Authenticated as {user_data.get('username')}")
            except Exception as e:
                print(f"Token from .env failed: {e}")

        if (
            not authenticated
            and username
            and password
            and not (hasattr(args, "interactive") and args.interactive)
        ):
            # Try username/password from .env
            print(f"Attempting login to {host} with credentials from .env...")
            try:
                response = httpx.post(
                    f"{host}/api/v1/auth",
                    json={"username": username, "password": password, "type": "normal"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    auth_token = data["auth_token"]
                    user_id = data.get("id")
                    authenticated = True
                    print(f"✓ Authenticated as {username}")
            except Exception as e:
                print(f"Login with credentials from .env failed: {e}")

        # Step 3: If --interactive or --github, prompt for credentials
        if not authenticated and (hasattr(args, "interactive") and args.interactive):
            from pytaiga_mcp.auth_setup import interactive_login_to_cache

            result = interactive_login_to_cache(host)
            if result:
                auth_token, user_id = result
                authenticated = True

        if not authenticated and (hasattr(args, "github") and args.github):
            from pytaiga_mcp.github_auth import github_oauth_to_cache

            result = github_oauth_to_cache(host)
            if result:
                auth_token, user_id = result
                authenticated = True

        # Step 4: If still not authenticated and not interactive, show help
        if (
            not authenticated
            and not (hasattr(args, "interactive") and args.interactive)
            and not (hasattr(args, "github") and args.github)
        ):
            print(f"No valid credentials found for {host}")
            print()
            print("To authenticate, you have several options:")
            print()
            print("1. Add credentials to .env file:")
            print("   TAIGA_HOST=https://api.taiga.io")
            print("   TAIGA_AUTH_TOKEN=your_token_here")
            print()
            print("2. Use interactive authentication:")
            print("   poetry run pytaiga-mcp login --interactive")
            print()
            print("3. Use GitHub OAuth:")
            print("   poetry run pytaiga-mcp login --github")
            print()
            return 1

        # Save to cache if authenticated
        if authenticated and auth_token:
            save_token(host, auth_token, user_id)
            print()
            print("✓ Authentication cached to ~/.cache/pytaiga-mcp/")
            print("✓ You can now use pytaiga-mcp without re-authenticating")
            return 0

        print("Authentication failed")
        return 1

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        return 130
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
