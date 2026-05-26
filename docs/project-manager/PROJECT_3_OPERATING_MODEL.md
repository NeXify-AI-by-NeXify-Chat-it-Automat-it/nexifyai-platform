# NeXify AI — System Activation 2026-05-26

## Project #3 Operating Model

### Aktueller Status

| Aspekt | Status | Blocker |
|:-------|:-------|:--------|
| Project #3 (Security & Workflow) | ✅ Aktiv | — |
| API-Zugriff über gh | ❌ Nicht möglich | Org-Scope fehlt im GH Token |
| Items erstellen/aktualisieren via API | ❌ Nicht geprüft | Fehlende Scope |
| Issues #42, #49 im Project | ❌ Nicht bestätigt | — |

### Workaround

Solange API-Zugriff nicht möglich: Issues manuell über `gh issue create` anlegen.
Project-Zuordnung via GitHub UI.

### Ziel

Sobald Token-Scope erweitert: Automatische Task-Erzeugung aus:
- GitHub Issues → PM API Tasks
- GitHub Project Items → PM API Tasks
- Code scanning Alerts → PM API Tasks
- Dependabot Alerts → PM API Tasks

## Task Queue Contract

### Queue-Endpunkte

| Endpoint | Methode | Beschreibung |
|:---------|:--------|:-------------|
| `/tasks` | POST | Neuen Task erstellen |
| `/tasks` | GET | Alle Tasks listen |
| `/tasks/next` | GET | Nächsten queued Task (Worker-Poll) |
| `/tasks/{id}` | GET | Task-Details |
| `/tasks/{id}/run` | POST | Task claimen & ausführen |
| `/tasks/{id}/evidence` | GET | Evidence abrufen |
| `/worker/callback` | POST | Worker-Ergebnis |

### Task States

```
queued → running → completed
              ↓
           failed
```

## Evidence Contract

Jeder Task muss Evidence produzieren:
1. **Worker-Output** → `/var/log/nexify-goose/evidence_{task_id}.txt`
2. **PR/Issue-Update** → GitHub
3. **Brain-Update** → `POST /store` (Brain API)

## Brain MCP Contract

Brain MCP dient als zentrale Context- und Memory-Einheit:
- **Categories**: governance, system_state, security, architecture, docs
- **Query**: `GET /query?q=...` — Semantische Suche
- **Store**: `POST /store` — Wissen speichern
- **Health**: `GET /health` — Statusprüfung

## Security Alert Operating Model

1. Code scanning Alert → Issue (label: code-scanning, security)
2. Issue → Project #3 Item
3. PM API Task aus Issue
4. Worker führt Task aus
5. PR erstellt
6. Evidence im Issue + Project + Brain

## PR Automerge Policy

- Nur PRs aus PM-driven Tasks
- CodeQL muss grün
- Trivy muss grün
- Kein direkter Push auf main
- Merge nur via `gh pr merge --auto --squash`
- Ruleset: `Changes must be made through a pull request`
