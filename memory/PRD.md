# NeXifyAI — Product Requirements Document

## Original Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium, hochsichere Architektur. Unified Login Stack, Worker/Scheduler Layer, Revolut-only Billing, vollständige Outbound Lead Machine mit Lead-Scraping und Kontaktaufnahme.

## Tech Stack
- **Frontend**: React 18 SPA (CRA), Shadcn/UI components
- **Backend**: FastAPI (Python), modular routing
- **Database**: MongoDB (via MONGO_URL)
- **Auth**: JWT, Dual-Role (Admin/Kundenportal), OAuth2 form-encoded login
- **Workers**: APScheduler (Background Jobs, Queue, Dead-Letter)
- **Email**: Hostinger SMTP
- **LLM**: DeepSeek (Target) — currently routed through Emergent GPT-5.2 mock
- **Payments**: Revolut ONLY (Stripe removed)
- **Storage**: emergentintegrations Object Storage

## Core Modules (Implemented & Verified)
1. **Unified Login Stack** — 2-step flow: Email -> Role Selection -> Password -> Panel
2. **Admin Portal** — 17 navigation views (Dashboard, Projekte, Verträge, Billing, Outbound, Legal, Angebote, Leads, Kommunikation, KI-Chats, WhatsApp, Aktivitäten, Kalender, Kunden, KI-Agenten, Audit, Monitoring)
3. **Outbound Lead Machine (P6)** — Full CRUD, Pipeline Stats, Lead Discovery, Prequalify, Analyze & Score, Legal-Check, Outreach Creation/Sending, Follow-up, Response Tracking, Handover (Angebot/Termin/Nurture), Bulk Import, Opt-Out
4. **Project Management (P1)** — CRUD, 22 Section Types, Section Editor, Build-Handover Markdown Generation, Project Chat
5. **Contract OS (P2)** — CRUD, Modulare Anhänge, Rechtsmodule, Evidenzpaket (Timestamp/IP/Hash), PDF Generation, Digital Acceptance
6. **Customer Case File (Kunden-Fallakte)** — Direct Email, Notes, Timeline, Memory
7. **Billing Dashboard** — Revolut-only, Quotes/Invoices/Revenue
8. **Legal & Compliance Guardian** — Risk Assessment, Audit Log, Gate Decisions, Opt-Outs
9. **System Monitoring** — API, DB, Workers, Email, LLM, Payments, Webhooks, Dead-Letter Queue, Object Storage, Documents
10. **Design System** — Unified First-Class UI (CSS Tokens, Premium Shadows, Depth System)
11. **Worker/Scheduler Layer** — APScheduler, Job Queue (send_email, payment_reminder, dunning, lead_followup, booking_reminder, quote_expiry, ai_task, status_transition)

## API Endpoints
- POST /api/admin/login (OAuth2 form-encoded)
- GET/POST /api/admin/outbound/discover, /leads, /pipeline, /bulk-import, /{id}/prequalify, /analyze, /legal-check, /outreach, /followup, /respond, /handover
- GET/POST /api/admin/projects, /{id}/sections, /{id}/chat, /{id}/build-handover
- GET/POST /api/admin/contracts, /{id}/appendices, /{id}/send, /{id}/generate-pdf
- GET /api/admin/stats, /billing/status, /legal/compliance, /monitoring/status

## DB Collections
leads, contacts, customers, quotes, invoices, bookings, timeline_events, customer_memory, chat_sessions, outbound_leads, projects, project_sections, project_versions, contracts, contract_appendices, contract_evidence, documents, admin_users, suppression_list, legal_audit, legal_risks, messages, conversations

## Test Credentials
- Admin: p.courbois@icloud.com / 1def!xO2022!!

## Completed (verifiziert)
- [x] Unified Login with Dual-Role Selection
- [x] Admin Dashboard with correct stat mapping
- [x] System-wide Design System Harmonization
- [x] Stripe removal (Revolut only)
- [x] Customer Case File with Email
- [x] React Hooks crash fix
- [x] Login infinite redirect loop fix
- [x] Outbound Lead Machine (Full Production CRUD + Pipeline) — Iteration 55, 100%
- [x] Project Management (CRUD + Sections + Chat + Build-Handover) — Iteration 55, 100%
- [x] Contract OS (CRUD + Appendices + Legal Modules + Evidence) — Iteration 55, 100%
- [x] Worker/Scheduler Layer (APScheduler, Queue, Dead-Letter)

## Upcoming (P3-P7)
- [ ] P3: Content & Copywriting Overhaul
- [ ] P4: Network, Security & Configuration Hardening (CORS, Rate Limiting)
- [ ] P5: E2E Browser Verifications (Quote to Invoice)
- [ ] P7: server.py modular refactoring (auth_routes, workers_routes, etc.)

## Future / Backlog
- [ ] Next.js Migration
- [ ] PydanticAI + LiteLLM + Temporal Adoption
- [ ] DeepSeek Live-Migration (replace Emergent GPT-5.2 mock)
