"""
Authentication and session management tools for Taiga MCP server.
"""

import logging
import uuid
from typing import Any

from pytaigaclient.exceptions import TaigaException

from pytaiga_mcp.taiga_client import TaigaClientWrapper

from .common import active_sessions, mcp
from .metrics import get_server_stats
from .token_storage import delete_token, get_token_file, list_cached_tokens, load_token, save_token

logger = logging.getLogger(__name__)


@mcp.tool(
    "login",
    description="Logs into a Taiga instance using username/password and returns a session_id for subsequent authenticated calls.",
)
def login(host: str, username: str, password: str) -> dict[str, str]:
    """
    Handles Taiga login and creates a session.

    Args:
        host: The URL of the Taiga instance (e.g., 'https://tree.taiga.io').
        username: The Taiga username.
        password: The Taiga password.

    Returns:
        A dictionary containing the session_id upon successful login.
        Example: {"session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
    """
    logger.info(f"Executing login tool for user '{username}' on host '{host}'")

    try:
        wrapper = TaigaClientWrapper(host=host)
        login_successful = wrapper.login(username=username, password=password)

        if login_successful:
            session_id = str(uuid.uuid4())
            active_sessions[session_id] = wrapper
            logger.info(f"Login successful for '{username}'. Session ID: {session_id[:8]}...")
            return {"session_id": session_id}
        else:
            logger.error(f"Login failed for '{username}': Authentication unsuccessful.")
            raise ValueError("Login failed: Invalid credentials or authentication error.")

    except (ValueError, TaigaException) as e:
        logger.error(f"Login failed for '{username}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during login for '{username}': {e}", exc_info=True)
        raise RuntimeError(f"An unexpected server error occurred during login: {e}")


@mcp.tool(
    "login_with_token",
    description="Logs into a Taiga instance using an authentication token (more secure than password). Returns a session_id for subsequent authenticated calls.",
)
def login_with_token(
    host: str, auth_token: str, token_type: str = "Bearer", user_id: int | None = None
) -> dict[str, str]:
    """
    Handles Taiga login using an existing authentication token.
    This is more secure than storing passwords.

    Args:
        host: The URL of the Taiga instance (e.g., 'https://api.taiga.io').
        auth_token: The authentication token (Bearer or Application token).
        token_type: Type of token - "Bearer" (default) or "Application".
        user_id: Optional user ID if known. If not provided, will fetch from /users/me.

    Returns:
        A dictionary containing the session_id upon successful authentication.
        Example: {"session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}

    How to get a token:
        1. Login with username/password first (using the 'login' tool)
        2. The token is returned in the response and stored in the session
        3. You can use that token for future authentication
        OR
        1. Create an Application token in Taiga web interface (User Settings > Applications)
        2. Use that token with token_type="Application"
    """
    logger.info(f"Executing login_with_token tool on host '{host}'")

    try:
        wrapper = TaigaClientWrapper(host=host)
        login_successful = wrapper.login_with_token(
            auth_token=auth_token, token_type=token_type, user_id=user_id
        )

        if login_successful:
            session_id = str(uuid.uuid4())
            active_sessions[session_id] = wrapper
            logger.info(f"Token authentication successful. Session ID: {session_id[:8]}...")
            return {"session_id": session_id}
        else:
            logger.error("Token authentication unsuccessful.")
            raise ValueError("Token authentication failed.")

    except (ValueError, TaigaException) as e:
        logger.error(f"Token authentication failed: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during token authentication: {e}", exc_info=True)
        raise RuntimeError(f"An unexpected server error occurred during token authentication: {e}")


@mcp.tool("logout", description="Invalidates the current session_id.")
def logout(session_id: str) -> dict[str, Any]:
    """Logs out the current session, invalidating the session_id."""
    logger.info(f"Executing logout for session {session_id[:8]}...")
    client_wrapper = active_sessions.pop(session_id, None)
    if client_wrapper:
        logger.info(f"Session {session_id[:8]} logged out successfully.")
        return {"status": "logged_out", "session_id": session_id}
    else:
        logger.warning(f"Logout attempt for non-existent session {session_id[:8]}.")
        return {"status": "session_not_found", "session_id": session_id}


@mcp.tool(
    "session_status",
    description="Checks if the provided session_id is currently active and valid.",
)
def session_status(session_id: str) -> dict[str, Any]:
    """Checks the validity of the current session_id."""
    logger.debug(f"Executing session_status check for session {session_id[:8]}...")
    client_wrapper = active_sessions.get(session_id)
    if client_wrapper and client_wrapper.is_authenticated:
        return {
            "status": "active",
            "session_id": session_id,
            "host": client_wrapper.host,
            "authenticated": True,
        }
    elif client_wrapper:
        return {
            "status": "inactive",
            "session_id": session_id,
            "authenticated": False,
        }
    else:
        return {
            "status": "not_found",
            "session_id": session_id,
            "authenticated": False,
        }


