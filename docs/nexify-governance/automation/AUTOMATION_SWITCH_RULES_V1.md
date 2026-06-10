# Automation Switch Rules V1

**Status:** V1 — 2026-06-10
**Owner:** Team 03 — Auto / User-Chat / Dispatcher / Sleep-Safe
**Geltungsbereich:** Schalterlogik für Automatik, User-Chat-Driver und Sleep-Safe-Autopilot

## Globale Schalter

| Schalter | Wert | Bedeutung |
|----------|------|-----------|
| SYSTEM_MODE | CHAT / ASSISTED / AUTO / SLEEP_SAFE | Gesamtsystem-Modus |
| USER_CHAT_DRIVER | OFF / ON / AUTO_SESSIONS_ONLY / PAUSED / ERROR | User-Chat-Driver |
| AUTOMATION_CONTROLLER | OFF / READY / RUNNING / PAUSED / ERROR | Automation Controller |
| DISPATCHER | OFF / READY / RUNNING / PAUSED / BLOCKED / ERROR | Dispatcher |

## User-Chat-Driver Schalter

| Schalter | Wirkung |
|----------|---------|
| USER_CHAT_DRIVER_OFF | Keine automatischen Fortsetzungen |
| USER_CHAT_DRIVER_ON | Automatische Fortsetzungen in allen berechtigten Sessions |
| USER_CHAT_DRIVER_AUTO_SESSIONS_ONLY | Nur in Sessions mit AUTO_ENABLED-Status |
| USER_CHAT_DRIVER_PAUSED | Vorübergehend angehalten |
| USER_CHAT_DRIVER_ERROR | Fehlerzustand, manuelles Eingreifen nötig |

## Team-Schalter

Siehe Team-System V1 — jedes der 12 Teams hat TEAM_EXECUTION_OFF / PLAN_ONLY / SAFE_INTERNAL / REVIEW_REQUIRED / BLOCKED.

## Automatik-Regeln

1. Automatik nie ohne Policy Gate für externe Aktionen
2. Automatik nie ohne Loop Guard (max 1/3min pro Session, max 5/h)
3. Automatik nie bei BLOCKED_APPROVAL, DONE_TRUE oder OPERATOR_LLM_UNAVAILABLE
4. Automatik immer mit Evidence-Pflicht
5. Automatik immer mit Stop-Button für Pascal
