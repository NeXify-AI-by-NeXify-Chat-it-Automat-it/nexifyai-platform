# NeXifyAI — Product Requirements Document (PRD)

## Plattform
NeXifyAI by NeXify — B2B AI Agency Platform. API-First, Unified Communication, Deep Customer Memory (mem0), Supabase Oracle System, OpenRouter/DeepSeek V4 Flash (Primary LLM), Agent Zero (External Master).

## Architektur
- **Frontend**: React 18 SPA (Vercel Deployment: nexify-automate.com)
- **Backend**: FastAPI (Python, Emergent Preview)
- **Datenbanken**: MongoDB (CRM, Projekte), Supabase PostgreSQL (Oracle Tasks, AI Agents)
- **AI**: OpenRouter / DeepSeek V4 Flash (Primary), Arcee AI (Fallback), mem0 (Brain Memory)
- **Deployment**: Vercel Pre-built (Frontend), Emergent (Backend)

## Vercel Deployment
- **URL**: https://www.nexify-automate.com
- **Methode**: Pre-built Static (`/tmp/vercel-deploy/.vercel/output/static/`)
- **Deploy**: `cd /app/frontend && yarn build` → Copy → `npx vercel deploy --prod --prebuilt`

## Zuletzt implementiert (27.04.2026)

### LLM-Modell: deepseek/deepseek-v4-flash via OpenRouter
### Chat UI Fixes
- Admin Chat: Cursor-Verlust behoben (ViewName() statt <ViewName />)
- LiveChat: z-index 200→400 (über Cookie-Banner z-300)
- LiveChat: grid-template-rows:1fr + flex:1 1 0% + min-height:0

## Testing: Iteration 82, 100% Pass (Frontend 4/4)

## Backlog
- P1: Contract OS-Erweiterung (RAG, Risikoscoring via Nutrient AI)
- P2: Cron-Jobs via Trigger.dev Scheduler
- P5: Legal & Compliance Guardian
- P6: Outbound Lead Machine
- P7: server.py Modular Refactoring
