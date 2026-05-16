"""
NeXifyAI — Structured JSON Logging
Loki-compatible JSON log format with trace correlation.

Usage:
    from backend.monitoring.logging import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    logger.info("User login", extra={"user_id": "xyz", "tenant": "abc"})
"""

import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for Loki ingestion."""

    def __init__(self, service_name: str = "nexifyai"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": os.getenv("ENVIRONMENT", "production"),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace context if available
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        if hasattr(record, "span_id"):
            log_entry["span_id"] = record.span_id

        # Add extra fields
        if hasattr(record, "extra_fields") and record.extra_fields:
            log_entry["extra"] = record.extra_fields

        # Add exception info
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        # Add request context (if set via adapter)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        return json.dumps(log_entry, default=str)


class ContextFilter(logging.Filter):
    """Add request context to log records."""

    def __init__(self):
        super().__init__()
        self._request_id: Optional[str] = None
        self._user_id: Optional[str] = None
        self._trace_id: Optional[str] = None
        self._span_id: Optional[str] = None

    def set_context(
        self,
        request_id: str = None,
        user_id: str = None,
        trace_id: str = None,
        span_id: str = None,
    ):
        self._request_id = request_id or str(uuid.uuid4())
        self._user_id = user_id
        self._trace_id = trace_id
        self._span_id = span_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = self._request_id or str(uuid.uuid4())
        if self._user_id:
            record.user_id = self._user_id
        if self._trace_id:
            record.trace_id = self._trace_id
        if self._span_id:
            record.span_id = self._span_id
        return True


# ══════════════════════════════════════════
# SETUP
# ══════════════════════════════════════════

_context_filter = ContextFilter()


def setup_logging(
    service_name: str = "nexifyai",
    level: str = None,
    json_output: bool = True,
):
    """Configure structured JSON logging."""
    level = level or os.getenv("LOG_LEVEL", "INFO")
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))

    if json_output:
        handler.setFormatter(JsonFormatter(service_name))
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))

    handler.addFilter(_context_filter)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    for noisy in ["uvicorn.access", "httpx", "httpcore", "opentelemetry"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with context injection."""
    logger = logging.getLogger(name)
    logger.addFilter(_context_filter)
    return logger


def set_request_context(
    request_id: str = None,
    user_id: str = None,
    trace_id: str = None,
    span_id: str = None,
):
    """Set request context for all subsequent log entries."""
    _context_filter.set_context(
        request_id=request_id,
        user_id=user_id,
        trace_id=trace_id,
        span_id=span_id,
    )
