# MCP Configuration Proposal — GitHub Cloud Agent

## Ziel

Read-only-first MCP-Integration für GitHub Copilot Cloud Agent, später schrittweise write-Tools nach Policy-Freigabe.

## Ausgangslage

- GitHub Cloud Agent Tab in Repo-Settings zeigt leere MCP-Konfiguration
- Keine aktiven Agent-Sessions
- PM-driven Goose Worker läuft task-driven über Control Plane (Port 8421)
- Brain API (Port 8420) als zentrale Retrieval- und Memory-Einheit

## Vorgeschlagene MCP-Konfiguration

### Phase 1: Read-only (sofort umsetzbar)

```json
{
  "mcpServers": {
    "github-builtin": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

GitHub bietet einen Built-in Remote MCP Server unter `https://api.githubcopilot.com/mcp/`, der OAuth verwendet. Kein PAT nötig. Toolset ist auf GitHub-interne Aktionen beschränkt (Issues lesen, PRs lesen, Code durchsuchen).

### Phase 2: Local GitHub MCP Server (optional, nach Policy-Prüfung)

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=${COPILOT_MCP_GITHUB_PAT}",
        "ghcr.io/github/github-mcp-server"
      ]
    }
  }
}
```

**Nicht aktivieren bevor:**
- COPILOT_MCP_GITHUB_PAT als fine-grained PAT mit read-only Berechtigung existiert
- Tool-Allowlist erstellt ist
- Policy Gate zustimmt

### Phase 3: Playwright MCP Evidence Runner (Optionsphase)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--sandbox",
        "--isolated"
      ]
    }
  }
}
```

**Nicht aktivieren bevor:**
- Browser-Sandbox konfiguriert
- Keine Login-Secrets verwendbar
- Nur für Evidence/Screenshots/Audits

## Secrets

GitHub verlangt `COPILOT_MCP_`-Prefix für Agent Secrets:

| Secret Name | Typ | Scope | Status |
|:------------|:----|:------|:-------|
| `COPILOT_MCP_GITHUB_PAT` | Secret | Fine-grained PAT, read-only | ❌ Fehlt |
| `COPILOT_MCP_PLAYWRIGHT_CONFIG` | Variable | JSON-Konfiguration | ❌ Fehlt |

## Tool-Allowlist (Read-only Phase)

Erlaubte Built-in Tools:
- `getIssue`, `searchIssues`, `listIssues`
- `getPullRequest`, `listPullRequests`, `searchPullRequests`
- `getRepository`, `searchCode`
- `listFiles`, `getFileContents`
- `getWorkflowRun`, `listWorkflowRuns`

Verboten (write):
- `createIssue`, `updateIssue`, `closeIssue`, `reopenIssue`
- `createPullRequest`, `updatePullRequest`, `mergePullRequest`
- `createRepository`, `deleteRepository`
- `createWorkflowRun`, `cancelWorkflowRun`
- `createBranch`, `deleteBranch`
- `createCommit`, `pushFiles`

## Risiken

| Risiko | Maßnahme |
|:-------|:---------|
| Autonome Write-Aktionen | Keine write-Tools freigegeben |
| Datenexfiltration | Read-only, keine write-Endpoints |
| Secret-Leakage | Nur COPILOT_MCP_-Prefix Secrets, keine systemd Secrets |
| Token-Missbrauch | Fine-grained PAT auf 1 Repo limitiert |
| Browser-Exploit | Playwright --sandbox + --isolated + --headless |

## Nächste Schritte

1. ✅ Docs erstellt
2. ❌ PAT erstellen (fine-grained, read-only, 1 Repo)
3. ❌ Secret im Agent UI setzen
4. ❌ MCP Config in GitHub UI eintragen
5. ❌ Test-Session starten
6. ❌ Tool-Logs prüfen
7. ❌ Schrittweise write-Tools nach Policy

## Rollback

1. MCP Config in GitHub UI leeren
2. PAT widerrufen
3. Agent Session beenden
