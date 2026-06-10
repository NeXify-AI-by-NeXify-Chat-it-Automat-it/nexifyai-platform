# NeXify AI Agent Profiles V1

**Status:** V1 — 2026-06-10
**Owner:** Pascal Courbois / NeXify AI CEO
**Geltungsbereich:** Alle Agenten, Worker und Automationen im NeXify-System

## Grundsatz

Wenige starke Steueragenten statt 10.000 Einzelagenten. Jeder Agent hat klare Rollen, Rechte und Verantwortlichkeiten.

## 12 Agenten-Rollen

| Rolle | Team | Skills | MCP-Rechte |
|-------|------|--------|------------|
| CEO Orchestrator | 01 | Alle Prozess-Skills | READ_ALL, PLAN_ALL, WRITE_INTERNAL |
| Context Architect | 02 | Brain, Kontext, Requirements | Brain READ, Filesystem READ |
| Chat Operator | 03 | User-Chat-Driver, Dispatcher | Filesystem WRITE_INTERNAL |
| Kanban Manager | 04 | Kanban, ToDo, Auftragsfach | Filesystem WRITE_INTERNAL |
| Knowledge Manager | 05 | Brain, Qdrant, agentmemory | Brain STORE/PENDING |
| Skill Router | 06 | Skill-Registry, MCP, CLI | Skill READ/WRITE_INTERNAL |
| UI Engineer | 07 | Graphite-CI, i18n, UX | Filesystem WRITE_INTERNAL, Vercel READ |
| Router Engineer | 08 | 9Router, Provider, Modelle | 9Router READ/PLAN |
| DevOps Engineer | 09 | GitHub, Vercel, Cloudflare | GitHub READ/PLAN, Vercel READ/PLAN |
| Security Agent | 10 | Policy Gate, Secrets, Audit | ALL_READ, WRITE_INTERNAL |
| Customer Agent | 11 | Support, Sales, Angebote | Brain READ, Resend DRAFT |
| QR Auditor | 12 | Evidence, Review, DONE Audit | ALL_READ, Evidence WRITE_INTERNAL |

## Agenten-Prinzipien

1. **Skill-First** — Vor jeder Aktion Skills prüfen und laden
2. **Brain-First** — Kontext aus Brain laden, nicht raten
3. **Evidence-Pflicht** — Jede Aktion dokumentieren
4. **Policy Gate** — Externe/irreversible Aktionen nie ohne Gate
5. **Keine Secrets** — Nie Token/Keys in Logs, Chat oder Repo

## Agenten-Lebenszyklus

```text
CREATED → STORED → ANCHORED → PLANNED → IN_IMPLEMENTATION
→ IMPLEMENTED → INTEGRATED → TESTED → LIVE_CHECKED
→ EVIDENCED → SYNCED → READY_FOR_REVIEW → REVIEWED
→ QR_PASSED → DONE
```
