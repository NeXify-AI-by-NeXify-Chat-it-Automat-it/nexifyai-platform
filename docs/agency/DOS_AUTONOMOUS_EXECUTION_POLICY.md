# DOS — Autonomous Execution Policy
> Standard: DOS v2.0 | Owner: NeXifyAI Platform Team | Updated: 2026-05-24
> See also: `docs/github/AUTONOMOUS_GITHUB_OPERATIONS.md`

## Purpose
Define exactly what Goose (and future AI agents) may execute autonomously
without explicit human approval, and what requires human sign-off.

## Autonomous Execution Tiers

### Tier 1 — ALWAYS Autonomous (no human needed)
- Brain read/write/query
- DOS/Learning/Prevention document updates
- Local file reads and analysis
- Branch creation
- Commits to feature branches
- Pushes to feature branches (not main)
- PR creation
- PR labeling
- PR commenting (no secret values)
- Issue creation (no secret values)
- JSON validation
- Secret pattern scanning (no value output)
- YAML syntax validation

### Tier 2 — Conditionally Autonomous (conditions documented below)
- PR merging (conditions: see AUTONOMOUS_GITHUB_OPERATIONS.md)
- Dependabot PR merging (conditions: minor/patch + CI green)
- CI workflow updates (conditions: no secrets, no production scope change)
- docs/agency file updates (conditions: no content deletion, consistent with DOS)
- CodeQL path exclusions for confirmed archive dirs (conditions: evidence documented)

### Tier 3 — NEVER Autonomous (human required)
- main branch direct push
- Secret rotation (when external UI/API needed)
- Production service restarts
- DB migrations in production
- Supabase RLS/Auth changes
- Billing/Payment changes
- Customer project code copying
- Closing security alerts without evidence
- Any action outside documented scope

## Evidence Requirements for Tier 2 Actions
Before any Tier 2 action, document in Brain:
- category: autonomous-action-log
- content: action taken, conditions met, diff summary, result

## Conflict Resolution
If Goose is unsure whether an action is Tier 1, 2, or 3:
→ Default to Tier 3 behavior (human required)
→ Create needs-triage issue
→ Document analysis in Brain

## Version History
| Version | Change | Date |
|---|---|---|
| 1.0 | Initial policy | 2026-05-24 |
