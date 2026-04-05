# NeXifyAI — Product Requirements Document (PRD)

## Plattform
NeXifyAI by NeXify — B2B AI Agency Platform. API-First, Unified Communication, Deep Customer Memory (mem0), Supabase Oracle System, DeepSeek/Arcee AI Orchestrators, Agent Zero (External Master).

## Architektur
- **Frontend**: React 18 SPA
- **Backend**: FastAPI (Python)
- **Datenbanken**: MongoDB (CRM, Projekte), Supabase PostgreSQL (Oracle Tasks, AI Agents, Brain Notes, Audit Logs)
- **AI**: DeepSeek (Primary Master + Sub-Agenten), Arcee AI (Fallback), mem0 (Brain Memory)
- **Agent Zero**: Externer Docker-Service (`agent0ai/agent-zero:latest`) — Zentraler Master-Orchestrator
- **Intelligence**: Crawl4AI (Web-Crawling), Nutrient AI (Document Processing)
- **Tasks**: Trigger.dev (6 TS-Tasks mit Python-Bridge, Fallback via DeepSeek lokal)
- **Workers**: APScheduler (24/7 autonome Task-Verarbeitung)

## Implementierte Module

### 1. Unified Login Stack
- 2-Schritt-Anmeldung, Admin/Kundenportal-Trennung, JWT Auth

### 2. Oracle System (Supabase)
- Autonome Task-Verarbeitung (alle 90s)
- 9 KI-Agenten: Nexus, Strategist, Forge, Lexi, Scout, Scribe, Pixel, Care, Rank
- Score-basierte Verifikation

### 3. Granulares Status-Modell (Zentrale Leitstelle)
- 13 definierte Status: erkannt bis eskaliert
- Loop-Tracking, Evidence-Pakete, Auto-Eskalation

### 4. Service-Boilerplate-System
- 9 Leistungskonzepte mit Template-Instanziierung

### 5. DeepSeek Live-Migration
- Master Orchestrator auf DeepSeek
- DeepSeek = Primary, Arcee = Fallback
- Streaming-Chat, Tool-Execution, Follow-up

### 6. Intelligence Center
- **Crawl4AI**: Web-Crawling, Firmen-Recherche, Wettbewerbsmonitoring
- **Nutrient AI**: PDF-Analyse, Vertrags-Risikoscoring, Dokumenten-Chat

### 7. Platform-Härtung
- .env.template, Health-Check (8 Services), Startup-Key-Validierung
- Stripe entfernt, Revolut aktiv

### 8. NeXify AI Master Chat
- DeepSeek-powered Konversationen mit mem0 Brain
- Intelligence-Tools direkt im Chat verfügbar

### 9. Agent Zero Hierarchie (NEU - 05.04.2026)
- System-Prompt etabliert Agent Zero als externen Master
- invoke_agent Tool nutzt DeepSeek primary, Arcee fallback
- Hierarchie: Pascal → Agent Zero → NeXify AI → Fachagenten

### 10. Trigger.dev Tasks Admin UI (NEU - 05.04.2026)
- 6 Tasks: Deep Research, Report generieren, Copy & Übersetzen, Vertragsanalyse, Wettbewerber-Monitoring, PDF generieren
- Task-Runner mit Payload-Editor im Admin-Panel
- Run-Historie mit Live-Polling (15s)
- Fallback-Modus: Lokale DeepSeek-Execution wenn kein TRIGGER_DEV_API_KEY

## API Endpoints (Aktuell)
- `GET /api/health` — 8 Services Health-Check
- `GET /api/admin/nexify-ai/status` — Master LLM Status (DeepSeek/Arcee)
- `GET /api/admin/oracle/leitstelle` — Live-Statusübersicht
- `GET /api/admin/service-templates` — 9 Boilerplates
- `POST /api/admin/intelligence/crawl` — Web-Crawling
- `POST /api/admin/intelligence/research-company` — Firmen-Recherche
- `GET /api/admin/trigger/tasks` — 6 Trigger.dev Tasks
- `POST /api/admin/trigger/run` — Task starten (Cloud oder Fallback)
- `GET /api/admin/trigger/runs` — Run-Historie
- `GET /api/admin/trigger/status` — Trigger.dev Verbindungsstatus

## Testing: Iteration 80, 100% Pass (Backend 7/7, Frontend 100%)

## Backlog
- P1: Contract OS-Erweiterung (RAG, Risikoscoring via Nutrient AI)
- P2: Cron-Jobs via Trigger.dev Scheduler (tägliches Competitor-Monitoring)
- P4: DeepSeek Live-Migration abschließen (Concrete routing)
- P5: Legal & Compliance Guardian
- P6: Outbound Lead Machine
- P7: server.py Modular Refactoring (nach P1-P6 stabil)
- Next.js Migration