@mcp.tool(
    "save_session_token",
    description="Extracts and securely saves the authentication token from an active session to cache. This allows re-authentication without storing passwords.",
)
def save_session_token(session_id: str) -> dict[str, Any]:
    """
    Extracts the authentication token from an active session and saves it securely.

    This is the recommended workflow:
    1. Login once with username/password using 'login' tool
    2. Use this tool to save the token to secure cache
    3. Delete password from any config files
    4. Use 'login_from_cache' or 'login_with_token' for future authentications

    Args:
        session_id: The session ID from which to extract the token

    Returns:
        Status information about the save operation
    """
    logger.info(f"Executing save_session_token for session {session_id[:8]}...")

    client_wrapper = active_sessions.get(session_id)
    if not client_wrapper or not client_wrapper.is_authenticated:
        logger.error(f"Invalid or inactive session {session_id[:8]}")
        return {
            "status": "error",
            "message": "Invalid or inactive session. Please login first.",
        }

    if not client_wrapper.api or not client_wrapper.api.auth_token:
        logger.error(f"No auth token found in session {session_id[:8]}")
        return {
            "status": "error",
            "message": "No authentication token found in session.",
        }

    # Extract token info
    host = client_wrapper.host
    auth_token = client_wrapper.api.auth_token
    # Determine token type from the token format or default to Bearer
    token_type = "Bearer"  # pytaigaclient uses Bearer tokens
    user_id = client_wrapper.user_id

    # Save to cache
    success = save_token(host, auth_token, token_type, user_id)

    if success:
        logger.info(f"Token saved successfully for {host}")
        return {
            "status": "success",
            "message": f"Token saved securely to cache for {host}",
            "host": host,
            "token_type": token_type,
            "user_id": user_id,
            "cache_location": (
                str(get_token_file(host)) if "get_token_file" in dir() else "~/.cache/taiga-mcp/"
            ),
        }
    else:
        logger.error(f"Failed to save token for {host}")
        return {
            "status": "error",
            "message": "Failed to save token to cache",
        }


@mcp.tool(
    "login_from_cache",
    description="Authenticates using a previously saved token from cache. Preferred over password authentication.",
)
def login_from_cache(host: str, user_id: int | None = None) -> dict[str, str]:
    """
    Login using a token that was previously saved to cache.

    This is the RECOMMENDED authentication method:
    - More secure than storing passwords
    - Tokens can be revoked without changing password
    - No credentials in config files

    Workflow:
    1. First time: Use 'login' with username/password
    2. Save token: Use 'save_session_token'
    3. Future logins: Use this 'login_from_cache' tool

    Args:
        host: The URL of the Taiga instance (e.g., 'https://api.taiga.io')
        user_id: Optional user ID override (uses cached value if not provided)

    Returns:
        A dictionary containing the session_id upon successful authentication
    """
    logger.info(f"Executing login_from_cache for host '{host}'")

    # Load token from cache
    token_data = load_token(host)

    if not token_data:
        logger.error(f"No cached token found for {host}")
        return {
            "status": "error",
            "message": f"No cached token found for {host}. Please login with username/password first and use 'save_session_token'.",
        }

    # Use cached user_id if not provided
    if user_id is None:
        user_id = token_data.get("user_id")

    # Login with the cached token
    try:
        wrapper = TaigaClientWrapper(host=host)
        login_successful = wrapper.login_with_token(
            auth_token=token_data["auth_token"],
            token_type=token_data["token_type"],
            user_id=user_id,
        )

        if login_successful:
            session_id = str(uuid.uuid4())
            active_sessions[session_id] = wrapper
            logger.info(f"Cache authentication successful. Session ID: {session_id[:8]}...")
            return {"session_id": session_id}
        else:
            logger.error("Cache authentication unsuccessful.")
            return {
                "status": "error",
                "message": "Token authentication failed. Token may be expired or invalid.",
            }

    except (ValueError, TaigaException) as e:
        logger.error(f"Cache authentication failed: {e}", exc_info=False)
        return {
            "status": "error",
            "message": f"Authentication failed: {str(e)}. You may need to login again and save a new token.",
        }
    except Exception as e:
        logger.error(f"Unexpected error during cache authentication: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}",
        }


