# GitHub Repository Baseline

## Actions
- **Default permissions**: `read` (target)
- **Fork PR approval**: Required
- **Artifact retention**: 90 days
- **Workflow patterns**: Explizite `permissions:` per Workflow

## OIDC
- **Immutable subject**: Enabled (target)
- **Subject prefix**: `repo:NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform`
- **Cloud providers**: Vercel, Supabase, Cloudflare (check trust policies first)

## Runners
- **Self-hosted**: NOT configured (GitHub-hosted sufficient)
- **VDS-Goose is NOT a GitHub Actions runner**

## Environments
| Environment | Status |
|-------------|--------|
| `cline-actions` | LEGACY — remove |
| `Production – web` | Normalize to `production-web` |
| `Production – frontend` | Normalize to `production-frontend` |
| `Production – nexifyai-platform` | Normalize to `production-platform` |
| `production` | Normalize to `staging-platform` or deprecate |
| `security-review` | Create |

## Secrets
- **Actions Secrets**: EMPTY (P0 gap)
- **Environment Secrets**: EMPTY
- **Agents Secrets**: EMPTY (Copilot license required)
- **Codespaces Secrets**: EMPTY
- **Dependabot Secrets**: EMPTY
- **Central Registry**: Partially documented in `docs/project-manager/SECRET_REGISTRY_POLICY.md`

## Advanced Security
- **Push protection**: Target ENABLED
- **Alert dismissal prevention**: Target ENABLED
- **Secret scanning**: ON (standard patterns)
- **Custom patterns**: To be defined
- **CodeQL**: Default setup active, config exists
- **Dependabot**: Alerts ON, security updates target ON
- **Private vulnerability reporting**: Target ENABLED

## Code Quality
- **JavaScript/TypeScript**: Active
- **Python**: Active
- **Actions**: Active
- **Query suite**: security-and-quality + security-extended
- **Schedule**: Push main, PR main, weekly

## Copilot / MCP
- **Cloud Agent**: NOT usable (no license)
- **MCP Config**: EMPTY
- **Default MCP**: GitHub + Playwright (no NeXify Brain integration)
- **Agents Secrets**: EMPTY

## Custom Properties
- **Status**: NOT configured (org-level)
- **Recommended**: platform_area, data_sensitivity, runtime_class, etc.

## Autolinks
- **Status**: NOT configured
- **Decision**: Wait for stable URL patterns

## Rulesets / Auto-Merge
- **Status**: Needs review
- **Agent/Auto-merge**: Policy required before enabling
