# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Fully premium, highly secure architecture with D/A/CH localization (EUR only, no $). CI design system relying strictly on "Dutch Orange" (#FF6B00) and White.

## Core Requirements
- Unified Login Stack with strict role separation (Admin/Customer)
- Contract Operating System (master contracts, modular appendices, digital acceptance)
- Unified Communication (LiveChat, Booking, Contact Forms)
- Background Worker/Scheduler Layer (APScheduler)
- KI-Orchestrator (Target: DeepSeek, Current Mock: Emergent GPT-5.2)
- Multi-language support: DE/NL/EN
- Legal compliance: D/A/CH (Impressum, Datenschutz, AGB, KI-Hinweise, Widerruf, Cookies, AVV)
- External API v1 with API-Key authentication

## Architecture
- Frontend: React 18 SPA
- Backend: FastAPI (Python) with modular routes
- Database: MongoDB
- Auth: JWT + Magic Links (internal), API Keys (external)
- Workers: APScheduler
- CI: Dutch Orange (#FF6B00) and White only

## What's Been Implemented

### Completed (verified via testing)
- [x] Worker/Scheduler-Layer (APScheduler, Queue, Dead-letter)
- [x] Services scaffolding (comms.py, outbound.py, billing.py, llm_provider.py)
- [x] Public Auth Security
- [x] Mobile Menu Overlay & Floating Actions
- [x] Hero 3D Scene
- [x] System-wide Design/Brand Harmonization (all breakpoints)
- [x] Admin Sidebar (collapsed default, hover tooltips)
- [x] Customer Portal Sidebar + Active Features
- [x] Comprehensive Legal Texts (7 docs x 3 langs = 21 routes) — Iter 62
- [x] TrustSection i18n Bug Fix + enhanced copy — Iter 63
- [x] External API v1 with API-Key Authentication — Iter 64
  - Contacts CRUD, Leads CRUD, Quotes/Contracts/Projects/Invoices Read
  - Stats, Webhooks, Health, Docs endpoints
  - Admin API Key Management (create/list/toggle/delete)
  - Frontend API-Zugang panel with cURL examples

### In Progress
- [ ] P2: DeepSeek Live-Migration (requires DEEPSEEK_API_KEY — already configured in .env)

### Backlog
- [ ] Projektchat / Build-Handover-Kontext härten
- [ ] Revolut/Stripe Live-Webhooks & Billing-Status-Sync
- [ ] Legal & Compliance Guardian (operative wiring)
- [ ] Outbound Lead Machine (production readiness)
- [ ] server.py modular refactoring (AFTER all features stable)
- [ ] Next.js Migration (target architecture)
- [ ] PydanticAI + LiteLLM + Temporal Adoption

## External API v1 Reference
- Base URL: `/api/v1`
- Auth: `X-API-Key: nxa_live_...` header
- Endpoints: /health, /docs, /stats, /contacts, /leads, /quotes, /contracts, /projects, /invoices, /webhooks
- Admin Key Mgmt: /api/admin/api-keys (CRUD)
- Scopes: all, contacts:read/write, leads:read/write, quotes:read, contracts:read, projects:read, invoices:read, stats:read, webhooks:read/write

## Key DB Collections
projects, contracts, documents, webhook_events, outbound_leads, contacts, api_keys, webhooks

## Testing History
- Iteration 60: Admin Sidebar (100% Pass)
- Iteration 61: Customer Portal (100% Pass)
- Iteration 62: Legal Pages (100% Pass)
- Iteration 63: TrustSection i18n Fix (100% Pass)
- Iteration 64: External API v1 (100% Pass — 24/24 backend + frontend)
