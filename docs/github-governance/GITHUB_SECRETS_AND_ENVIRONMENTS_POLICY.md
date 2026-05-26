# GitHub Secrets and Environments Policy

## Principles
1. **No secrets in code.** All secrets stored via GitHub Secrets UI or systemd overrides.
2. **Granular scoping.** Actions → repo secrets. Deploy → environment secrets. Agents → agent secrets.
3. **Per-environment isolation.** Production secrets never exposed to staging workflows.
4. **Rotation documented.** Each secret has defined rotation interval and owner.
5. **Central registry.** All secrets documented by name in `SECRET_REGISTRY_POLICY.md`.

## Environment Structure

| Environment | Purpose | Required Reviewers | Branch Restriction | Wait Timer |
|-------------|---------|-------------------|--------------------|------------|
| `production-platform` | PM API, Brain, Worker | 1 | `main` | 0 |
| `production-web` | Frontend (Vercel) | 1 | `main` | 0 |
| `production-frontend` | Legacy frontend | 1 | `main` | 0 |
| `staging-platform` | Pre-deploy validation | 0 | `develop`, `feat/*` | 0 |
| `staging-web` | Web preview | 0 | `develop`, `feat/*` | 0 |
| `security-review` | Code scanning trust | 2 | `main` | 5min |

## Legacy: `cline-actions`
- Status: **CLINE is DEAD LEGACY**
- No workflows currently reference `cline-actions` environment.
- **Action**: Remove environment after verification.

## Environment Secrets by Name
| Secret Name | Scope | Environments |
|-------------|-------|-------------|
| `GITHUB_APP_ID` | Repo | all |
| `GITHUB_APP_INSTALLATION_ID` | Repo | all |
| `GITHUB_APP_PRIVATE_KEY` | Repo | all |
| `DEEPSEEK_API_KEY` | Repo | production-platform |
| `NSCALE_API_KEY` | Repo | production-platform |
| `CLOUDFLARE_API_TOKEN` | Repo | production-platform |
| `VERCEL_TOKEN` | Repo | production-web, staging-web |
