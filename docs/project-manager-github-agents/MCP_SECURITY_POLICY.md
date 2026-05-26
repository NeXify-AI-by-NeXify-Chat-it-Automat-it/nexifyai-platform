# MCP Security Policy

## Prinzipien

1. **Read-only first** — Kein MCP-Server bekommt write-Tools bevor ein Policy Gate und Tool-MCP-Gateway stehen.
2. **Minimales Toolset** — Nur die Tools freigeben, die für die aktuelle Aufgabe nötig sind.
3. **Kein `tools: ["*"]`** — Pauschale Freigabe verboten.
4. **COPILOT_MCP_-Prefix** — Alle MCP-Secrets müssen mit `COPILOT_MCP_` beginnen.
5. **Fine-grained PAT** — Wenn PAT nötig, dann fine-grained, auf 1 Repo limitiert, read-only.
6. **Built-in bevorzugen** — GitHub Built-in Remote MCP Server (OAuth) vor Local/SSE.
7. **Keine Login-Secrets** — Playwright MCP darf keine Secrets-Datei mit Login-Daten erhalten.

## Erlaubte Tools (Phase 1 — Read-only)

### Built-in GitHub MCP (Remote)
- `searchCode`, `getFileContents`
- `searchIssues`, `getIssue`, `listIssues`
- `searchPullRequests`, `getPullRequest`, `listPullRequests`
- `getRepository`, `listFiles`
- `listWorkflowRuns`, `getWorkflowRun`

### Local GitHub MCP Server (Phase 2, optional)
Gleiches Set wie Built-in +:
- `searchUsers` (read-only)
- `getCommit`, `listCommits` (read-only)
- `getBranch`, `listBranches` (read-only)

## Verbotene Tools (Alle Phasen)

### Unabhängig vom Server
- `createIssue`, `updateIssue`, `closeIssue`
- `createPullRequest`, `mergePullRequest`, `updatePullRequest`
- `createRepository`, `deleteRepository`, `transferRepository`
- `createWorkflowRun`, `cancelWorkflowRun`, `reRunWorkflow`
- `createBranch`, `deleteBranch`, `createCommit`
- `pushFiles`, `createOrUpdateFile`, `deleteFile`

## Richtlinien für neue MCP-Server

Jeder neue MCP-Server benötigt:
1. **Security Review** — Issue im Repo
2. **Tool-Allowlist** — Explizit dokumentiert
3. **Secret-Plan** — Welche Secrets, wo gespeichert
4. **Rollback-Plan** — Wie deaktivieren
5. **Test-Session** — Read-only Test vor Write-Freigabe

## Sanktionen

- `tools: ["*"]` für write-fähige Server = P0-Incident
- Secrets im MCP-Config-JSON = P0-Incident
- PAT mit Org-Weit write = P0-Incident
