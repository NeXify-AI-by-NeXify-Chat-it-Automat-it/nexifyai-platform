# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium, hochsichere Architektur. Unified Login Stack, Worker/Scheduler Layer, Revolut-only Billing, vollständige Outbound Lead Machine mit Lead-Scraping und Kontaktaufnahme. Autopilot-Direktive P0.10 bis P0.10.7 für vollumfängliche Produktion.

## Tech Stack
- **Frontend**: React 18 SPA (CRA), Shadcn/UI
- **Backend**: FastAPI (Python), modular routing
- **Database**: MongoDB (via MONGO_URL)
- **Auth**: JWT, Dual-Role (Admin/Kundenportal), OAuth2 form-encoded
- **Workers**: APScheduler (Background Jobs, Queue, Dead-Letter)
- **Email**: Hostinger SMTP
- **LLM**: DeepSeek (Target) — currently routed through Emergent GPT-5.2 mock
- **Payments**: Revolut ONLY (Stripe removed)
- **Storage**: emergentintegrations Object Storage

## Architecture Blocks (Autopilot P0.10)

### BLOCK A — Public, Pre-Login, Conversion Core (DONE)
- 3D Hero, Solutions, UseCases, AppDev, Process, Governance, Pricing, FAQ, SEO
- Services page, Trust indicators, Integration showcase
- LiveChat, Booking modal, Cookie consent
- Legal pages (Impressum, Datenschutz, AGB) via LegalPages component
- Footer with full legal links

### BLOCK B — Customer Portal (DONE)
- 10 Tabs: Übersicht, Verträge, Projekte, Angebote, Finanzen, Dokumente, Termine, Kommunikation, Aktivität, Einstellungen
- Profile editing (first_name, last_name, phone, company, country)
- Document management (Verträge, Angebote, Rechnungen, Build-Handover als Download-Liste)
- Consent management (Marketing Opt-In/Out, DSGVO-Einwilligungen)
- Contract acceptance with digital signature & evidence package
- Finance overview with invoice tracking

### BLOCK C — Admin Panel (DONE)
- 19 Navigation Views: Dashboard, Projekte, Verträge, Billing, Outbound, Legal, Angebote & Rechnungen, Leads, Kommunikation, KI-Chats, WhatsApp, Aktivitäten, Kalender, Kunden, KI-Agenten, Benutzer, Webhooks, Audit, Monitoring
- Full CRUD for all entities
- Customer Case File (Kunden-Fallakte) with direct email

### BLOCK D — Admin Governance (DONE)
- Admin User Management (CRUD: create, update, delete, list, self-deletion blocked)
- Webhook Event Store (list webhook events with filtering)
- Audit Log view
- Legal & Compliance Guardian (risk assessment, gate decisions)
- System Monitoring (API, DB, Workers, Email, LLM, Payments, Webhooks, Dead-Letter, Object Storage, Documents)
- Recovery & Self-Healing status panel

### BLOCK E — Outbound Lead Machine (DONE)
- Full CRUD: Lead Discovery, Prequalify, Analyze & Score, Legal-Check
- Outreach Creation/Sending, Follow-up, Response Tracking
- Handover (Angebot/Termin/Nurture), Bulk Import, Opt-Out
- Pipeline visualization with stats & filter system
- Lead detail view with full pipeline action buttons

### BLOCK F — Backend, Data, APIs (DONE)
- Modular routing: auth_routes, admin_routes, portal_routes, billing_routes, project_routes, contract_routes, outbound_routes, monitoring_routes
- Webhook Event Store (revolut webhooks stored + queried)
- Timeline events for all operations
- Legal audit logging
- Customer memory service

### BLOCK G — Production Hardening (DONE)
- CORS restriction (origins whitelist, wildcard only in preview)
- Security headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Strict-Transport-Security, Permissions-Policy, Referrer-Policy
- Rate limiting (200/min via slowapi)
- Worker/Scheduler with Dead-Letter Queue

## Key API Endpoints
- POST /api/admin/login (OAuth2 form-encoded)
- GET/POST /api/admin/users (User management)
- DELETE /api/admin/users/{email}
- GET /api/admin/webhooks/events
- GET/POST /api/admin/outbound/* (Full pipeline)
- GET/POST /api/admin/projects/*
- GET/POST /api/admin/contracts/*
- GET /api/admin/stats, /billing/status, /legal/compliance, /monitoring/status
- GET/PATCH /api/customer/profile
- GET /api/customer/documents
- GET /api/customer/consents
- POST /api/customer/consents/opt-out, /opt-in

## DB Collections
leads, contacts, customers, quotes, invoices, bookings, timeline_events, customer_memory, chat_sessions, outbound_leads, projects, project_sections, project_versions, contracts, contract_appendices, contract_evidence, documents, admin_users, suppression_list, legal_audit, legal_risks, messages, conversations, webhook_events, opt_outs

## Test Credentials
- Admin: p.courbois@icloud.com / 1def!xO2022!!

## Testing Status
- Iteration 55: 100% (22/22 backend, 20/20 frontend)
- Iteration 56: 100% (23/23 backend, all UI flows)

## Mocked Services
- DeepSeek LLM → Emergent GPT-5.2 mock (via EMERGENT_LLM_KEY)

## Upcoming/Backlog
- [ ] P3: Content & Copywriting Overhaul
- [ ] P4: DeepSeek Live-Migration (replace mock)
- [ ] P5: E2E Browser Verifications (Quote to Invoice)
- [ ] P7: server.py modular refactoring (after P1-P6 stable)
- [ ] Next.js Migration
- [ ] PydanticAI + LiteLLM + Temporal Adoption
