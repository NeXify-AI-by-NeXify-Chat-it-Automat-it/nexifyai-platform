# GitHub Repository Baseline Matrix

## Repository
`NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform`

## Baseline Version: 1.0 — 2026-05-26

| Area | Current State | Target State | API Changeable | Applied | Blocker | Manual UI Path |
|------|--------------|--------------|----------------|---------|---------|----------------|
| Actions: Default permissions | `read_all` or `write_all` | `read` (minimal) | ✅ | ❌ | Needs verification | Settings → Actions → General → Workflow permissions |
| Actions: Fork PR approval | Unknown | Required | ✅ | ❌ | Needs verification | Settings → Actions → General → Fork pull request workflows |
| Actions: Artifact retention | Unknown | 90 days | ✅ | ❌ | Needs verification | Settings → Actions → General → Artifact and log retention |
| OIDC: Immutable subject | Unknown | Enabled | ✅ | ❌ | Needs check if Trust Policies break | Settings → Actions → General → OIDC token |
| OIDC: Subject prefix | Unknown | `repo:org/repo` | ✅ | ❌ | Needs verification | — |
| Environments: cline-actions | Legacy | Remove/quarantine | ✅ | ❌ | Needs workflow audit | Settings → Environments → cline-actions → Delete |
| Environments: Normalize | 5 environments | 6 standardized | ✅ | ❌ | Needs planning | Settings → Environments → Create |
| Secrets: Actions | Empty | Registry documented | ❌ | ❌ | No PAT/secret values | Settings → Secrets and variables → Actions |
| Secrets: Agents | Empty | Documented (blocked) | ❌ | ❌ | No Copilot license | Settings → Secrets and variables → Codespaces |
| Advanced Security: Push protection | Unknown | Enabled | ✅ | ❌ | Needs verification | Settings → Code security and analysis → Push protection |
| Advanced Security: Alert dismissal | Unknown | Prevent direct dismissals | ✅ | ❌ | Needs verification | Settings → Code security and analysis → Prevent alert dismissal |
| CodeQL: Default setup | Active | Keep with config | ✅ | ❌ | Needs verification | Settings → Code security and analysis → CodeQL |
| Dependabot: Security updates | Unknown | Enabled | ✅ | ❌ | Needs verification | Settings → Code security and analysis → Dependabot |
| Copilot Cloud Agent | Not usable | Read-only proposal | ❌ | ❌ | No license | Settings → Copilot Cloud Agent → MCP |
| MCP Config | Empty | Read-only proposal | ❌ | ❌ | No `COPILOT_MCP_*` secrets | Settings → Copilot Cloud Agent → MCP |
| Custom Properties | None | Defined | ❌ | ❌ | Needs org-level setup | Settings → Custom properties |
| Autolinks | None | Defined | ✅ | ❌ | Needs URL pattern stability | Settings → Autolink references |
| Rulesets | Unknown | Documented | ✅ | ❌ | Needs review | Settings → Rules → Rulesets |
| Branch protection | Unknown | Required checks | ✅ | ❌ | Needs review | Settings → Rules → Rulesets |

## API-Änderbare Einstellungen

Diese können via `gh api` oder GitHub API gesetzt werden. Jede Änderung braucht vorher/nachher Check.
