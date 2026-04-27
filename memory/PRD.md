# NeXifyAI — Product Requirements Document (PRD)

## Plattform
NeXifyAI by NeXify — B2B AI Agency Platform. API-First, Unified Communication, Deep Customer Memory (mem0), Supabase Oracle System, OpenRouter/DeepSeek V4 Flash (Primary LLM), Agent Zero (External Master).

## Architektur
- **Frontend**: React 18 SPA (Vercel Pro, Edge Network)
- **Backend**: FastAPI (Python, Emergent Preview)
- **AI**: OpenRouter / DeepSeek V4 Flash (Primary), Arcee AI (Fallback)
- **Deployment**: Vercel Pro (Frontend + Edge Functions + Cron)

## Vercel Pro Stack (27.04.2026)

### API Proxy (Edge Rewrite)
- Alle `/api/*` Anfragen werden von Vercel Edge zum Backend proxied
- Eliminiert CORS komplett — Same-Origin Requests
- Backend-URL vor Browser versteckt

### Security Headers
- HSTS (63072000s, includeSubDomains, preload)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: camera=(), microphone=(), geolocation=()

### Caching
- Statische Assets: `max-age=31536000, immutable` (1 Jahr)
- API: Kein Cache (passthrough)

### Analytics & Performance
- @vercel/analytics (Web Analytics)
- @vercel/speed-insights (Core Web Vitals)

### Skew Protection
- Max Age: 86400s — verhindert Versionskonflikte bei Deployments

### Cron Jobs (Edge Functions)
| Job | Schedule | Funktion |
|-----|----------|----------|
| health-monitor | */5 * * * * | Backend-Health prüfen (8 Services) |
| oracle-pulse | */15 * * * * | Oracle-Task Processing triggern |
| competitor-monitor | 0 6 * * * | Tägliche Wettbewerbsanalyse |
| cleanup-sessions | 0 3 * * * | Stale Sessions bereinigen |

### Env-Variablen (Vercel encrypted)
- REACT_APP_BACKEND_URL (leer — Proxy-Modus)
- CRON_SECRET (Auth für Cron-Endpoints)
- ADMIN_EMAIL, ADMIN_PASSWORD (Cron-Auth zum Backend)

## Deploy-Workflow
```bash
cd /app/frontend && REACT_APP_BACKEND_URL="" yarn build
rm -rf /tmp/vercel-deploy/.vercel/output/static/*
cp -r /app/frontend/build/* /tmp/vercel-deploy/.vercel/output/static/
cp /app/vercel-config/config.json /tmp/vercel-deploy/.vercel/output/config.json
cp -r /app/vercel-config/functions/* /tmp/vercel-deploy/.vercel/output/functions/
cd /tmp/vercel-deploy && npx vercel deploy --prod --prebuilt --token <TOKEN>
```

## Domains
- nexify-automate.com (verified)
- www.nexify-automate.com (verified)
- nexifyai-website-sicherheitskopie.vercel.app

## Testing: Iteration 82, 100% Pass

## Backlog
- P1: Contract OS-Erweiterung (RAG, Risikoscoring via Nutrient AI)
- P2: Cron Alerting (Slack/Email bei Health-Failure)
- P5: Legal & Compliance Guardian
- P6: Outbound Lead Machine
- P7: server.py Modular Refactoring
