#!/usr/bin/env python3
"""Log Redactor — redacts secrets from logs and telemetry."""
import re
PATS = [
    (r'(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}', '[REDACTED_TOKEN]'),
    (r'github_pat_[A-Za-z0-9_]{22,}', '[REDACTED_PAT]'),
    (r'sk-[A-Za-z0-9]{20,}', '[REDACTED_SK]'),
    (r'-----BEGIN[\s\S]*?PRIVATE KEY-----', '[REDACTED_KEY]'),
]
def redact(text):
    for pat, rep in PATS:
        text = re.sub(pat, rep, text)
    return text
def redact_json(obj):
    if isinstance(obj, str): return redact(obj)
    if isinstance(obj, dict): return {k: redact_json(v) for k,v in obj.items()}
    if isinstance(obj, list): return [redact_json(i) for i in obj]
    return obj
if __name__ == "__main__":
    print(redact("ghp_test123456789012345678901234567890abcde"))
