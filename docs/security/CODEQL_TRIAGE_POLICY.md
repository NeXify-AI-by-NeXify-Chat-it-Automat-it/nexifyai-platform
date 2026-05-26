# NeXifyAI — CodeQL Triage Policy
> Owner: NeXifyAI Platform Team | Updated: 2026-05-24

## Overview
~111 CodeQL alerts exist. The majority are expected to be archive/legacy false positives.
This policy governs how we classify, fix, and exclude alerts.

## Scan Scope (current codeql.yml)
```yaml
paths:
  - frontend/**
  - backend/**
  - public/**
```
> NOTE: `_archive/` and `knowledge/` are NOT in scan paths but may still be picked up
> by CodeQL autobuild. See Archive Scan Policy for exclusion steps.

## Classification Flow

```
CodeQL Alert
    │
    ├─ File under _archive/ or knowledge/?
    │       └─ YES → category: archive_legacy
    │                 → action: exclude_archive_from_scan
    │                 → DO NOT close without confirming not in production
    │
    ├─ File is generated bundle (*.min.js, bundle.js, dist/**)?
    │       └─ YES → category: false_positive_candidate
    │                 → action: mark_false_positive_with_evidence
    │
    ├─ File is test/fixture (*.test.*, __tests__/**, fixtures/**)?
    │       └─ YES → Low priority, document, optionally dismiss
    │
    ├─ File is production code (backend/, frontend/, services/)?
    │       ├─ SSRF / Injection / Auth bypass?
    │       │       └─ YES → fix_now (P1 if Critical/High)
    │       └─ Other?
    │               └─ Assess with developer
    │
    └─ UNKNOWN → Triage required, tag needs-triage
```

## SSRF Fix Plan — crawl4ai_service.py (P1 — CRITICAL)

### Problem
External URL inputs passed to crawl4ai without validation.
An attacker can supply internal URLs (http://localhost/, http://169.254.169.254/ metadata).

### Fix Requirements
1. Validate all incoming URLs before passing to crawl4ai
2. Block: private IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, ::1)
3. Block: cloud metadata endpoints (169.254.169.254, fd00:ec2::254)
4. Allowlist if possible: only known external domains
5. Disable redirects or validate redirect targets
6. Set max timeout (10s recommended)
7. Log blocked attempts
8. Add unit tests for blocked URLs

### Example Python Validator (template — adapt to actual code)
```python
import ipaddress, re
from urllib.parse import urlparse

BLOCKED_PATTERNS = [
    r"169\.254\.169\.254",  # AWS metadata
    r"fd00:ec2",               # AWS metadata IPv6
    r"localhost",
    r"127\.\d+\.\d+\.\d+",
    r"0\.0\.0\.0",
]

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    try:
        addr = ipaddress.ip_address(parsed.hostname)
        if addr.is_private or addr.is_loopback or addr.is_reserved:
            return False
    except ValueError:
        pass  # hostname, not IP — OK
    return True
```

## Exclusion Process for Archive Alerts
See `docs/security/ARCHIVE_SCAN_POLICY.md`

## Closing Alerts — Requirements
- `false_positive`: Must include: file path, reason it's not exploitable, evidence
- `won't fix`: Must include: risk assessment, compensating control
- `archive_legacy`: Must confirm file is not reachable in production
- Secret alerts: NEVER close without confirmed rotation

## Review Cadence
| Severity | Review Interval |
|---|---|
| Critical/High | Weekly |
| Medium | Monthly |
| Low | Quarterly |
