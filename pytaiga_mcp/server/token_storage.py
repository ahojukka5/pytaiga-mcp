"""
Secure token storage for Taiga MCP server.
Stores authentication tokens in a secure cache directory.
"""

import json
import logging
import os
import stat
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_cache_dir() -> Path:
    """
    Get the cache directory for storing tokens.
    Uses XDG_CACHE_HOME on Linux, ~/Library/Caches on macOS, or ~/.cache as fallback.
    """
    if os.name == "nt":  # Windows
        cache_base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif os.name == "posix":
        if os.uname().sysname == "Darwin":  # macOS
            cache_base = Path.home() / "Library" / "Caches"
        else:  # Linux
            cache_base = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
    else:
        cache_base = Path.home() / ".cache"

    cache_dir = cache_base / "taiga-mcp"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Set restrictive permissions (user-only read/write)
    try:
        os.chmod(cache_dir, stat.S_IRWXU)  # 0o700
    except Exception as e:
        logger.warning(f"Could not set restrictive permissions on cache dir: {e}")

    return cache_dir


def get_token_file(host: str) -> Path:
    """
    Get the token file path for a specific Taiga host.
    Each host gets its own token file.
    """
    cache_dir = get_cache_dir()
    # Sanitize host for filename (replace special chars with underscores)
    safe_host = "".join(c if c.isalnum() or c in [".", "-"] else "_" for c in host)
    token_file = cache_dir / f"token_{safe_host}.json"
    return token_file


def save_token(
    host: str, auth_token: str, token_type: str = "Bearer", user_id: int | None = None
) -> bool:
    """
    Save authentication token to cache.

    Args:
        host: The Taiga instance URL
        auth_token: The authentication token
        token_type: Type of token ("Bearer" or "Application")
        user_id: Optional user ID

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        token_file = get_token_file(host)

        token_data = {
            "host": host,
            "auth_token": auth_token,
            "token_type": token_type,
            "user_id": user_id,
        }

        # Write with restrictive permissions
        token_file.write_text(json.dumps(token_data, indent=2))
        os.chmod(token_file, stat.S_IRUSR | stat.S_IWUSR)  # 0o600 - user read/write only

        logger.info(f"Token saved successfully to {token_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to save token: {e}", exc_info=True)
        return False


def load_token(host: str) -> dict[str, Any] | None:
    """
    Load authentication token from cache.

    Args:
        host: The Taiga instance URL

    Returns:
        Dictionary with token data or None if not found
    """
    try:
        token_file = get_token_file(host)

        if not token_file.exists():
            logger.debug(f"No cached token found for {host}")
            return None

        # Check file permissions for security
        file_stat = token_file.stat()
        if file_stat.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
            logger.warning(f"Token file has insecure permissions: {oct(file_stat.st_mode)}")

        token_data = json.loads(token_file.read_text())

        # Validate token data structure
        required_fields = ["host", "auth_token", "token_type"]
        if not all(field in token_data for field in required_fields):
            logger.error("Invalid token data structure in cache")
            return None

        logger.info(f"Token loaded successfully from {token_file}")
        return token_data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in token file: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load token: {e}", exc_info=True)
        return None


def delete_token(host: str) -> bool:
    """
    Delete cached token for a specific host.

    Args:
        host: The Taiga instance URL

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        token_file = get_token_file(host)

        if token_file.exists():
            token_file.unlink()
            logger.info(f"Token deleted successfully: {token_file}")
            return True
        else:
            logger.debug(f"No token file to delete for {host}")
            return False

    except Exception as e:
        logger.error(f"Failed to delete token: {e}", exc_info=True)
        return False


def list_cached_tokens() -> dict[str, dict]:
    """
    List all cached tokens.

    Returns:
        Dictionary mapping hosts to their token info (without actual tokens)
    """
    try:
        cache_dir = get_cache_dir()
        tokens = {}

        for token_file in cache_dir.glob("token_*.json"):
            try:
                token_data = json.loads(token_file.read_text())
                host = token_data.get("host", "unknown")
                tokens[host] = {
                    "token_type": token_data.get("token_type"),
                    "user_id": token_data.get("user_id"),
                    "file": str(token_file),
                }
            except Exception as e:
                logger.warning(f"Could not read token file {token_file}: {e}")

        return tokens

    except Exception as e:
        logger.error(f"Failed to list tokens: {e}", exc_info=True)
        return {}
