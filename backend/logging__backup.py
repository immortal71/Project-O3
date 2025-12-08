"""
Backup copy of legacy logging (renamed to avoid shadowing stdlib logging)
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog import get_logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application (backup)"""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def get_struct_logger(name: str = None) -> structlog.BoundLogger:
    return get_logger(name)


def info(message: str, **kwargs: Any) -> None:
    get_struct_logger().info(message, **kwargs)


def error(message: str, **kwargs: Any) -> None:
    get_struct_logger().error(message, **kwargs)
