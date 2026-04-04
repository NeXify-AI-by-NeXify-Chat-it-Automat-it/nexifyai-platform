# NeXifyAI — Product Requirements Document

## Produkt
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator (DeepSeek).

## Architektur
- **Frontend**: React 18 SPA (React Router v6, Framer Motion, Three.js)
- **Backend**: FastAPI (Python 3.11) — 10 modulare Route-Dateien
- **Datenbank**: MongoDB (Motor async, 35 Collections)
- **LLM**: DeepSeek (Primär), GPT-5.2 (Fallback via Emergent)
- **Object Storage**: Emergent Object Storage
- **Payments**: Stripe (via emergentintegrations)
- **E-Mail**: Resend (mit Audit-Trail)
- **Background Jobs**: APScheduler + Job Queue + Dead Letter Queue

## Backend-Module
```
server.py → routes/
├── shared.py (State Container S)
├── auth_routes.py, public_routes.py, admin_routes.py
├── billing_routes.py, portal_routes.py, comms_routes.py
├── contract_routes.py, project_routes.py
├── outbound_routes.py, monitoring_routes.py
services/ → billing, comms, llm_provider, outbound, storage
workers/ → manager, job_queue, scheduler
```

## System-Audit (2026-02-04, Iteration 45) — VOLLSTÄNDIG VERIFIZIERT

### APIs (26/26 Tests bestanden)
| Endpoint | Status |
|---|---|
| /api/health | 200 |
| /api/admin/stats | 200 (47 Leads, 15+ Buchungen) |
| /api/admin/leads | 200 |
| /api/admin/customers | 200 |
| /api/admin/calendar-data | 200 |
| /api/admin/quotes | 200 |
| /api/admin/invoices | 200 |
| /api/admin/projects | 200 |
| /api/admin/contracts | 200 |
| /api/admin/chat-sessions | 200 |
| /api/admin/agents | 200 |
| /api/admin/activities | 200 |
| /api/admin/billing/status | 200 |
| /api/admin/outbound/pipeline | 200 |
| /api/admin/workers/status | 200 |
| /api/admin/monitoring/status | 200 |
| /api/contact | 200 |
| /api/booking | 200 |
| /api/booking/slots | 200 |
| /api/chat/message | 200 |
| /api/auth/check-email | 200 |
| /api/product/tariffs | 200 |
| /api/product/tariff-sheet | 200 |

### Monitoring (12 Subsysteme)
- API v3.0.0, Datenbank (35 Collections), Worker/Queue
- E-Mail (Resend), LLM/DeepSeek, Revolut, Stripe
- Webhooks (28 Events), Memory/Audit, Dead Letter Queue
- Object Storage, Dokumente

### Frontend (Alle Flows)
- Landing Page: Hero + 3D + 9 Sektionen + Footer
- Login: Admin + Customer + Registrierung
- Admin: 16 Sidebar-Views funktionsfähig
- Booking Modal: Premium 2-Step Design
- Chat: Desktop + Mobile mit Avataren, Timestamps, AI-Disclaimer
- Legal: 4 Seiten in DE/NL/EN
- Responsive: 1920px, 1024px, 768px, 375px

## Implementierte Features
1. Backend Modular Refactoring (P7 → vorgezogen, 6530→10 Module)
2. Domain Layer Hardening (17 Modelle)
3. Memory/Audit Systematik (write_classified, audit_action)
4. Legacy MongoDB→Object Storage Migration (29 Dokumente)
5. UnifiedLogin Premium (2-Spalten, Framer-motion)
6. Chat-Bug-Fix (generate_response_fallback)
7. Chat Premium (Avatare, Timestamps, Mobile-Header, Disclaimer)
8. Booking Modal Premium (2-Step, Progress, Datums-Karten)
9. Legal (Datenschutz-Fix, KI-Hinweise)
10. Contact Form (source+language)
11. System-wide Audit (Iteration 45: 100%)

## Offene Punkte
- Stripe Webhook Secret (Produktionskey)
- Master-Auftrag Items
- Next.js Migration (Zielarchitektur)
- PydanticAI + LiteLLM + Temporal
- Chatwoot / Cal.com / Documenso
- PostHog / Grafana

## Admin Credentials
- Email: p.courbois@icloud.com
- Password: NxAi#Secure2026!
