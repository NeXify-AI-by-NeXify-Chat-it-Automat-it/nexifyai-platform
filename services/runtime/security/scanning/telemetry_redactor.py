#!/usr/bin/env python3
import re

PATS = [
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}"), "[REDACTED]"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[REDACTED]"),
    (re.compile(r"-----BEGIN[\s\S]*?PRIVATE KEY-----"), "[REDACTED]"),
    (re.compile(r"(?i)(api_key|secret|password|token)[:=\s]+[\\S]{16,}"), "[CRED]"),
]

def redact(text):
    for pat, rep in PATS:
        text = pat.sub(rep, text)
    return text

if __name__ == "__main__":
    t = "key=ghp_test_token_abc123"
    print("OK:", redact(t)[:30])
