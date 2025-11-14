"""
Metrics collection for Taiga MCP server.
Tracks request counts, error rates, and response times.
"""

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Metrics:
    """
    Container for server metrics.

    Attributes:
        request_count: Total number of requests per tool
        error_count: Total number of errors per tool
        total_time: Total execution time per tool (seconds)
        min_time: Minimum execution time per tool (seconds)
        max_time: Maximum execution time per tool (seconds)
    """

    request_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    error_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_time: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    min_time: dict[str, float] = field(default_factory=lambda: defaultdict(lambda: float("inf")))
    max_time: dict[str, float] = field(default_factory=lambda: defaultdict(float))

    def record_request(self, tool_name: str, duration: float, success: bool = True) -> None:
        """
        Record a request execution.

        Args:
            tool_name: Name of the tool executed
            duration: Execution time in seconds
            success: Whether the request succeeded (default: True)
        """
        self.request_count[tool_name] += 1
        self.total_time[tool_name] += duration
        self.min_time[tool_name] = min(self.min_time[tool_name], duration)
        self.max_time[tool_name] = max(self.max_time[tool_name], duration)

        if not success:
            self.error_count[tool_name] += 1

    def get_stats(self, tool_name: str) -> dict[str, Any]:
        """
        Get statistics for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dict containing request count, error count, avg/min/max time, error rate
        """
        count = self.request_count[tool_name]
        if count == 0:
            return {
                "request_count": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "avg_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
            }

        avg_time = self.total_time[tool_name] / count
        error_rate = self.error_count[tool_name] / count

        return {
            "request_count": count,
            "error_count": self.error_count[tool_name],
            "error_rate": round(error_rate * 100, 2),  # Percentage
            "avg_time": round(avg_time, 3),
            "min_time": round(self.min_time[tool_name], 3),
            "max_time": round(self.max_time[tool_name], 3),
        }

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """
        Get statistics for all tools.

        Returns:
            Dict mapping tool names to their statistics
        """
        return {tool_name: self.get_stats(tool_name) for tool_name in self.request_count.keys()}

    def reset(self) -> None:
        """Reset all metrics to zero."""
        self.request_count.clear()
        self.error_count.clear()
        self.total_time.clear()
        self.min_time.clear()
        self.max_time.clear()
        logger.info("Metrics reset")


# Global metrics instance
_metrics = Metrics()


def track_metrics(func: Callable) -> Callable:
    """
    Decorator to track execution metrics for MCP tool functions.

    Usage:
        @track_metrics
        @mcp.tool("my_tool")
        def my_tool(session_id: str, ...) -> Dict[str, Any]:
            ...

    Args:
        func: Function to decorate

    Returns:
        Wrapped function with metrics tracking
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tool_name = func.__name__
        start_time = time.time()
        success = True

        try:
            result = func(*args, **kwargs)
            return result
        except Exception:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            _metrics.record_request(tool_name, duration, success)

            if success:
                logger.debug(f"{tool_name} completed in {duration:.3f}s")
            else:
                logger.warning(f"{tool_name} failed after {duration:.3f}s")

    return wrapper


def get_metrics() -> Metrics:
    """
    Get the global metrics instance.

    Returns:
        The global Metrics instance
    """
    return _metrics


def get_server_stats() -> dict[str, Any]:
    """
    Get overall server statistics.

    Returns:
        Dict containing aggregated server metrics:
        - total_requests: Total number of requests across all tools
        - total_errors: Total number of errors across all tools
        - error_rate: Overall error rate percentage
        - tools: Per-tool statistics
    """
    all_stats = _metrics.get_all_stats()

    total_requests = sum(stats["request_count"] for stats in all_stats.values())
    total_errors = sum(stats["error_count"] for stats in all_stats.values())
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

    return {
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": round(error_rate, 2),
        "tools": all_stats,
    }
