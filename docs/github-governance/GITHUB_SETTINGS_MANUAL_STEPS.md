# GitHub Settings — Manual Steps (Not API Changeable)

These settings CANNOT be changed via GitHub API. They require manual UI navigation.

## 1. Custom Properties (Org-Level)

**Path**: GitHub.com → Organization Settings → Custom properties
**Values**: See `GITHUB_CUSTOM_PROPERTIES_AND_AUTOLINKS.md`

## 2. Copilot Cloud Agent / MCP Config

**Path**: Repository Settings → Copilot Cloud Agent → MCP configuration
**Action**: Enter read-only MCP config JSON (see `GITHUB_COPILOT_AGENT_MCP_POLICY.md`)

## 3. Actions Repository Secrets

**Path**: Repository Settings → Secrets and variables → Actions
**Action**: Add secrets per `GITHUB_SECRETS_AND_ENVIRONMENTS_POLICY.md`

## 4. Environment Secrets

**Path**: Repository Settings → Environments → [environment] → Add secret
**Action**: Per environment as documented

## 5. Agents Secrets (Copilot)

**Path**: Repository Settings → Secrets and variables → Agents
**Action**: Add `COPILOT_MCP_GITHUB_PAT` when available

## 6. Dependabot Secrets

**Path**: Repository Settings → Secrets and variables → Dependabot
**Action**: Add secrets per policy

## 7. Codespaces Secrets

**Path**: Repository Settings → Secrets and variables → Codespaces
**Action**: Add secrets per policy

## 8. Environments Structure

**Path**: Repository Settings → Environments
**Actions**:
- Create: `production-platform`, `production-web`, `production-frontend`, `staging-platform`, `staging-web`, `security-review`
- Set required reviewers, branch restrictions, wait timers
- Delete/rename: `cline-actions` (legacy), normalize production environments

## 9. Autolink References

**Path**: Repository Settings → Autolink references
**Note**: DO NOT create until URL patterns are stable.

## 10. Branch Protection / Rulesets

**Path**: Repository Settings → Rules → Rulesets
**Action**: Review and align with governance baseline.
