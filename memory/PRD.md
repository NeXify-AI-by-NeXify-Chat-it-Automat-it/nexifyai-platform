# NeXifyAI — Product Requirements Document (PRD)

## Plattform
NeXifyAI by NeXify — B2B AI Agency Platform. API-First, Unified Communication, Deep Customer Memory (mem0), Supabase Oracle System, DeepSeek/Arcee AI Orchestrators.

## Architektur
- **Frontend**: React 18 SPA
- **Backend**: FastAPI (Python)
- **Datenbanken**: MongoDB (CRM, Projekte), Supabase PostgreSQL (Oracle Tasks, AI Agents, Brain Notes, Audit Logs)
- **AI**: Arcee AI (Master Orchestrator), DeepSeek (Sub-Agenten via LLMProvider), mem0 (Brain Memory)
- **Workers**: APScheduler (24/7 autonome Task-Verarbeitung)

## Implementierte Module

### 1. Unified Login Stack
- 2-Schritt-Anmeldung (E-Mail -> Rollenauswahl -> Passwort)
- Admin- und Kundenportal-Trennung, JWT Auth

### 2. Oracle System (Supabase)
- Autonome Task-Verarbeitung (alle 90s)
- 9 KI-Agenten: Nexus, Strategist, Forge, Lexi, Scout, Scribe, Pixel, Care, Rank
- Brain-Notes & Knowledge-Base, Score-basierte Verifikation

### 3. Granulares Status-Modell (Zentrale Leitstelle)
- 13 definierte Status: erkannt, eingeplant, gestartet, in_bearbeitung, wartet_auf_input, wartet_auf_freigabe, in_loop, erfolgreich_abgeschlossen, erfolgreich_validiert, fehlgeschlagen, blockiert, abgebrochen, eskaliert
- Loop-Tracking, Evidence-Pakete, Automatische Eskalation
- Status-History (JSONB) mit Audit-Trail
- Manuelle Eskalation/Abbruch durch Admin

### 4. Service-Boilerplate-System
- 9 Leistungskonzepte: Starter/Growth AI (499/1299 EUR/Mo), SEO Starter/Growth (799/1499 EUR/Mo), Website Starter/Pro/Enterprise (2990/7490/14900 EUR), App MVP/Pro (9900/24900 EUR)
- Template-Instanziierung: Sofortige Projekterstellung mit Milestones, Tasks, Agenten-Zuweisungen

### 5. Platform-Härtung (AUFTRAG.txt)
- .env.template mit dokumentierten Keys
- Stripe vollständig entfernt, Revolut aktiv
- /api/health mit 8 Service-Checks (MongoDB, Supabase, DeepSeek, Arcee, mem0, Resend, Revolut, Workers)
- API-Key Startup-Validierung mit Graceful Degradation
- Sub-Agenten migriert auf LLMProvider (DeepSeek primary)
- Status-Migration: Legacy-EN -> Granular-DE (2634 Tasks migriert)
- Oracle Views aktualisiert (varchar(50), neue Status)
- Frontend deutsche Labels in OracleView
- Logging-System (JsonFormatter für Production)
- Dokumentation: SETUP.md, .env.template

### 6. NeXify AI Master Chat
- Kontextbewusste KI-Konversationen (Arcee AI)
- Brain-Integration (mem0), Direkte Tools
- Schnellaktionen: Morgen-Briefing, Lead-Analyse, System-Check

### 7. CRM & Pipeline
- Leads, Kontakte, Angebote, Verträge, Rechnungen, Timeline

## API Endpoints (Neu)
- `GET /api/health` — Öffentlicher Health-Check (8 Services)
- `GET /api/admin/oracle/leitstelle` — Live-Statusübersicht
- `GET /api/admin/oracle/tasks/{id}/transitions` — Task-Statusübergänge
- `POST /api/admin/oracle/tasks/{id}/escalate` — Manuelle Eskalation
- `POST /api/admin/oracle/tasks/{id}/cancel` — Manueller Abbruch
- `GET /api/admin/service-templates` — 9 Boilerplates
- `GET /api/admin/service-templates/{key}` — Template-Detail
- `POST /api/admin/service-templates/instantiate` — Projekt aus Template

## Testing: Iteration 78, 100% Pass (Backend 35/35, Frontend 100%)

## Backlog
- P1: Legal & Compliance Guardian (operative Verdrahtung)
- P2: DeepSeek Live-Migration für Master Orchestrator (Arcee -> DeepSeek)
- server.py Refactoring (nach Stabilisierung)
- Next.js Migration, PydanticAI + LiteLLM + Temporal
