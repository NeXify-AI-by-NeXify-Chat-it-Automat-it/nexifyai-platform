# NeXify AI Team-System V1

**Status:** V1 — 2026-06-10
**Owner:** Pascal Courbois / NeXify AI CEO
**Geltungsbereich:** Alle NeXify AI Teams und Agenten

## Grundsatz

Wenige starke Teams, klare Rollen, automatische Skill-Zuladung, MCP-/Tool-Rechte und Policy Gate.

## 12 Kernteams

| Team | Name | Verantwortung |
|------|------|---------------|
| 01 | CEO / Orchestration / Strategy | Gesamtführung, Zielzustand, Priorisierung, Tagessteuerung |
| 02 | Context / Requirements / Task Architecture | Kontext laden, Anforderungen zerlegen, Task-Schema erzeugen |
| 03 | Auto / User-Chat / Dispatcher / Sleep-Safe | User-Chat-Driver, Chat Operator, Dispatcher, Automatik |
| 04 | Kanban / ToDo / Auftragsfach | Eingänge erfassen, priorisieren, Tasks erzeugen |
| 05 | Brain / agentmemory / Knowledge | Wissen laden, speichern, konservieren, Pending steuern |
| 06 | Skills / MCP / Tooling | Skills, MCPs, CLIs, Templates, Karpathy-Lessons, Capability-System |
| 07 | Workstation / UI / CI / UX | Graphite-CI, Deutsch, Layoutqualität, Branding, Performance |
| 08 | Router / Models / 9Router | Modelle, Provider, Kosten, Fallbacks, Standardmodell |
| 09 | DevOps / Cloud / Live / GitHub / Deployment | VDS, Cloudflare, Vercel, DNS, GitHub, Rollback |
| 10 | Security / Governance / Compliance | Policy Gate, Security, Secrets, Datenschutz, Risiko |
| 11 | Customer / Sales / Offer / Support | Zielgruppen, Produkte, Angebote, Support, Kundenbindung |
| 12 | Review / QR / Evidence / DONE Audit | Qualitätssicherung, Evidence, Tests, echte Fertigstellung |

## Team-Schalter

Jedes Team hat einen Betriebsmodus:

| Schalter | Bedeutung |
|----------|-----------|
| TEAM_EXECUTION_OFF | Team inaktiv |
| TEAM_EXECUTION_PLAN_ONLY | Nur Planung, keine Ausführung |
| TEAM_EXECUTION_SAFE_INTERNAL | Sichere interne Arbeiten erlaubt |
| TEAM_EXECUTION_REVIEW_REQUIRED | Ergebnisse brauchen Review vor Abschluss |
| TEAM_EXECUTION_BLOCKED | Team durch Blocker gestoppt |

## Regel

Sichere interne Arbeiten sind erlaubt. Produktive, externe, irreversible oder secret-relevante Aktionen bleiben gate-pflichtig.

## Team-Kommunikation

Teams kommunizieren über:
- Kanban/Tasks als operative Wahrheit
- Dispatcher zur Aufgabenverteilung
- Evidence zur Dokumentation
- Brain-Sync für Langzeitwissen
