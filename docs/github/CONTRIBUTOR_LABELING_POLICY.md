# NeXifyAI — Contributor Labeling Policy
> Owner: NeXifyAI Platform Team | Updated: 2026-05-24

## good first issue — Eligibility Criteria

### ✅ Eligible Tasks
- Documentation improvements (docs/**, *.md)
- Typo and copy corrections
- JSON file improvements (non-security)
- Isolated React UI components (no auth/billing)
- Adding test coverage for existing functions
- Label and issue template improvements
- README and runbook additions
- DOS/Learning file improvements

### ❌ NOT Eligible (Never label as good first issue)
- Anything touching auth, billing, payment
- Security fixes
- Infra/VDS changes
- Core Brain/OpenRouter configuration
- Supabase RLS/Auth
- CI/CD secrets or environment changes
- Anything requiring production deployment

## help wanted — Criteria
Use for tasks where the core team needs external help:
- Non-critical feature implementations
- Non-sensitive UI improvements
- Test writing
- Documentation
- Translations

## Label Assignment Workflow
```
New Issue/PR Created
  │
  ├─ Auto-label: needs-triage
  │
  └─ Triage Assessment:
       ├─ Security risk? → security:critical/high/medium/low
       ├─ Docs only? → documentation, docs-only
       ├─ CI change? → ci, github-actions
       ├─ Contributor-friendly? → good first issue + help wanted
       └─ Platform area? → frontend/backend/brain/etc.
```

## Suggested good first issue Examples
1. **docs: improve agency DOS file index descriptions**
   - Edit `docs/agency/AGENCY_DOS_FILE_INDEX.md`
   - Add better purpose descriptions for each file
   - Labels: good first issue, documentation, help wanted

2. **docs: add contributor guide for governance-only changes**
   - Create `docs/CONTRIBUTING.md` for governance PR process
   - Labels: good first issue, documentation, help wanted

3. **test: add JSON validation test for docs/agency machine-readable files**
   - Write a Python/Node test that validates all JSON in docs/agency/machine-readable/
   - Labels: good first issue, documentation, backend, help wanted
