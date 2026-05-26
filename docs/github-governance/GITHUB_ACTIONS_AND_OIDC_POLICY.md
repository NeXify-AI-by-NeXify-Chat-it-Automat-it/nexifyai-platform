# GitHub Actions and OIDC Policy

## Default Permissions
- Default `GITHUB_TOKEN` should be `read-only` at repository level.
- Write permissions are granted **per workflow** via explicit `permissions:` block.
- No workflow may use `permissions: write-all`.
- PR creation/approval via `GITHUB_TOKEN` only allowed with documented policy.

## Required Workflow Patterns
Every workflow must have:
```yaml
permissions:
  contents: read  # minimal starting point
```

Additional permissions are documented by workflow purpose.

## Workflow Approval
- Fork PRs require approval before running workflows.
- No secrets exposed to fork PRs.

## OIDC
- Immutable subject claim: **ENABLED** (target).
- Subject prefix: `repo:NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform`
- OIDC only for explicit trust policies (Vercel, Cloudflare, Supabase if configured).
- No pauschale cloud role grants via OIDC.

## Self-hosted Runners
- **NOT** currently configured.
- GitHub-hosted runners are sufficient for current workload.
- Self-hosted runners require: isolated user, ephemeral mode, strict sandbox, no untrusted PR access.

## Artifact & Log Retention
- Target: **90 days** (org maximum).
- Applied via API or GitHub UI.
