"""
NeXifyAI — Zentrales Logging-System
Einheitliches Logging auf allen Ebenen: JSON-Strukturiert, Log-Level pro Environment.
"""
import os
import sys
import json
import re
import logging
from datetime import datetime, timezone


SENSITIVE_PATTERNS = [
    (r"(?i)(api_key[\"']?\s*[:=]\s*['\"]?)[^'\"\s,;}\]]+", r"\1[REDACTED]"),
    (r"(?i)(secret[\"']?\s*[:=]\s*['\"]?)[^'\"\s,;}\]]+", r"\1[REDACTED]"),
    (r"(?i)(token[\"']?\s*[:=]\s*['\"]?)[^'\"\s,;}\]]+", r"\1[REDACTED]"),
    (r"(?i)(password[\"']?\s*[:=]\s*['\"]?)[^'\"\s,;}\]]+", r"\1[REDACTED]"),
    (r"(?i)(bearer\s+)[a-z0-9._-]+", r"\1[REDACTED]"),
    (r"(?i)(authorization[\"']?\s*[:=]\s*['\"]?)[^'\"\s,;}\]]+", r"\1[REDACTED]"),
    (r"(?i)(key[\"']?\s*[:=]\s*['\"]?)[^'\"\s,;}\]]{8,}", r"\1[REDACTED]"),
    (r"(?i)(credential[\"']?\s*[:=]\s*['\"]?)[^'\"\s,;}\]]+", r"\1[REDACTED]"),
]


def redact_sensitive(msg: str) -> str:
    """Entfernt sensitive Daten aus Log-Nachrichten."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        msg = re.sub(pattern, replacement, msg)
    return msg


class JsonFormatter(logging.Formatter):
    """Production-taugliches JSON-Log-Format mit Redaction."""
    def format(self, record):
        msg = record.getMessage()
        msg = redact_sensitive(msg)
        log_entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": msg,
        }
        if record.exc_info and record.exc_info[0]:
            exc_text = self.formatException(record.exc_info)
            exc_text = redact_sensitive(exc_text)
            log_entry["exception"] = exc_text
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data
        return json.dumps(log_entry, ensure_ascii=False, default=str)


def setup_logging():
    """Initialisiert das Logging-System basierend auf Environment."""
    env = os.environ.get("ENVIRONMENT", "development")
    is_prod = env in ("production", "prod", "staging")
    level = logging.INFO if is_prod else logging.DEBUG

    root = logging.getLogger()
    root.setLevel(level)

    # Entferne bestehende Handler
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    if is_prod:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

    root.addHandler(handler)

    # Externe Libraries auf WARNING setzen
    for noisy in ["urllib3", "httpcore", "httpx", "asyncio", "uvicorn.access"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("nexifyai").setLevel(level)

    return logging.getLogger("nexifyai")
