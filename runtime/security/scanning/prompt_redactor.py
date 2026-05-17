#!/usr/bin/env python3
import re

PATS = [
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}"), "[R]"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[R]"),
    (re.compile(r"DS_[A-Z0-9_]{10,}__[A-Z_]{3,}"), "[DS]"),
    (re.compile(r"(?i)(api_key|secret|password)[:=\s]+[\\S]{16,}"), "[CRED]"),
    (re.compile(r"-----BEGIN[\s\S]*?PRIVATE KEY-----"), "[KEY]"),
]

def redact(text):
    for pat, rep in PATS:
        text = pat.sub(rep, text)
    return text

def messages(msgs):
    return [dict(m, content=redact(m.get("content",""))) if isinstance(m.get("content"),str) else m for m in msgs]

if __name__ == "__main__":
    t = "sk-test-secret-key-here and ghp_test"
    print("OK:", redact(t)[:30])
