"""
Logging configuration module for the Conntour Space Explorer.

This module provides a centralized logging setup with configurable log levels
and destinations (console + file).

Environment variables:
- LOG_LEVEL: log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO.
- LOG_FILE:  path to log file. Default: logs/app.log
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "conntour-space-explorer",
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Set up and configure a logger for the application.

    Args:
        name: Logger name (default: "conntour-space-explorer")
        log_level: Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If None, reads from LOG_LEVEL environment variable or defaults to DEBUG.
        log_format: Custom log format string. If None, uses a default format.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times if logger already configured
    if logger.handlers:
        return logger

    # Determine log level
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Convert string to logging level
    numeric_level = getattr(logging, log_level, logging.INFO)
    logger.setLevel(numeric_level)

    # Set log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating)
    log_file = os.getenv("LOG_FILE", "logs/app.log")
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Create a default logger instance for easy import
logger = setup_logger()

