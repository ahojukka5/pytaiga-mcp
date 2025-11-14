"""
Common utilities and session management for Taiga MCP server.
"""

import logging
import os

from mcp.server.fastmcp import FastMCP
from pytaigaclient import TaigaClient

from pytaiga_mcp.taiga_client import TaigaClientWrapper

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logging.getLogger("pytaigaclient").setLevel(logging.WARNING)

# --- Manual Session Management ---
# Store active sessions: session_id -> TaigaClientWrapper instance
active_sessions: dict[str, TaigaClientWrapper] = {}

# --- MCP Server Instance (Lazy Initialization) ---
_mcp_instance: FastMCP | None = None


def get_mcp() -> FastMCP:
    """
    Get or create the MCP server instance.

    This lazy initialization allows environment variables to be set
    before the FastMCP instance is created (by __main__.py or main()).
    """
    global _mcp_instance
    if _mcp_instance is None:
        # Read configuration from environment variables if set
        fastmcp_host = os.getenv("FASTMCP_HOST", "127.0.0.1")
        fastmcp_port = int(os.getenv("FASTMCP_PORT", "8000"))

        _mcp_instance = FastMCP(
            "Taiga Bridge (Session ID)",
            dependencies=["pytaigaclient"],
            host=fastmcp_host,
            port=fastmcp_port,
        )
    return _mcp_instance


# Provide module-level access via __getattr__ for backward compatibility
# This allows `from .common import mcp` to work, but delays creation until first use
def __getattr__(name: str):
    if name == "mcp":
        return get_mcp()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def get_authenticated_client(session_id: str) -> TaigaClientWrapper:
    """
    Retrieves the authenticated TaigaClientWrapper for a given session ID.
    Raises PermissionError if the session is invalid or not found.
    """
    client = active_sessions.get(session_id)
    if not client or not client.is_authenticated:
        logger.warning(f"Invalid or expired session ID provided: {session_id}")
        raise PermissionError(f"Invalid or expired session ID: '{session_id}'. Please login again.")
    logger.debug(f"Retrieved valid client for session ID: {session_id}")
    return client


def get_api_client(session_id: str) -> TaigaClient:
    """
    Retrieves the authenticated TaigaClient API instance for a given session ID.
    This helper ensures type safety by guaranteeing the API client is not None.
    Raises PermissionError if the session is invalid or not found.
    """
    wrapper = get_authenticated_client(session_id)
    if wrapper.api is None:
        # This should never happen due to is_authenticated check, but we guard against it
        logger.error(f"Authenticated client has no API instance for session {session_id[:8]}")
        raise PermissionError("Client is authenticated but API instance is unavailable.")
    return wrapper.api
