"""
Logging configuration for Taiga MCP Server.

Provides structured logging with:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Console output with colored formatting
- Optional file logging with rotation
- Per-module logging (auth, projects, tasks, etc.)
- Timestamp and level information
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ANSI color codes for terminal output
class LogColors:
    """ANSI color codes for colored console output."""

    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_RED = "\033[1;91m"
    RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color to console output.

    Color scheme:
    - DEBUG: Grey
    - INFO: Blue
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Bold Red
    """

    COLORS = {
        logging.DEBUG: LogColors.GREY,
        logging.INFO: LogColors.BLUE,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.BOLD_RED,
    }

    def format(self, record):
        """Format log record with color codes."""
        # Add color to levelname
        color = self.COLORS.get(record.levelno, LogColors.RESET)
        record.levelname = f"{color}{record.levelname}{LogColors.RESET}"

        # Format the message
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    log_to_console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure logging for the Taiga MCP server.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, no file logging.
        log_to_console: Whether to log to console (default: True)
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)

    Example:
        ```python
        # Console only with INFO level
        setup_logging(log_level="INFO")

        # File and console with DEBUG level
        setup_logging(log_level="DEBUG", log_file="logs/taiga_mcp.log")

        # File only with WARNING level
        setup_logging(
            log_level="WARNING",
            log_file="logs/warnings.log",
            log_to_console=False
        )
        ```
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with colors
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(numeric_level)

        console_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
        console_formatter = ColoredFormatter(console_format, datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)

        file_format = (
            "%(asctime)s | %(levelname)-8s | %(name)-30s | "
            "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
        )
        file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Configure module-specific loggers
    _configure_module_loggers(numeric_level)

    # Log the configuration
    logger = logging.getLogger("pytaiga_mcp.logging_config")
    logger.info(f"Logging initialized: level={log_level}, file={log_file or 'None'}")


def _configure_module_loggers(level: int) -> None:
    """
    Configure logging for specific modules.

    This ensures each module has proper logging hierarchy:
    - pytaiga_mcp.server.auth
    - pytaiga_mcp.server.projects
    - pytaiga_mcp.server.tasks
    - etc.
    """
    modules = [
        "pytaiga_mcp",
        "pytaiga_mcp.server",
        "pytaiga_mcp.server.common",
        "pytaiga_mcp.server.auth",
        "pytaiga_mcp.server.projects",
        "pytaiga_mcp.server.tasks",
        "pytaiga_mcp.server.user_stories",
        "pytaiga_mcp.server.issues",
        "pytaiga_mcp.server.epics",
        "pytaiga_mcp.server.milestones",
        "pytaiga_mcp.server.wiki",
        "pytaiga_mcp.taiga_client",
    ]

    for module_name in modules:
        logger = logging.getLogger(module_name)
        logger.setLevel(level)
        logger.propagate = True

    # Silence noisy third-party libraries
    logging.getLogger("pytaigaclient").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Configured logger instance

    Example:
        ```python
        logger = get_logger(__name__)
        logger.info("Server started")
        logger.debug("Processing request", extra={"request_id": "123"})
        logger.error("Failed to connect", exc_info=True)
        ```
    """
    return logging.getLogger(name)
