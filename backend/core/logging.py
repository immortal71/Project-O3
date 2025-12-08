"""
Structured logging configuration for OncoPurpose
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog import get_logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application"""
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
            if settings.is_production
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_struct_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return get_logger(name)


class LoggerMixin:
    """Mixin class to add structured logging to any class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_struct_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    def log_info(self, message: str, **kwargs: Any) -> None:
        self.logger.info(message, **kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        self.logger.error(message, **kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        self.logger.warning(message, **kwargs)

    def log_debug(self, message: str, **kwargs: Any) -> None:
        self.logger.debug(message, **kwargs)


# Convenience functions for quick logging
def info(message: str, **kwargs: Any) -> None:
    get_struct_logger().info(message, **kwargs)


def error(message: str, **kwargs: Any) -> None:
    get_struct_logger().error(message, **kwargs)


def warning(message: str, **kwargs: Any) -> None:
    get_struct_logger().warning(message, **kwargs)


def debug(message: str, **kwargs: Any) -> None:
    get_struct_logger().debug(message, **kwargs)
