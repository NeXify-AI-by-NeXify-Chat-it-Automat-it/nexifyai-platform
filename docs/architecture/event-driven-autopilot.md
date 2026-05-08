# Event-getriebene Autopilot-Architektur

**Status:** Konzept (Roadmap) | **Datum:** 08.05.2026 | **Version:** 1.0

## Vision

Statt periodischem Polling der Task-Queue via Cron-Job (`*/5 * * * *`) wird das System auf eine **Event-getriebene Architektur** umgestellt:

> GitHub Actions senden ein `workflow_completed`-Event an eine Hermes-API.
> Hermes prüft daraufhin die Queue und reagiert nur dann.
> **Kein Polling mehr.**

Diese Architektur spart Container-Memory, CPU-Zyklen und verhindert dass der Agent im Hintergrund endlos pollt, obwohl keine Tasks anstehen.

## IST-Zustand (Polling-basiert)

```
Cron (alle 5 Min) → Hermes startet Skill cli-task-worker
  → psql: SELECT ... WHERE status='waiting'
  → Wenn Task: bearbeiten
  → Wenn kein Task: idle-Spin (10s × 5 Zyklen), dann exit
```

**Nachteile:**
- 288 Cron-Runs pro Tag, davon >95% Leerläufe
- Jeder Run kostet Model-Inferenz (auch bei leerer Queue)
- Container-CPU-Last durch ständiges Polling
- Max 5-Minuten-Latenz zwischen Event und Reaktion

## SOLL-Zustand (Event-getrieben)

```
GitHub Workflow abgeschlossen
  → POST /api/agent/trigger (Webhook)
    → Hermes-API validiert Payload
      → Skill event-driven-worker startet
        → Queue prüfen und abarbeiten
        → HTTP 200 OK mit Job-Status
```

**Vorteile:**
- Keine Leerläufe mehr → 95% weniger Cron-Runs
- Sofortige Reaktion (< 1s) statt bis zu 5 Min Latenz
- Ressourcen nur bei Bedarf aktiv
- Skalierbar: Webhook kann von beliebigen Quellen kommen

## Umsetzungsschritte

### Schritt 1: Hermes-API-Endpunkt implementieren

```python
# endpoint: POST /api/agent/trigger
# payload: { "event": "workflow_completed", "workflow": "ci.yml", "status": "success" }
# response: { "accepted": true, "task_count": 3, "tasks_processed": 3 }

@router.post("/api/agent/trigger")
async def trigger_agent(payload: AgentTriggerPayload):
    # 1. Payload validieren (Signatur, Quelle)
    # 2. Skill event-driven-worker laden
    # 3. Task-Queue abarbeiten
    # 4. Ergebnis zurückgeben
    ...
```

### Schritt 2: GitHub Repository Webhook konfigurieren

In GitHub Repository Settings → Webhooks:

| Feld | Wert |
|------|------|
| Payload URL | `https://srv1243952.hstgr.cloud/api/agent/trigger` |
| Content type | `application/json` |
| Secret | (generiert, in Hermes .env als `WEBHOOK_SECRET`) |
| Events | **Workflow runs** (nicht "Just the push event") |
| Active | ✅ |

### Schritt 3: Skill `event-driven-worker` erstellen

Minimaler Skill, der nur bei Aufruf die Queue abarbeitet:

```yaml
name: event-driven-worker
mode: on-demand  # KEIN continuous loop
trigger: webhook  # Wird nur via /api/agent/trigger aufgerufen
```

Der Worker:
1. Holt alle `waiting`-Tasks aus Supabase
2. Arbeitet sie sequentiell ab (max 5 pro Trigger)
3. Markiert `done` oder `failed`
4. Schreibt Summary-Log

### Schritt 4: Alte Cron-Jobs deaktivieren

**Phase 1 (Parallelbetrieb):**
- Cron `048e2cd0a6f6` (CLI-Autopilot) **pausieren**, nicht löschen
- Webhook 1 Woche parallel testen
- Logs vergleichen: Werden alle Tasks verarbeitet?

**Phase 2 (Cut-over):**
- Webhook bestätigt stabil → Cron deaktivieren
- `463459445ea8` (Badge Report) auf Webhook umstellen

**Phase 3 (Archiv):**
- Alte Polling-Skripte endgültig entfernen
- Health-Dashboard um "Event-Driven" Status erweitern

## Architektur-Diagramm

```
┌─────────────┐     workflow_completed      ┌───────────────┐
│  GitHub     │ ──────────────────────────► │  Hermes API   │
│  Actions    │    POST /api/agent/trigger  │  (Traefik)    │
└─────────────┘                             └───────┬───────┘
                                                    │
                                          ┌─────────▼─────────┐
                                          │  event-driven-    │
                                          │  worker Skill     │
                                          └─────────┬─────────┘
                                                    │
                                          ┌─────────▼─────────┐
                                          │  Supabase Queue   │
                                          │  (tasks Tabelle)  │
                                          └───────────────────┘
```

## Sicherheit

- **Webhook Secret:** HMAC-SHA256 Signatur-Prüfung
- **IP-Whitelist:** Nur GitHub Webhook IPs (`140.82.112.0/20`)
- **Rate-Limit:** Max 10 Trigger/Minute pro Quelle
- **Audit-Log:** Jeder Trigger wird mit Payload + Ergebnis geloggt

## Meilensteine

| Meilenstein | Status | Ziel |
|-------------|--------|------|
| API-Endpoint implementiert | 📋 Geplant | Q2 2026 |
| GitHub Webhook konfiguriert | 📋 Geplant | Q2 2026 |
| event-driven-worker Skill | 📋 Geplant | Q2 2026 |
| Parallelbetrieb (Cron + Webhook) | 📋 Geplant | 1 Woche Test |
| Cron deaktiviert | 📋 Geplant | Nach erfolgreichem Test |
| Health-Dashboard Update | 📋 Geplant | Q3 2026 |

## Offene Fragen

1. **Auth:** Soll der Webhook-Endpoint JWT-Auth nutzen oder reicht Webhook-Secret?
2. **Retry:** Was passiert wenn Hermes-API down ist? GitHub retried automatisch (bis 72h).
3. **Mehrere Quellen:** Sollen auch Vercel-Deploy-Webhooks den Autopiloten triggern?
4. **Priority:** Wie werden Tasks priorisiert wenn mehrere Events gleichzeitig eintreffen?

---

*Dieses Dokument ist eine Roadmap — keine sofortige Umsetzung.*
*Erstellt im Rahmen des CLI-Autopilot-Finalisierungsauftrags am 08.05.2026.*
