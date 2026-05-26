# NeXifyAI — Security Alert Backlog
> Owner: NeXifyAI Platform Team | Updated: 2026-05-24 | Source: GitHub Security & Quality
> ⚠️ No secret values are stored here. All tokens redacted.

## Status Summary (as of 2026-05-24)
| Category | Count | Status |
|---|---|---|
| Secret Scanning | ~3 (2 default + 1 generic) | ⚠️ ROTATION REQUIRED — P0 |
| Code Scanning (CodeQL) | ~111 | Triage in progress |
| Dependabot Vulnerabilities | 6 | PRs available |

## Secret Scanning Alerts
> ⚠️ Values are REDACTED. Do not populate with actual tokens.

| Alert # | Type | Location (redacted) | Status | Action |
|---|---|---|---|---|
| SS-001 | GitHub Token (default) | Path: ***REDACTED*** | Open | Rotate immediately |
| SS-002 | API Token (default) | Path: ***REDACTED*** | Open | Rotate immediately |
| SS-003 | Generic Secret | Path: ***REDACTED*** | Open | Assess + rotate |

**Rotation Required: YES — ALL 3 TOKENS MUST BE REVOKED AND REPLACED**

## CodeQL Alerts — Priority Classification

### P1: Critical — Immediate Action Required
| ID | Rule | File | Category | Action |
|---|---|---|---|---|
| CQL-CRIT-001 | SSRF (Server-Side Request Forgery) | services/api/services/crawl4ai_service.py | real_core | fix_now |

### P2: High — Fix within 14 days  
| ID | Rule | File | Category | Action |
|---|---|---|---|---|
| CQL-HIGH-* | Various | TBD via gh api when authenticated | TBD | manual_review |

### P3-P6: Medium/Low
> Bulk classification pending GitHub API access. Expected distribution:
> - ~80% under _archive/ or knowledge/ → archive_legacy → exclude_archive_from_scan
> - ~15% under frontend/backend → real_app/real_core → fix or dismiss with evidence
> - ~5% genuine false positives → mark_false_positive_with_evidence

## Dependabot Vulnerabilities
| Package | Ecosystem | Severity | Manifest | PR Available |
|---|---|---|---|---|
| actions/setup-python | github-actions | Low | .github/workflows | PR #11 ✅ |
| TBD-1 | npm | TBD | apps/web/ | Check Dependabot branches |
| TBD-2 | npm | TBD | apps/web/ | Check Dependabot branches |
| TBD-3 | pip | TBD | backend/ | TBD |

> Full Dependabot details require `gh auth login` to access API.

## Archive Classification Decision
`_archive/` and `knowledge/` directories exist in repo root.
These are NOT production code. CodeQL scanning these generates false positives.

**Decision: Exclude from CodeQL scan paths via .github/workflows/codeql.yml**
**Evidence required before closing any archive alert.**
