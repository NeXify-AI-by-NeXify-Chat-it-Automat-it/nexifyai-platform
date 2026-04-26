# NeXifyAI — Product Requirements Document (PRD)

## Plattform
NeXifyAI by NeXify — B2B AI Agency Platform. API-First, Unified Communication, Deep Customer Memory (mem0), Supabase Oracle System, OpenRouter/DeepSeek V4 Flash (Primary LLM), Agent Zero (External Master).

## Architektur
- **Frontend**: React 18 SPA (Vercel Deployment)
- **Backend**: FastAPI (Python)
- **Datenbanken**: MongoDB (CRM, Projekte), Supabase PostgreSQL (Oracle Tasks, AI Agents, Brain Notes, Audit Logs)
- **AI**: OpenRouter / DeepSeek V4 Flash (Primary Master + Sub-Agenten), Arcee AI (Fallback), mem0 (Brain Memory)
- **Agent Zero**: Externer Docker-Service (`agent0ai/agent-zero:latest`) — Zentraler Master-Orchestrator
- **Intelligence**: Crawl4AI (Web-Crawling), Nutrient AI (Document Processing)
- **Tasks**: Trigger.dev (6 TS-Tasks mit Python-Bridge, Fallback via OpenRouter lokal)
- **Workers**: APScheduler (24/7 autonome Task-Verarbeitung)
- **Deployment**: Vercel (Frontend), Emergent Preview (Backend)

## Vercel Deployment
- **Projekt**: nexifyai-website-sicherheitskopie
- **URL**: https://nexifyai-website-sicherheitskopie.vercel.app
- **Methode**: Pre-built static deployment (`.vercel/output/static`)
- **Env**: REACT_APP_BACKEND_URL → Emergent Preview Backend
- **Deploy-Befehl**: `cd /app/frontend && yarn build` → Copy zu `/tmp/vercel-deploy/.vercel/output/static/` → `npx vercel deploy --prod --prebuilt`

## Implementierte Module

### 1-10: (Siehe vorherige PRD-Einträge)

### 11. LLM-Migration: DeepSeek V4 Flash via OpenRouter (26.04.2026)
- Modell geändert von minimax/minimax-m2.7 → deepseek/deepseek-v4-flash
- Neuer API-Key konfiguriert
- Alle Defaults in deepseek_provider.py, llm_provider.py, nexify_ai_routes.py aktualisiert

### 12. Vercel Frontend Deployment (26.04.2026)
- Projekt-Config korrigiert (war: rootDirectory=backend, Framework=None)
- Pre-built Static Output Deployment
- 3 Vercel-Domains aktiv

## API Endpoints (Aktuell)
- `GET /api/health` — 8 Services (openrouter, arcee, mem0, supabase, mongodb, resend, revolut, workers)
- `GET /api/admin/nexify-ai/status` — Master LLM Status (OpenRouter/Arcee)
- `GET /api/admin/oracle/leitstelle` — Live-Statusübersicht
- `GET /api/admin/oracle/health` — Supabase + OpenRouter Konnektivität
- Trigger.dev, Intelligence, Service-Templates etc.

## Testing: Iteration 81, 100% Pass

## Backlog
- P1: Contract OS-Erweiterung (RAG, Risikoscoring via Nutrient AI)
- P2: Cron-Jobs via Trigger.dev Scheduler
- P5: Legal & Compliance Guardian
- P6: Outbound Lead Machine
- P7: server.py Modular Refactoring (nach P1-P6 stabil)
- Next.js Migration
