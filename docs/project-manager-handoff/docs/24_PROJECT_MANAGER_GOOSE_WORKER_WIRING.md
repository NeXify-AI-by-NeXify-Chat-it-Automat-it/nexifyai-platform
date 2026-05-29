# Project Manager → Goose Worker Wiring

## Stand: 2026-05-26

### Aktive Services

| Service | Status | Rolle |
|:--------|:-------|:------|
| `nexify-project-manager-api.service` | ✅ Active | **Control Plane API** — Port 8421, verwaltet Tasks, Queue, Skills, Brain-Connect |
| `nexify-brain-api.service` | ✅ Active | **Brain API v3** — Port 8420, Qdrant-Vector-Store, Embeddings, Wissensabfrage |
| `nexify-goose-loop.service` | ✅ Active | **Legacy: Statischer Prompt-Runner** — muss durch Worker ersetzt werden |
| `goose-acp-server.service` | ✅ Active | **Goose ACP Server** — Port 3284, HTTP/WebSocket-Schnittstelle |
| `nexify-embedding-health.service` | ✅ Active | **Embedding Health Monitor** — prüft Embedding-Service alle 300s |
| `goose-ai-brain.service` | ❌ Inactive | **Legacy** — nicht starten, Brain läuft bereits via `nexify-brain-api.service` |

### Architektur: Soll-Zustand

```
GitHub Issue / Project #3 / API Call
        │
        ▼
┌───────────────────────────────┐
│  Project Manager API (8421)   │◄──── POST /tasks
│  - Task Queue                 │
│  - Skill Registry             │
│  - Policy Gate                │
│  - Evidence Store             │
└───────┬───────────────────────┘
        │ GET /tasks/next
        ▼
┌───────────────────────────────┐
│  Goose Worker (systemd)       │──── Task holen → Brain-Kontext laden
│  - nexify-goose-worker.sh     │──── Goose run mit Task-Prompt
│  - Poolt PM API alle 30s      │──── Evidence speichern
│  - Schickt Callback zurück    │──── Brain aktualisieren
└───────────────────────────────┘
        │ POST /worker/callback
        ▼
┌───────────────────────────────┐
│  Project Manager API          │──── Status updaten
│  - Task → completed/failed    │
│  - Evidence persistiert       │
│  - Brain-Update               │
└───────────────────────────────┘
```

### API-Endpunkte (PM Control Plane)

| Methode | Pfad | Beschreibung |
|:--------|:-----|:-------------|
| GET | `/health` | System-Health (Brain, Skills, Tracker) |
| POST | `/tasks` | Neuen Task erstellen (Auth required) |
| GET | `/tasks` | Alle Tasks listen (optional `?status=queued`) |
| **GET** | **`/tasks/next`** | **Nächsten queued Task holen (Worker-Polling)** |
| GET | `/tasks/{id}` | Task-Details abrufen |
| POST | `/tasks/{id}/run` | Task claimen und ausführen |
| **GET** | **`/tasks/{id}/evidence`** | **Evidence eines Tasks abrufen** |
| POST | `/worker/callback` | Worker meldet Ergebnis (Auth required) |
| POST | `/webhooks/github` | GitHub Webhook-Empfang |

### Task Lifecycle

```
queued ──► running ──► completed
              │              │
              ▼              ▼
           failed        needs_review
              │
              ▼
           blocked / rejected
```

### Worker-Integration

Der `nexify-goose-worker.sh` implementiert den Polling-Worker:

1. **GET /tasks/next** — Holt nächsten queued Task
2. **POST /tasks/{id}/run** — Claimt Task (Status → running)
3. **Brain-Kontext laden** — `GET /query?q=...`
4. **Goose run** — Führt Task mit konkretem Prompt aus
5. **Evidence speichern** — Output in `/var/log/nexify-goose/`
6. **POST /worker/callback** — Ergebnis zurück an PM API
7. **Brain Update** — `POST /store` mit Task-Ergebnis

### Systemd-Service-Pairing

**Empfohlene Service-Unit für Worker:**
```ini
[Unit]
Description=NeXify AI PM-Driven Task Worker
After=network-online.target nexify-project-manager-api.service
PartOf=nexify-project-manager-api.service

[Service]
Type=oneshot
User=root
ExecStart=/opt/nexify/goose-runtime/bin/nexify-goose-worker.sh
Environment=PM_API_URL=http://127.0.0.1:8421
Environment=PM_API_TOKEN=pm_local_dev_token
Environment=BRAIN_API_URL=http://127.0.0.1:8420

[Install]
WantedBy=multi-user.target
```

**Timer (alle 30s):**
```ini
[Unit]
Description=Timer for goose worker polling

[Timer]
OnCalendar=*:*:0/30
Unit=nexify-goose-worker.service

[Install]
WantedBy=timers.target
```

### Legacy-Services

| Service | Status | Grund |
|:--------|:-------|:------|
| `goose-ai-brain.service` | Disabled | Legacy — Brain läuft via `nexify-brain-api.service`, Inhalt ist in Qdrant. Kein blindes Reaktivieren. |
| `nexify-goose-loop.service` | Active | Aktuell noch statischer Prompt-Runner. Wird nach Worker-Einführung abgelöst. |

### Warum kein `goose-ai-brain.service`?

- `nexify-brain-api.service` (Port 8420) ist der aktive Brain-Dienst mit Qdrant-Backend
- `goose-ai-brain.service` war ein früherer, nicht vollständig integrierter Service
- Goose nutzt Brain über `brain_mcp_server.py` (läuft im Goose-Prozess) + direkte Brain-API
- Blindes Starten könnte Port-Konflikte oder Daten-Inkonsistenzen verursachen
- Erst sauber analysieren, dann migrieren oder Löschen

### GitHub Project #3 Integration

- Project #3 heißt "Security & Workflow"
- Tasks sollen aus GitHub Issues/Project Items erzeugt werden
- Aktuell noch manuelle Task-Erzeugung via PM API
- Automatisierung: GitHub Webhook → Project #3 Item → PM API Task → Worker → PR/Evidence

### Blocker

1. **Statischer Prompt-Runner** — `nexify-goose-loop.service` pollt nicht die PM API
2. **Kein Task-Timer** — Worker muss per systemd timer alle 30s laufen
3. **Kein GitHub-Project-Watcher** — Tasks werden nicht automatisch aus Issues erzeugt
4. **Legacy `goose-ai-brain.service`** — Muss dokumentiert bleiben, nicht aktivieren
