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

## Health-Alert-System (27.04.2026 — DONE)

**Feature**: Automatische Benachrichtigung bei System-Health-Failures per E-Mail + optional Slack.

**Architektur**:
- `vercel-config/functions/api/cron/health-monitor.func/` ruft alle 5 Minuten `/api/health` am Backend ab
- Bei Unhealthy-Services wird `/api/internal/alerts/health` (mit `CRON_SECRET` Bearer-Auth) benachrichtigt
- Backend dedupliziert (60 min Cooldown pro Service), sendet E-Mail an `NOTIFICATION_EMAILS` (+ Slack wenn `SLACK_WEBHOOK_URL` gesetzt), persistiert in `health_alerts` + `health_alert_state`
- Recovery-Notifications senden sich automatisch, sobald ein Service wieder gesund ist

**Neue Endpoints**:
- `POST /api/internal/alerts/health` — Cron-only (CRON_SECRET Bearer)
- `GET /api/admin/health-alerts` — Admin-History inkl. active_incidents
- `POST /api/admin/health-alerts/test` — manuelles Test-Alert für Admin

**Neue Env-Variablen** (in `/app/backend/.env`):
- `CRON_SECRET` (gesetzt)
- `SLACK_WEBHOOK_URL` (optional, off by default)

**Härtung der `send_email()`** (gleicher Release):
- 3 Retry-Versuche mit Exponential Backoff (0.6s/1.2s/2.4s) bei transienten Fehlern (429, 502, 503, timeout, rate limit)
- Fehler-Details (`error` + `failed_at`) jetzt persistiert
- Alter Rate-Limit-Fail (04.04.2026) archiviert als `failed_acknowledged`

**E2E Test Scenarios (alle bestanden)**:
1. Unauthorized Request → 401
2. Erster Failure → Alert versendet
3. Duplicate in Cooldown → unterdrückt
4. Recovery → Recovery-Mail + Incident cleared
5. Admin History-Endpoint zeigt Events + Active-Incidents

## Passwort-Reset & Admin-Kundenkonten-Verwaltung (27.04.2026 — DONE)

**Feature**: Vollständiger Self-Service Passwort-Reset für Kundenportal-Konten + Admin-Steuerung.

**Backend-Endpoints**:
- `POST /api/auth/password-reset/request` — Self-Service Reset; rate-limited 5/600s; stets 200 (keine User-Enumeration); Token 1h gültig; sendet Reset-E-Mail via Resend
- `POST /api/auth/password-reset/confirm` — Token + neues Passwort (min. 8 Zeichen); invalidiert Token nach Use; gibt JWT zurück (direkter Login)
- `GET /api/admin/customer-accounts?search=` — Admin-Liste aller aktivierten Kundenkonten
- `POST /api/admin/customer-accounts/{email}/reset` — Admin triggert Reset-Mail
- `DELETE /api/admin/customer-accounts/{email}` — Admin deaktiviert Account (audit-preserving, kein Hard-Delete)

**Frontend** (`UnifiedLogin.js`):
- Neuer Step `customer_password` enthält Link "Passwort vergessen?" → `requestPasswordReset`
- Neuer Step `reset_sent` (Bestätigung nach Anforderung)
- URL-Parameter `?reset_token=X` aktiviert automatisch Step `reset_password` (Neues Passwort + Bestätigung → `confirmPasswordReset` → auto-login → /portal)

**Security**:
- Rate limiting (5/600s bzw. 20/300s)
- Keine User-Enumeration in Response
- Token gehasht in DB (SHA-256)
- Tokens sind 1x verwendbar
- Admin-Aktionen im `audit_log`

**E2E Test**: `/app/backend/tests/test_customer_portal_setup_e2e.py` (19/19 assertions — setup, login, reset, admin list/reset/deactivate)

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
- P1: Contract OS-Erweiterung (RAG, Risikoscoring via Nutrient AI) — benötigt Nutrient AI API Key
- P2: ✅ DONE — Cron Alerting (E-Mail + optional Slack bei Health-Failure)
- P5: Legal & Compliance Guardian
- P6: Outbound Lead Machine
- P7: server.py Modular Refactoring (>4000 Zeilen)
- P8: ✅ DONE — Admin Kundenkonten-Verwaltung + Passwort-Reset
- P9: ✅ DONE — Admin-UI Frontend für Kundenkonten-Management
- P10: Admin-UI für Health-Alert-History (Backend-Endpoints bereit)
