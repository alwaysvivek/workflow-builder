"""
Structured JSON logging configuration.

Provides a JSON formatter for all application logs, emitting structured
log entries to stdout for production observability.
"""

import logging
import json
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include any extra fields passed via `extra={}`
        for key in ("workflow_id", "run_id", "step", "action", "method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        return json.dumps(log_entry)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with JSON formatting to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    # Remove any default handlers (e.g. uvicorn's)
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet down noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Use module __name__ as convention."""
    return logging.getLogger(name)