@mcp.tool(
    "delete_cached_token",
    description="Deletes a cached authentication token for a specific Taiga host.",
)
def delete_cached_token(host: str) -> dict[str, Any]:
    """
    Delete a cached authentication token.

    Use this when:
    - You want to revoke access from this machine
    - The token is compromised
    - You're switching to a different authentication method

    Args:
        host: The URL of the Taiga instance

    Returns:
        Status information about the deletion
    """
    logger.info(f"Executing delete_cached_token for host '{host}'")

    success = delete_token(host)

    if success:
        return {
            "status": "success",
            "message": f"Cached token deleted for {host}",
            "host": host,
        }
    else:
        return {
            "status": "not_found",
            "message": f"No cached token found for {host}",
            "host": host,
        }


@mcp.tool(
    "list_cached_tokens",
    description="Lists all cached authentication tokens (without revealing the actual token values).",
)
def list_cached_tokens_tool() -> dict[str, Any]:
    """
    List all cached authentication tokens.

    Returns information about cached tokens without exposing the actual token values.
    Useful for:
    - Checking which hosts have cached credentials
    - Auditing saved tokens
    - Managing multiple Taiga instances

    Returns:
        Dictionary with information about cached tokens
    """
    logger.info("Executing list_cached_tokens")

    tokens = list_cached_tokens()

    return {
        "status": "success",
        "count": len(tokens),
        "tokens": tokens,
        "message": f"Found {len(tokens)} cached token(s)",
    }


@mcp.tool(
    "health_check",
    description="Verifies API connectivity and returns server health status. Useful for monitoring and deployment checks.",
)
def health_check(session_id: str) -> dict[str, Any]:
    """
    Perform health check on Taiga API connectivity.

    This tool verifies:
    - Session is valid and active
    - API client is authenticated
    - Can communicate with Taiga API
    - User information is accessible

    Args:
        session_id: The session ID to check

    Returns:
        Dictionary with health status:
        - status: 'healthy' or 'unhealthy'
        - session_active: Whether session exists
        - authenticated: Whether session is authenticated
        - api_accessible: Whether API responds
        - details: Additional diagnostic information

    Example:
        {
            "status": "healthy",
            "session_active": true,
            "authenticated": true,
            "api_accessible": true,
            "host": "https://api.taiga.io",
            "user_id": 12345,
            "details": "All systems operational"
        }
    """
    logger.info(f"Executing health_check for session {session_id[:8]}...")

    health_status = {
        "status": "unhealthy",
        "session_active": False,
        "authenticated": False,
        "api_accessible": False,
        "host": None,
        "user_id": None,
        "details": "",
    }

    try:
        # Check if session exists
        wrapper = active_sessions.get(session_id)
        if not wrapper:
            health_status["details"] = "Session not found or expired"
            return health_status

        health_status["session_active"] = True
        health_status["host"] = wrapper.host

        # Check if authenticated
        if not wrapper.is_authenticated:
            health_status["details"] = "Session exists but not authenticated"
            return health_status

        health_status["authenticated"] = True
        health_status["user_id"] = wrapper.user_id

        # Try to access API (get current user info)
        try:
            if wrapper.api is None:
                health_status["details"] = "API client not initialized"
                return health_status

            wrapper.api.users.get_me()  # Check API accessibility
            health_status["api_accessible"] = True
            health_status["status"] = "healthy"
            health_status["details"] = "All systems operational"
            logger.info(f"Health check passed for session {session_id[:8]}")
        except Exception as api_error:
            health_status["details"] = f"API not accessible: {str(api_error)}"
            logger.warning(f"Health check failed - API error: {api_error}")

        return health_status

    except Exception as e:
        health_status["details"] = f"Health check error: {str(e)}"
        logger.error(f"Health check exception: {e}", exc_info=True)
        return health_status


@mcp.tool(
    "get_server_metrics",
    description="Returns server performance metrics including request counts, error rates, and response times.",
)
def get_server_metrics_tool() -> dict[str, Any]:
    """
    Get server performance metrics.

    Returns:
        A dictionary containing:
        - total_requests: Total number of requests across all tools
        - total_errors: Total number of errors across all tools
        - error_rate: Overall error rate as percentage
        - tools: Per-tool statistics with request counts, error rates, and timing data

    Example:
        {
            "total_requests": 150,
            "total_errors": 5,
            "error_rate": 3.33,
            "tools": {
                "list_projects": {
                    "request_count": 50,
                    "error_count": 1,
                    "error_rate": 2.0,
                    "avg_time": 0.125,
                    "min_time": 0.098,
                    "max_time": 0.234
                }
            }
        }
    """
    logger.debug("Retrieving server metrics")
    return get_server_stats()
