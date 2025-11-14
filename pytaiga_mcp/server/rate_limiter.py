"""
Rate limiting middleware for Taiga MCP server.
Prevents API abuse by limiting request frequency.
"""

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm.

    Attributes:
        requests_per_minute: Maximum requests allowed per minute per session
        tokens: Dict tracking available tokens per session
        last_update: Dict tracking last token refill time per session
    """

    def __init__(self, requests_per_minute: int = 100):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute (default: 100)
        """
        self.requests_per_minute = requests_per_minute
        self.tokens: dict[str, float] = defaultdict(lambda: float(requests_per_minute))
        self.last_update: dict[str, float] = defaultdict(time.time)
        logger.info(f"Rate limiter initialized: {requests_per_minute} requests/minute")

    def _refill_tokens(self, session_id: str) -> None:
        """
        Refill tokens based on time elapsed since last update.

        Args:
            session_id: Session identifier for token tracking
        """
        now = time.time()
        time_passed = now - self.last_update[session_id]
        # Refill rate: requests_per_minute / 60 tokens per second
        refill_rate = self.requests_per_minute / 60.0
        self.tokens[session_id] = min(
            self.requests_per_minute, self.tokens[session_id] + time_passed * refill_rate
        )
        self.last_update[session_id] = now

    def is_allowed(self, session_id: str) -> bool:
        """
        Check if request is allowed under rate limit.

        Args:
            session_id: Session identifier to check

        Returns:
            True if request is allowed, False if rate limited
        """
        self._refill_tokens(session_id)

        if self.tokens[session_id] >= 1.0:
            self.tokens[session_id] -= 1.0
            return True

        logger.warning(f"Rate limit exceeded for session {session_id[:8]}...")
        return False

    def get_remaining_tokens(self, session_id: str) -> int:
        """
        Get number of remaining tokens for a session.

        Args:
            session_id: Session identifier

        Returns:
            Number of remaining request tokens (rounded down)
        """
        self._refill_tokens(session_id)
        return int(self.tokens[session_id])

    def reset_session(self, session_id: str) -> None:
        """
        Reset rate limit counters for a session.

        Args:
            session_id: Session identifier to reset
        """
        if session_id in self.tokens:
            del self.tokens[session_id]
        if session_id in self.last_update:
            del self.last_update[session_id]
        logger.debug(f"Rate limit reset for session {session_id[:8]}...")


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(func: Callable) -> Callable:
    """
    Decorator to apply rate limiting to MCP tool functions.

    Usage:
        @rate_limit
        @mcp.tool("my_tool")
        def my_tool(session_id: str, ...) -> Dict[str, Any]:
            ...

    Args:
        func: Function to decorate (must have session_id as first argument)

    Returns:
        Wrapped function with rate limiting

    Raises:
        PermissionError: If rate limit is exceeded
    """

    @wraps(func)
    def wrapper(session_id: str, *args: Any, **kwargs: Any) -> Any:
        if not _rate_limiter.is_allowed(session_id):
            remaining = _rate_limiter.get_remaining_tokens(session_id)
            raise PermissionError(
                f"Rate limit exceeded. Too many requests. "
                f"Please wait before making more requests. "
                f"Limit: {_rate_limiter.requests_per_minute} requests/minute. "
                f"Remaining tokens: {remaining}"
            )

        return func(session_id, *args, **kwargs)

    return wrapper


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance.

    Returns:
        The global RateLimiter instance
    """
    return _rate_limiter


def configure_rate_limit(requests_per_minute: int) -> None:
    """
    Configure the global rate limiter.

    Args:
        requests_per_minute: Maximum requests allowed per minute
    """
    global _rate_limiter
    _rate_limiter = RateLimiter(requests_per_minute)
    logger.info(f"Rate limiter reconfigured: {requests_per_minute} requests/minute")
