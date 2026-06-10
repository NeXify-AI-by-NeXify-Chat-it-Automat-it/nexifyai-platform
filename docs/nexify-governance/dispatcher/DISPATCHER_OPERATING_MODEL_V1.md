# Dispatcher Operating Model V1

**Status:** V1 — 2026-06-10
**Owner:** Team 03 — Auto / User-Chat / Dispatcher / Sleep-Safe
**Geltungsbereich:** Aufgabenverteilung im NeXify-AI-System

## Zweck

Der Dispatcher verteilt Aufgaben aus dem Automation Controller an die richtigen Teams, Agenten, Skills und Tools. Er ist die zentrale Verteilungsinstanz.

## Dispatcher-Pflichtfelder

Jede Task im Dispatcher hat:

| Feld | Beschreibung |
|------|--------------|
| task_id | Eindeutige ID (NX-P0-NNN) |
| source | Herkunft (Chat/ToDo/Auftragsfach/Automatik) |
| priority | P0/P1/P2 |
| team | Zugeordnetes Team (01-12) |
| owner_role | Konkrete Rolle/Agent |
| policy_level | READ_ONLY / PLAN_ONLY / WRITE_INTERNAL / WRITE_PROJECT / ADMIN_APPROVAL / FORBIDDEN |
| skills_required | Benötigte Skills |
| mcp_required | Benötigte MCPs |
| tools_required | Benötigte Tools/CLIs |
| cli_required | Benötigte Command-Line-Tools |
| allowed_actions | Erlaubte Aktionen |
| forbidden_actions | Verbotene Aktionen |
| evidence_path | Pfad zur Evidence-Dokumentation |
| next_action | Nächster geplanter Schritt |
| completion_state | Status im Fertigstellungsmodell |

## Dispatcher Pipeline

```text
Task empfangen
→ Policy Level prüfen
→ Team zuordnen
→ Skills/MCPs/Tools prüfen
→ Expert Planner delegieren
→ Worker Execution starten
→ Ergebnis prüfen
→ Evidence anfordern
→ Kanban aktualisieren
→ Folgeaufträge prüfen
→ Abschluss melden
```

## Gate-pflichtige Aktionen (Dispatcher blockiert)

- Git Push/Merge
- Deployment (Vercel/Cloudflare)
- DNS-Änderungen
- Supabase produktiv
- Kundennachrichten
- E-Mail-Versand
- SimpleX-Outbound
- Secret-Änderung
- Irreversible Löschung

Diese werden in Queue `waiting_for_approval` abgelegt und nicht automatisch ausgeführt.
