"""
Authentication cache management for pytaiga-mcp.

Stores authentication tokens in ~/.cache/pytaiga-mcp/ with proper permissions.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


def get_cache_dir() -> Path:
    """Get the cache directory for authentication tokens."""
    cache_home = os.environ.get("XDG_CACHE_HOME")
    if cache_home:
        cache_dir = Path(cache_home) / "pytaiga-mcp"
    else:
        cache_dir = Path.home() / ".cache" / "pytaiga-mcp"

    cache_dir.mkdir(parents=True, exist_ok=True)
    # Ensure cache directory has secure permissions (user only)
    cache_dir.chmod(0o700)
    return cache_dir


def get_cache_file(host: str) -> Path:
    """Get the cache file path for a specific host."""
    cache_dir = get_cache_dir()
    # Sanitize host for filename
    safe_host = host.replace("://", "_").replace("/", "_").replace(":", "_")
    return cache_dir / f"{safe_host}.json"


def save_token(host: str, token: str, user_id: Optional[int] = None) -> None:
    """
    Save authentication token to cache.

    Args:
        host: Taiga instance URL
        token: Authentication token
        user_id: Optional user ID
    """
    cache_file = get_cache_file(host)

    data: dict[str, Any] = {"host": host, "token": token}
    if user_id is not None:
        data["user_id"] = user_id

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)

    # Ensure file has secure permissions (user read/write only)
    cache_file.chmod(0o600)


def load_token(host: str) -> Optional[dict]:
    """
    Load authentication token from cache.

    Args:
        host: Taiga instance URL

    Returns:
        Dict with 'token' and optionally 'user_id', or None if not found
    """
    cache_file = get_cache_file(host)

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError):
        return None


def delete_token(host: str) -> bool:
    """
    Delete cached token for a host.

    Args:
        host: Taiga instance URL

    Returns:
        True if token was deleted, False if it didn't exist
    """
    cache_file = get_cache_file(host)

    if cache_file.exists():
        cache_file.unlink()
        return True
    return False


def list_cached_hosts() -> list[str]:
    """
    List all hosts with cached tokens.

    Returns:
        List of host URLs
    """
    cache_dir = get_cache_dir()
    hosts = []

    for cache_file in cache_dir.glob("*.json"):
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                if "host" in data:
                    hosts.append(data["host"])
        except (json.JSONDecodeError, IOError):
            continue

    return hosts


def clear_all_tokens() -> int:
    """
    Clear all cached tokens.

    Returns:
        Number of tokens cleared
    """
    cache_dir = get_cache_dir()
    count = 0

    for cache_file in cache_dir.glob("*.json"):
        try:
            cache_file.unlink()
            count += 1
        except IOError:
            continue

    return count
