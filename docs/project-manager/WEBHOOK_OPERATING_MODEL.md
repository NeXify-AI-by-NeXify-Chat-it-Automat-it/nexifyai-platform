# Webhook Operating Model

## Status
- **Webhook Endpoint**: ✅ Live — `https://webhook.nexifyai.cloud/webhooks/github`
- **GitHub Hook**: ✅ Repository Webhook #631147476 — active (9 events)
- **HMAC Secret**: ✅ Gesetzt via systemd override (Issue #68)
- **PM API Processing**: ✅ Alle POSTs answered 200
- **Event → Task Mapping**: ❌ Fehlt (Issue #66)

## Events aktiv

| Event | Status | PM API Processing |
|:------|:-------|:------------------|
| `issues` | ✅ | Received & verified |
| `issue_comment` | ✅ | Received & verified |
| `pull_request` | ✅ | Received & verified |
| `pull_request_review` | ✅ | Received & verified |
| `pull_request_review_comment` | ✅ | Received & verified |
| `check_run` | ✅ | Received & verified |
| `check_suite` | ✅ | Received & verified |
| `workflow_run` | ✅ | Received & verified |
| `code_scanning_alert` | ✅ | Received & verified |

## Webhook Secret Management

- **Secret Name (Env)**: `GITHUB_WEBHOOK_SECRET`
- **Storage**:
  - `systemd override.conf` auf VDS
  - Kein Leak in Logs, GitHub, Brain
- **Rotation Policy**: Jährlich oder nach Incident
- **Consumer**: `services/project-manager-api/app/github_client.py`

## Event → Task Pipeline (TODO)

Der Task-Generator muss GitHub Events in PM API Tasks konvertieren:

1. GitHub Event → Webhook → PM API
2. Event-Typ klassifizieren (issue/PR/alert)
3. Task erstellen mit `POST /tasks`
4. Worker holt Task via `GET /tasks/next`
5. Evidence schreiben
6. Issue/PR/Brain aktualisieren

Blockiert durch: Issue #66, fehlender Task-Generator.
