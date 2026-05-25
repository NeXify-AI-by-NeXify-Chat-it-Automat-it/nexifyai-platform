"""Secret redaction for logs and stored data."""
import logging
import re
from typing import Any

logger = logging.getLogger("pm.redaction")

_TOKEN_PATTERNS = [
    r'ghp_[A-Za-z0-9]{36}',
    r'github_pat_[A-Za-z0-9_]+',
    r'sk-[A-Za-z0-9]{20,}',
    r'xox[baprs]-[A-Za-z0-9\-]+',
    r'AIza[A-Za-z0-9_\-]{35}',
    r'ya29\.[A-Za-z0-9_\-]+',
]

_OBFUSCATED_PATTERNS = [
    (r'(Authorization:\s*Bearer\s*)\S+', r'\1[REDACTED]'),
    (r'(api[_-]?key[_-]?\s*[:=]\s*)\S+', r'\1[KEY_REDACTED]'),
    (r'(secret[_-]?\s*[:=]\s*)\S+', r'\1[KEY_REDACTED]'),
    (r'(token[_-]?\s*[:=]\s*)\S+', r'\1[KEY_REDACTED]'),
    (r'(password[_-]?\s*[:=]\s*)\S+', r'\1[KEY_REDACTED]'),
]

def redact_string(text: str) -> str:
    if not text:
        return text
    for pattern in _TOKEN_PATTERNS:
        text = re.sub(pattern, '[REDACTED]', text)
    for pattern, replacement in _OBFUSCATED_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def redact_dict(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: redact_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_dict(v) for v in data]
    elif isinstance(data, str):
        return redact_string(data)
    return data
