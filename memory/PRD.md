# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, KI-Orchestrator. Premium, hochsichere Architektur. CI: Niederländisches Orange (#FF6B00) + Weiss. Revolut ONLY. D/A/CH-Lokalisierung.

## CI-Farben (Verbindlich)
- **Primär**: Niederländisches Orange `#FF6B00` (Hover: `#FF8533`)
- **Sekundär**: Weiss `#FFFFFF`
- **Ausnahmen NUR**: Grün (Bestätigung), Rot (Warnung), Blau (Information)
- **Keine**: Dollar-Zeichen ($), billige SVG-Icons

## Tech Stack
React 18 SPA, FastAPI, MongoDB, JWT Auth, APScheduler, Hostinger SMTP, Revolut, Emergent GPT-5.2 (DeepSeek Target)

## Go-Live Status: APPROVED (Iteration 60, 100%)

### Verifizierte Geschäftsprozesse
- E2E Outbound: Discover > Prequalify > Analyze > Legal > Outreach > Send > Respond > Handover
- E2E Contract: Create > Appendix > Send (Magic Link) > View > Legal Accept > Signature > Evidence
- Public Contract Acceptance: `/vertrag?token=xxx&cid=xxx` (token-basiert, kein Login)
- Admin Sidebar: Collapsed by default, Toggle, Mouseover-Tooltip-Labels

### Architecture Blocks (Alle VERIFIZIERT)
| Block | Status |
|-------|--------|
| A: Public Website (3D Hero, Legal Pages, Booking) | VERIFIZIERT |
| B: Customer Portal (10 Tabs) | VERIFIZIERT |
| C: Admin Panel (19+ Views, Collapsed Sidebar) | VERIFIZIERT |
| D: Governance (Users, Webhooks, Audit, Monitoring) | VERIFIZIERT |
| E: Outbound Lead Machine (42 Leads) | VERIFIZIERT |
| F: Backend Infrastructure (10 Route-Module) | VERIFIZIERT |
| G: Production Hardening (HSTS, CORS, Rate Limiting) | VERIFIZIERT |
| CI: Orange/Weiss Migration (293+ Referenzen) | VERIFIZIERT |
| H: Sidebar Default-Closed + Tooltips | VERIFIZIERT |

### Testing History
- Iteration 55-59: 100% (Functional, E2E, Security, CI Migration)
- **Iteration 60: 100% — Sidebar Collapsed + Tooltips + Finaler Audit verifiziert**

## Test Credentials
- Admin: p.courbois@icloud.com / 1def!xO2022!!

## MOCKED: DeepSeek > Emergent GPT-5.2

## Post-Go-Live Backlog
- [ ] DeepSeek Live-Migration
- [ ] Content & Copywriting Overhaul
- [ ] server.py modular refactoring
- [ ] Next.js Migration
- [ ] PydanticAI + LiteLLM + Temporal
