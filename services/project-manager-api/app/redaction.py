"""Secret redaction for logs and stored data."""
import re
from typing import Any

# Patterns to redact common secret formats
_TOKEN_PATTERNS = [
    r'ghp_[A-Za-z0-9]{36}',
    r'github_pat_[A-Za-z0-9_]+',
    r'sk-[A-Za-z0-9]{20,}',
    r'xox[baprs]-[A-Za-z0-9\-]+',
    r'AIza[A-Za-z0-9_\-]{35}',
    r'ya29\.[A-Za-z0-9_\-]+',
]

_OBFUSCATED_PATTERNS = [
    r'(?:password|passwd|secret|token|api_key|apikey|authorization)\s*[:=]\s*\S{4,}',
]

def redact_string(text: str) -> str:
    result = text
    for pat in _TOKEN_PATTERNS:
        result = re.sub(pat, '[REDACTED]', result, flags=re.IGNORECASE)
    result = re.sub(r'Bearer\s+[A-Za-z0-9_\-\.]+', 'Bearer [REDACTED]', result)
    for pat in _OBFUSCATED_PATTERNS:
        result = re.sub(pat, '[KEY_REDACTED]', result, flags=re.IGNORECASE)
    return result

def redact_dict(obj: Any) -> Any:
    if isinstance(obj, str):
        return redact_string(obj)
    if isinstance(obj, dict):
        return {k: redact_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_dict(v) for v in obj]
    return obj
