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

## Kundenkonto-Zwang bei Angeboten (27.04.2026 — DONE)
**Feature**: Kunden müssen vor Angebotsansicht ein Passwort festlegen, um ein Kundenportal-Konto zu erstellen.

**Flow**:
1. Kunde klickt auf "Angebot öffnen" Link in E-Mail (`/portal/quote?token=X&qid=Y`)
2. `GET /api/portal/quote/{qid}?token=X` liefert `account_status.has_account=false` bei erstem Zugriff
3. `QuotePortal.js` zeigt Passwort-Setup-UI (min. 8 Zeichen, Bestätigung)
4. `POST /api/portal/setup-account` erstellt `customer_accounts` Eintrag (bcrypt), legt Contact-Record an, liefert JWT → direkter Portal-Zugriff
5. Bei späteren Besuchen: Login unter `/login` mit E-Mail + Passwort → `POST /api/auth/customer-login` → JWT für `/api/customer/*`
6. `POST /api/auth/check-email` liefert jetzt `has_portal_password` — `UnifiedLogin.js` zeigt `customer_password`-Step statt Magic Link
7. Dual-Flow (Admin + Kunde): 2 Optionen (Administration mit Passwort, Kundenportal mit Passwort/Magic-Link je nach Status)

**E2E Test**: `/app/backend/tests/test_customer_portal_setup_e2e.py` (10/10 assertions pass)

**Security**:
- Rate limiting (20/300s) auf `/api/auth/customer-login`
- bcrypt Passwort-Hashing
- Audit-Log für failed/success logins
- Token-basierte Quote-Zugriff bleibt unverändert

**Gefixt nebenbei**:
- Doppelte Route-Definitionen in `portal_routes.py` (accept/decline/revision) bereinigt
- Fehlende Imports (secrets, timedelta, VAT_RATE, get_tariff, get_next_number, create_revolut_order, generate_invoice_pdf) in `portal_routes.py` ergänzt → Accept-Flow war zuvor latent broken
- `check-email` Response-Shape konsistent (immer alle Flags)

## Backlog
- P1: Contract OS-Erweiterung (RAG, Risikoscoring via Nutrient AI)
- P2: Cron Alerting (Slack/Email bei Health-Failure)
- P5: Legal & Compliance Guardian
- P6: Outbound Lead Machine
- P7: server.py Modular Refactoring (>4000 Zeilen)
- P8: Admin-UI "Kundenkonten verwalten" (Passwort-Reset durch Admin)
