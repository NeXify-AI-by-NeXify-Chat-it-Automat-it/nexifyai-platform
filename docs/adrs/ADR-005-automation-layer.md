# ADR-005: Native Automation Layer (ersetzt n8n)

**Status:** ACCEPTED  
**Datum:** 2026-05-08  
**Decider:** NeXifyAI (Hermes Lead Agent)  
**Consulted:** Pascal Courbois (CEO)  
**Replaces:** Keine vorherige ADR — strategische Korrektur der impliziten n8n-Annahme  

## Kontext

Die DOS-v2.0-Transformation wurde ohne dedizierte Automation-Layer-Entscheidung abgeschlossen. Zuvor existierte die implizite Annahme, n8n könne als zentrale Workflow-Engine dienen. Eine strategische Neubewertung ergibt, dass dieser Ansatz für ein Brain-first, AI-natives System ungeeignet ist.

### IST-Zustand (08.05.2026)
- Kein n8n-Container, kein n8n-Cron, keine n8n-Config
- 3 Code-Referenzen auf n8n (alle entfernt in M1.1)
- packages/events/taxonomy.ts existiert (v1.0, 19 Event-Schemata)
- packages/workflows/ und packages/services/ existieren NICHT
- 12 Cron-Jobs via Hermes Cron Scheduler (Polling-basiert)
- Event-Driven Autopilot als Roadmap-Konzept dokumentiert

## Entscheidung

**n8n wird NICHT verwendet.** Automation erfolgt ausschließlich über native, versionierte, CI-validierte Systeme.

### Gewählte Architektur

| Bereich | Lösung | Begründung |
|---------|--------|------------|
| Cronjobs | GitHub Actions + native VPS systemd timers | Versioniert im Repo, CI-validiert, kein externes System |
| Event Processing | Supabase Edge Functions | TypeScript, Deno-basiert, nah an der DB, geringe Latenz |
| Queue-Systeme | BullMQ (Redis) | Siehe ADR-006 |
| Background Jobs | Trigger.dev | Open-Source, TypeScript-native, Observability integriert |
| Internal Workflows | TypeScript Services in /packages/workflows/ | Monorepo, CI, testbar |
| Event Bus | Supabase Realtime + Redis Streams | PostgreSQL-nativ, geringe Komplexität |
| AI Orchestration | Native Hermes Agent Layer | Bestehende Architektur, Brain-first |
| Monitoring | OpenTelemetry + Sentry + Prometheus | Siehe ADR-007 |
| Scheduling | Vercel Cron + GitHub scheduled workflows | Serverless, versioniert |
| Webhooks | First-Class API Layer (FastAPI) | Type-safe, OpenAPI-dokumentiert |
| State Machines | XState (TypeScript) | Bei komplexen Workflows, optional |

### Verworfene Alternativen

| Alternative | Ablehnungsgrund |
|-------------|-----------------|
| n8n | Unnötige Systemlast, Infrastruktur-Overhead, Wartungsaufwand, schwache Typsicherheit, fragmentierte Logik, schlechte Skalierbarkeit für Brain-first, erschwerte CI/CD-Governance |
| Zapier/Make | Vendor-Lockin, nicht versionierbar, keine CI-Integration |
| Temporal | Overengineered für aktuelle Skalierung, komplexe Infrastruktur |

## Konsequenzen

### Positiv
- **Alles ist Code:** Versioniert, reviewbar, CI-validiert
- **Monorepo-Integrität:** Keine fragmentierte Logik
- **Brain-first:** Automationen können Brain-Zustand lesen
- **Zero Overhead:** Kein zusätzlicher Container/Service
- **Skalierbar:** Von Cron → Event-Driven migrierbar (Roadmap vorhanden)

### Negativ
- Höherer initialer Implementierungsaufwand (TypeScript-Services schreiben statt Flowchart klicken)
- Kein visuelles Workflow-Debugging (dafür TypeScript-Tooling)
- Benötigt Entwickler-Know-how für Automation-Änderungen

### Neutral
- Teams müssen TypeScript statt Low-Code nutzen
- Workflow-Änderungen durchlaufen PR-Review-Zyklus

## Compliance-Prüfung

| Guardrail | Status |
|-----------|--------|
| Funnel-Zuordnung | ✅ Jede Automation hat Trigger+Ziel |
| No One-Off UI | ✅ Keine visuelle Workflow-UI |
| Tracking First | ✅ Events via taxonomy.ts |
| Loop-Automation | ✅ KPI-Thresholds in Workflows |
| Dokumentationspflicht | ✅ Jeder Workflow dokumentiert |
| Modularität | ✅ Austauschbare Service-Module |

## Referenzen

- DOS v2.0 Kap. 21: AI Agent Operating Layer
- /docs/architecture/event-driven-autopilot.md
- /packages/events/taxonomy.ts
- ADR-006: Queue System
- ADR-007: Observability Stack
