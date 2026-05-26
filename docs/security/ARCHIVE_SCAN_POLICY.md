# NeXifyAI — Archive/Legacy Scan Policy
> Owner: NeXifyAI Platform Team | Updated: 2026-05-24

## Problem
The repository contains legacy/archive directories:
- `_archive/` — historical code not used in production
- `knowledge/` — historical knowledge base not used in production

CodeQL autobuild may scan these, generating false-positive alerts
that inflate the security backlog and obscure real findings.

## Classification Rules

| Directory | Status | Production Impact | Scan Required |
|---|---|---|---|
| `_archive/` | Legacy/Archive | NONE | NO |
| `knowledge/` | Historical KB | NONE | NO |
| `frontend/` | Active | YES | YES |
| `backend/` | Active | YES | YES |
| `services/` | Active | YES | YES |
| `apps/web/` | Active | YES | YES |
| `public/` | Active (static) | YES | YES |

## Exclusion Options

### Option A: CodeQL paths-ignore (preferred)
Add to `.github/workflows/codeql.yml`:
```yaml
    steps:
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v4
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality
          paths-ignore:
            - '_archive/**'
            - 'knowledge/**'
            - '**/*.min.js'
            - '**/dist/**'
            - '**/bundle.js'
```

### Option B: .codeqlignore file
Create `.codeqlignore` in repo root:
```
_archive/
knowledge/
```

### Option C: Remove archive from repo (governance decision)
Only if archive has no historical value.
Requires separate governance decision + PR.
NOT to be done autonomously.

## Evidence Requirements for Closing Archive Alerts
Before closing any alert from archive paths:
1. Confirm file is under `_archive/` or `knowledge/`
2. Confirm file is not imported or required anywhere in production code
3. `grep -r "archive_filename" frontend/ backend/ services/ apps/` → zero results
4. Document evidence in alert dismissal comment

## Recommended Next Step
Add `paths-ignore` to `codeql.yml` in a separate PR:
`chore: exclude archive dirs from codeql scan`
Expected alert reduction: ~80+ alerts
