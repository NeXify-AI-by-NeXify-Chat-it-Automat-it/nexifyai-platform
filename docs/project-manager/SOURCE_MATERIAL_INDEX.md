# Source Material Index

**Version:** 1.0  
**Stand:** 2026-05-25  
**Status:** active_managed  
**Owner:** Project Manager

---

## Zweck

Dieser Index dokumentiert, welche externen Quellen als Architekturvorgabe für das NeXify Project-Manager-Handoff und die interne Project Manager Control Plane gelten.

## Verbindliche Kernaussagen

Die folgenden Aussagen stammen aus den hochgeladenen ChatGPT-/Projektplanungsunterlagen und gelten als Architekturquelle für alle weiteren Entscheidungen:

### Governance-first
- Aktuelles Hauptproblem ist Governance, nicht Entwicklung.
- Keine Feature-Arbeit vor vollständiger Plattforminventarisierung.
- GitHub ist Source of Truth.
- `nexifyai-platform` ist das zentrale Monorepo/Gesamtsystem.
- Kundenprojekte dürfen nicht im Plattform-Core vermischt bleiben.

### Core-Systeme
- Brain/Qdrant/9Router sind reale Core-Systeme und dürfen nicht gefährdet werden.
- Cline ist Dead Legacy.
- Goose ist Primärintelligenz.
- Lokale Fake-Skills sind verboten.
- `claude-code-templates` ist Master-Skill-System.

### Wissensschichten
- Brain bleibt Governance-/Langzeitwissen.
- `agentmemory` ist nur operative Memory-Ergänzung, kein Brain-Ersatz.
- Temporal ist spätere Durable-Execution-Schicht.
- Huginn ist spätere Event-/Automation-Schicht, kein Brain-Ersatz.

### Browser-Tests
- Webwright ist geplanter Browser-Evidence-Runner, nicht produktiv installiert.

### Business-first
- Agenturseite, Leadstrecke, KI-Berater, Angebot, Kundenprojekte, Security/CI haben Priorität vor neuem Portal.
- Neues Portal kommt später.

### Zielarchitektur (später)
- Brain + agentmemory + Temporal + Huginn + Tool-MCP + GitHub App + Vercel/Supabase/GitHub Expert Agents.

## Quellen

| Quelle | Typ | Datum | Status |
|--------|-----|-------|--------|
| ChatGPT-Projektplanungsunterlagen (hochgeladen) | Architekturvorgabe | 2026-05-25 | active_managed |
| PR #17 — Project Manager Handoff Package | GitHub Commit | 2026-05-25 | active_managed |
| PR #18 — Project Manager Handoff Cleanup | GitHub Commit | 2026-05-25 | active_managed |
| Anton-Goose-Bridge Artefakte (Server) | Quarantänisiert | 2026-05-25 | quarantined |

## Status-Zusammenfassung

- ✅ Governance-Foundation im Repo (22 Docs, 7 JSON-Schemas, 5 Prompts, 4 Templates)
- ✅ Resource Lifecycle Policy aktiv
- ✅ GitHub Source of Truth bestätigt
- ✅ Business-first Priorität dokumentiert
- ✅ Bridge-Artefakte quarantänisiert
- ⏳ Business Reality Audit — NÄCHSTER SCHRITT
- ❌ Keine Feature-Implementierung vor Audit

## Nächster Schritt

**Read-only Business Reality Audit:** Prüfe Agenturseite, Leadstrecke, KI-Berater, Angebotsprozess, Kundenprojekte, Security/CI, Runtime, Domains, Auth und Deployment-Wahrheit. Keine Feature-Implementierung vor Audit.

## Keine Secrets

Dieser Index enthält keine Secrets, keine API-Keys, keine personenbezogenen Token und keine Chat-Rohdaten.

