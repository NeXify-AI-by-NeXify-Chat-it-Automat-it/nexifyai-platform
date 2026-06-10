# Automation Controller V1

**Status:** V1 — 2026-06-10
**Owner:** Team 03 — Auto / User-Chat / Dispatcher / Sleep-Safe
**Geltungsbereich:** Alle Automationen im NeXify-System

## Pflichtarchitektur

```text
Input / Chat / ToDo / Auftragsfach / Evidence / Kanban
→ Automation Controller
→ Policy Gate
→ Task Generator
→ Skill Router
→ MCP/Tool Permission Layer
→ Dispatcher
→ Expert Planner
→ Worker Execution
→ Review / QR / Evidence
→ Brain + agentmemory Sync
→ Kanban / Workspace Update
→ Follow-up / Self-Optimization
```

## Statuswerte

| Status | Bedeutung |
|--------|-----------|
| CHAT_MODE | Nur Chat, keine Automatik |
| ASSISTED_MODE | Chat mit assistierten Tools |
| AUTO_READY | Automatik bereit, aber nicht aktiv |
| AUTO_RUNNING | Automatik aktiv |
| AUTO_PAUSED | Automatik pausiert |
| AUTO_BLOCKED | Automatik durch Blocker gestoppt |
| AUTO_REVIEW_REQUIRED | Ergebnis braucht Review |
| AUTO_COMPLETED | Automatik erfolgreich abgeschlossen |
| AUTO_ERROR | Automatik mit Fehler beendet |
| SLEEP_SAFE_AUTOPILOT | Schlafmodus mit kontrollierten Fortsetzungen |

## Queues

| Queue | Priorität | Beschreibung |
|-------|-----------|--------------|
| p0_now | Sofort | Kritische Tasks |
| p1_today | Heute | Wichtige Tasks |
| p2_next_72h | 72h | Geplante Tasks |
| safe_internal_work | Laufend | Interne Writes ohne Gate |
| waiting_for_approval | Blockiert | Wartet auf Pascal-Freigabe |
| blocked_access | Blockiert | Zugriff nicht verfügbar |
| evidence_pending | Rückstand | Evidence muss erstellt werden |
| review_required | Rückstand | Qualitätsprüfung ausstehend |
| followups_generated | Rückstand | Folgeaufträge erzeugt |
| done_audit | Archiv | Abgeschlossene, geprüfte Tasks |

## Automatik-Button

Schalter zwischen CHAT_MODE und vollständiger Automatik. Nur über kontrollierte Architektur aktivierbar. Nie freier Loop.
