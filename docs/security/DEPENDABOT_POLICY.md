# NeXifyAI — Dependabot Policy
> Owner: NeXifyAI Platform Team | Updated: 2026-05-24

## Configuration
Dependabot is configured in `.github/dependabot.yml` for:
- npm (frontend/ — weekly Monday)
- pip (backend/ — weekly Monday)
- github-actions (/ — weekly Monday)
- docker (docker/ — weekly Monday)

> NOTE: Dependabot watches `/frontend` and `/backend` paths.
> The actual app is under `apps/web/` (npm) and potentially `services/` (pip).
> If updates are missing, verify directory paths in dependabot.yml.

## Auto-Merge Policy

### Allowed (Goose may auto-merge)
- GitHub Actions version bumps (actions/checkout, actions/setup-*)
- Patch-level updates with green CI
- Non-breaking minor updates for dev-only packages

### Requires Human Review
- Major version bumps
- Security-critical packages (auth, crypto, payment)
- Supabase client updates
- Runtime core packages (react major, fastapi major)
- Any update that fails CI

## PR #11 — actions/setup-python from 5 to 6
- Type: github-actions minor bump
- Risk: Low (GitHub Actions runner, no production code impact)
- Recommendation: **MERGE** — after CI passes
- Labels to set: dependencies, ci, github-actions

## 6 Open Vulnerability Alerts
| Priority | Action |
|---|---|
| Critical | Fix in active PR immediately |
| High | Fix within 7 days via Dependabot PR |
| Medium | Fix within 30 days |
| Low | Fix in next maintenance window |

## Grouping Recommendation (dependabot.yml update)
```yaml
groups:
  github-actions-minor:
    patterns: ["actions/*"]
    update-types: ["minor", "patch"]
  npm-patch:
    update-types: ["patch"]
  pip-patch:
    update-types: ["patch"]
```
