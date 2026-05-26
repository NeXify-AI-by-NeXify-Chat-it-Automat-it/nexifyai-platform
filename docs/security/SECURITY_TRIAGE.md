# NeXifyAI — Security Triage Policy
> Owner: NeXifyAI Platform Team | Standard: DOS v2.0 | Updated: 2026-05-24

## Priority Order

| Priority | Category | Action |
|---|---|---|
| P0 | Secret Scanning Alerts | Rotate immediately, revoke compromised token, close alert with evidence |
| P1 | CodeQL Critical | Fix or exclude with documented evidence within 7 days |
| P2 | CodeQL High | Fix or exclude within 14 days |
| P3 | Dependabot Critical/High | Update via PR within 7 days |
| P4 | CodeQL Medium | Triage within 30 days |
| P5 | Dependabot Medium/Low | Update in next maintenance window |
| P6 | CodeQL Low / False Positive | Classify and document; exclude if archive/test |

## Secret Alert Protocol (P0)
1. DO NOT output secret values in any log, issue, PR, or comment
2. Immediately revoke the token at the provider (GitHub, OpenRouter, etc.)
3. Generate a new least-privilege replacement token
4. Store new token in secure secret store only (never in repo)
5. Search git history: `git log -S "partial_pattern" --all`
6. Check systemd/env/journal for exposure
7. Close GitHub Secret Alert only AFTER rotation is confirmed
8. Document incident in `docs/security/incidents/`

## CodeQL Triage Categories

| Category | Definition | Action |
|---|---|---|
| real_core | Production platform code (backend/, frontend/, services/) | Fix now |
| real_app | Production app code (apps/web/) | Fix now |
| archive_legacy | Under _archive/, knowledge/, old bundles | Classify, exclude from scan if confirmed legacy |
| test_fixture | Test files, fixtures, mocks | Low priority, document |
| false_positive_candidate | Pattern match with no real risk | Dismiss with evidence |
| dependency | Third-party dependency code | Use Dependabot |
| unknown | Not yet classified | Triage required |

## Escalation
- P0 secrets: Immediate manual action required — cannot be automated
- P1 CodeQL SSRF in `crawl4ai_service.py`: Block external URL inputs, add allowlist/blocklist
- Archive alerts: Do NOT close without classification evidence
