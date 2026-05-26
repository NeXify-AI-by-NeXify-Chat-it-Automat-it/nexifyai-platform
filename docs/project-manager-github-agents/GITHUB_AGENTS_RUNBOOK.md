# GitHub Agents Runbook

## Übersicht

GitHub Copilot Cloud Agent ermöglicht AI-gestützte Code-Interaktion direkt im Browser. Agenten können MCP-Server nutzen, um mit externen Tools und Datenquellen zu interagieren.

## Aktueller Status

| Aspekt | Status |
|:-------|:-------|
| GitHub Cloud Agent Sessions | ❌ Keine aktiven Sessions |
| MCP Konfiguration | ❌ Leer (leeres `mcpServers` Objekt) |
| Built-in GitHub MCP verfügbar | ✅ Ja (via api.githubcopilot.com/mcp) |
| PM-driven Goose Worker | ✅ Aktiv (task-driven, queue-basiert) |
| Brain MCP Integration | ✅ Aktiv (Brain API Port 8420) |

## Warum aktuell keine aktiven Agent Sessions?

1. **MCP-Konfiguration ist leer** — Agent hat keine Tools
2. **Keine `COPILOT_MCP_*` Secrets gesetzt** — Fehlende PAT für Local MCP Server
3. **Kein testbarer Use-Case definiert** — Kein Issue/Project Item als erster Agent-Task
4. **Governance-first** — Erst Policy, dann Konfiguration, dann Session

## Activation Plan

### Schritt 1: Secrets bereitstellen (Blocked by Issue #46)
```bash
# Benötigt: Fine-grained PAT mit read-only Zugriff auf 1 Repo
# Name: COPILOT_MCP_GITHUB_PAT
# Scope: Repo-Inhalt lesen, Issues lesen, PRs lesen
```

### Schritt 2: MCP Config eintragen (GitHub UI)
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

### Schritt 3: Test-Session starten
- Issue #42 lesen
- Brain-Status prüfen
- Code-Durchsicht für Alert #42
- Ergebnis dokumentieren

### Schritt 4: Schrittweise Write-Tools
Nach Freigabe durch Policy Gate:
- Issue erstellen/aktualisieren
- PR erstellen
- Branch erstellen

## Blockers

1. **Issue #46** — Secrets nicht verfügbar
2. **Issue #49** — Webhook-Endpoint fehlt
3. **Kein PAT** — Fine-grained PAT nicht erstellt
