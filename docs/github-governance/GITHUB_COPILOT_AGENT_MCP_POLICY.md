# GitHub Copilot Agent and MCP Policy

## Current Status
- **Copilot Cloud Agent**: NOT usable — requires Copilot Pro/Business/Enterprise license.
- **MCP Configuration**: Empty (`{ "mcpServers": {} }`).
- **Default MCP**: GitHub and Playwright MCP servers are "default enabled" by GitHub UI, but NOT connected to NeXify Brain/PM API.
- **Agent Secrets**: None configured. Requires `COPILOT_MCP_*` prefix.

## Assessment
1. GitHub Cloud Agent cannot be the primary execution layer without license.
2. PM API + Goose Worker remain the primary execution layer.
3. MCP should be prepared **read-only first** for future GitHub-native agents.
4. NeXify Brain MCP is NOT automatically active — requires explicit integration.

## Target MCP Configuration (Read-only Proposal)
```json
{
  "mcpServers": {
    "github": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```
- Write tools: BLOCKED
- `tools: ["*"]`: FORBIDDEN
- Custom MCP servers: only after Policy Gate approval

## Required Secrets (COPILOT_MCP_* Prefix)
| Secret Name | Purpose | Status |
|-------------|---------|--------|
| `COPILOT_MCP_GITHUB_PAT` | Fine-grained read-only PAT | ❌ Missing |

## Activation Criteria
1. ✅ MCP Security Policy exists (read-only docs)
2. ✅ Tool Allowlist documented
3. ❌ Copilot license available
4. ❌ `COPILOT_MCP_GITHUB_PAT` created and set
5. ❌ MCP config entered in GitHub UI
6. ❌ Test session completed
7. ❌ Tool logs audited
