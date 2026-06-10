# Brain-Sync-Entscheidung — V1 Governance-Paket

**Datum:** 2026-06-10
**Status:** PENDING — noch nicht in Brain geschrieben
**Grund:** Brain/Qdrant aktuell nicht als Online-Service erreichbar (Embedding-JWT invalid). Entscheidung: STORE_SUMMARY bei nächster Brain-Sync-Gelegenheit.

## STORE (bei Brain-Sync)

Folgende Erkenntnisse sollen in Brain Kategorie `governance/system_architecture/v1` gespeichert werden:

1. **NeXify AI Gesamtbetrieb V1** — 12 Teams, Automation Controller, Dispatcher, Kanban, Evidence
2. **ADR Workstation/Automation** — Legacy-Governance übersteuert; Workstation + Hermes + CEO Orchestrator sind primär
3. **Policy-Gate-System** — 6 Policy-Levels (READ_ONLY bis FORBIDDEN), alle externen Writes gate-pflichtig
4. **DONE-Definition** — 16-Punkte-Checkliste, PARTIAL_DONE ≠ DONE
5. **Skill-Routing** — Prozess-Skills vor Implementation-Skills, MCP-Rechte-Matrix
6. **Dispatcher** — 10 Pflichtfelder, 10 Queues, Gate-pflichtige Aktionen
7. **Archivierte Files** — 10 Governance-Dokumente unter docs/nexify-governance/

## DO_NOT_STORE

- Details zu einzelnen Dateipfaden (sind im Repo)
- Session-spezifische Tool-Ausgaben
- Temporäre Statuswerte

## Agentmemory-Update

Episodischer Eintrag: "2026-06-10: V1 Governance-Paket mit 10 Dokumenten in docs/nexify-governance/ erstellt. ADR für Legacy-Übersteuerung geschrieben. GitHub-Push blockiert (gh CLI fehlt). Nächster Schritt: Pascal-Freigabe für Push einholen."

