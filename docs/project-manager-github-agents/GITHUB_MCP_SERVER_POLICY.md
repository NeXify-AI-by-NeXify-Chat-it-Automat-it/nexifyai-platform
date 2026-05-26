# GitHub MCP Server Policy

## Entscheidungsmatrix

| Kriterium | Built-in Remote MCP | Local Docker MCP |
|:----------|:-------------------|:-----------------|
| Authentifizierung | OAuth (kein PAT) | PAT erforderlich |
| Toolset | Eingeschränkt (GitHub-Native) | Vollständig |
| Setup | Nur URL eintragen | Docker + PAT |
| Wartung | Keine | Docker-Updates |
| Sicherheit | OAuth-geschützt | PAT-Abhängig |
| Read-only Tools | Nur read | Read + Write |

## Entscheidung

**Phase 1: Built-in Remote MCP bevorzugen**

Begründung:
- Kein PAT benötigt
- Keine zusätzliche Runtime
- OAuth-Schutz
- Read-only ausreichend für Context-Erfassung
- GitHub betreibt den Server

**Phase 2: Local MCP nur wenn Built-in nicht ausreicht**

Begründung:
- Built-in hat kein `searchCode` über Repo-Grenzen
- Built-in hat kein `getWorkflowRun` Details
- Falls diese Features nötig sind: Local Docker MCP mit fine-grained PAT

## Read-only Tool Allowlist (Local MCP)

```json
{
  "tools": [
    "getIssue", "searchIssues", "listIssues",
    "getPullRequest", "listPullRequests",
    "getRepository", "searchCode", "listFiles",
    "getFileContents", "getBranch", "listBranches",
    "listCommits", "getCommit",
    "getWorkflowRun", "listWorkflowRuns",
    "searchUsers", "getUser",
    "listProjects", "getProject"
  ]
}
```

## Write-Tools Blocklist (alle Phasen)

```json
{
  "blocked_tools": [
    "createIssue", "updateIssue", "closeIssue",
    "createPullRequest", "updatePullRequest", "mergePullRequest",
    "createRepository", "deleteRepository",
    "createWorkflowRun", "cancelWorkflowRun",
    "createBranch", "deleteBranch",
    "pushFiles", "createCommit", "updateRef"
  ]
}
```
