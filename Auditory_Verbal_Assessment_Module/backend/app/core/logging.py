import logging
import sys
from typing import Any, Dict, Optional
from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Standardized JSON/Structured Log Formatter for production log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Contextual metadata from extra params
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        import json

        return json.dumps(log_obj)


def setup_logging():
    """Initializes structured logging configuration across the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)

    if settings.LOG_FORMAT_JSON:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s (%(filename)s:%(lineno)d)"
        )

    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # Uvicorn log level overrides
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)


logger = logging.getLogger("mentiscope.app")


def log_audit_event(event_name: str, payload: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None):
    """Helper logging structured audit trail events."""
    extra = {}
    if correlation_id:
        extra["correlation_id"] = correlation_id
    logger.info(f"[AUDIT EVENT] {event_name}: {payload or {}}", extra=extra)
