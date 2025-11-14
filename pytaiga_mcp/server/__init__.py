"""
Taiga MCP Server - Modular structure with domain-specific modules.

This package provides a clean, organized structure for the Taiga MCP server.
All functions are re-exported from this __init__.py for backward compatibility.

Modules:
- common: Session management and shared utilities
- auth: Authentication and session management
- projects: Project CRUD and member management
- user_stories: User story operations
- tasks: Task operations
- issues: Issue operations
- epics: Epic operations
- milestones: Milestone/sprint operations
- wiki: Wiki page operations
"""

# IMPORTANT: Set environment variables BEFORE any imports
# This allows CLI arguments to configure the FastMCP instance
import os
import sys

# Pre-parse command-line arguments to configure FastMCP
# This happens at package import time, before decorators are processed
if "--transport" in sys.argv:
    try:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "sse":
            # SSE transport - check for port and host
            if "--port" in sys.argv:
                port_idx = sys.argv.index("--port")
                if port_idx + 1 < len(sys.argv):
                    os.environ["FASTMCP_PORT"] = sys.argv[port_idx + 1]

            if "--host" in sys.argv:
                host_idx = sys.argv.index("--host")
                if host_idx + 1 < len(sys.argv):
                    os.environ["FASTMCP_HOST"] = sys.argv[host_idx + 1]
    except (ValueError, IndexError):
        pass  # Let argparse handle errors later

# NOW we can safely import everything
# The FastMCP instance will be created with the correct configuration

# Export auth functions
from .auth import (
    delete_cached_token,
    list_cached_tokens_tool,
    login,
    login_from_cache,
    login_with_token,
    logout,
    save_session_token,
    session_status,
)

# Export the FastMCP instance and utilities
# NOTE: mcp is NOT imported here to allow lazy initialization
# It's imported locally in main() after environment variables are set
from .common import active_sessions, get_api_client, get_authenticated_client

# Export epic functions
from .epics import (
    assign_epic_to_user,
    create_epic,
    delete_epic,
    get_epic,
    list_epics,
    unassign_epic_from_user,
    update_epic,
)

# Export issue functions
from .issues import (
    assign_issue_to_user,
    create_issue,
    delete_issue,
    get_issue,
    get_issue_priorities,
    get_issue_severities,
    get_issue_statuses,
    get_issue_types,
    list_issues,
    unassign_issue_from_user,
    update_issue,
)

# Export milestone functions
from .milestones import (
    create_milestone,
    delete_milestone,
    get_milestone,
    list_milestones,
    update_milestone,
)

# Export project functions
from .projects import (
    create_project,
    delete_project,
    get_project,
    get_project_by_slug,
    get_project_members,
    invite_project_user,
    list_all_projects,
    list_projects,
    update_project,
)

# Export task functions
from .tasks import (
    assign_task_to_user,
    create_task,
    delete_task,
    get_task,
    list_tasks,
    unassign_task_from_user,
    update_task,
)

# Export user story functions
from .user_stories import (
    assign_user_story_to_user,
    create_user_story,
    delete_user_story,
    get_user_story,
    get_user_story_statuses,
    list_user_stories,
    unassign_user_story_from_user,
    update_user_story,
)

# Export wiki functions
from .wiki import (
    create_wiki_page,
    get_wiki_page,
    list_wiki_pages,
)


def main():
    """
    Main entry point for the Taiga MCP server (server-only).

    Note: This is called by pytaiga_mcp.main after login command handling.
    For CLI usage, use the 'pytaiga-mcp' command instead of calling this directly.

    This function can be called via:
    - Python module: python -m pytaiga_mcp.server (for development)

    Supports comprehensive options:
    - Transport modes (stdio/sse)
    - Port and host configuration
    - Logging levels and file output
    - Debug and quiet modes

    Examples:
        pytaiga-mcp                          # Default stdio mode
        pytaiga-mcp --transport sse          # SSE on port 8000
        pytaiga-mcp --port 5000              # SSE on custom port
        pytaiga-mcp --log-level DEBUG        # Debug logging
        pytaiga-mcp --log-file server.log    # Log to file
        pytaiga-mcp -v --log-file debug.log  # Verbose file logging
    """
    import os
    import sys

    from pytaiga_mcp.cli import parse_args, print_startup_info
    from pytaiga_mcp.logging_config import get_logger, setup_logging

    # Parse command-line arguments
    args = parse_args()

    # Set FastMCP environment variables BEFORE importing server modules
    # FastMCP's Settings uses pydantic BaseSettings which reads env vars at instantiation
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


__all__ = [
    # Common - mcp is accessed via common.get_mcp() for lazy init
    "active_sessions",
    "get_authenticated_client",
    "get_api_client",
    # Main entry point
    "main",
    # Auth
    "login",
    "login_with_token",
    "logout",
    "session_status",
    "save_session_token",
    "login_from_cache",
    "delete_cached_token",
    "list_cached_tokens_tool",
    # Projects
    "list_projects",
    "list_all_projects",
    "get_project",
    "get_project_by_slug",
    "create_project",
    "update_project",
    "delete_project",
    "get_project_members",
    "invite_project_user",
    # User Stories
    "list_user_stories",
    "create_user_story",
    "get_user_story",
    "update_user_story",
    "delete_user_story",
    "assign_user_story_to_user",
    "unassign_user_story_from_user",
    "get_user_story_statuses",
    # Tasks
    "list_tasks",
    "create_task",
    "get_task",
    "update_task",
    "delete_task",
    "assign_task_to_user",
    "unassign_task_from_user",
    # Issues
    "list_issues",
    "create_issue",
    "get_issue",
    "update_issue",
    "delete_issue",
    "assign_issue_to_user",
    "unassign_issue_from_user",
    "get_issue_statuses",
    "get_issue_priorities",
    "get_issue_severities",
    "get_issue_types",
    # Epics
    "list_epics",
    "create_epic",
    "get_epic",
    "update_epic",
    "delete_epic",
    "assign_epic_to_user",
    "unassign_epic_from_user",
    # Milestones
    "list_milestones",
    "create_milestone",
    "get_milestone",
    "update_milestone",
    "delete_milestone",
    # Wiki
    "list_wiki_pages",
    "get_wiki_page",
    "create_wiki_page",
]
