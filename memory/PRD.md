# NeXifyAI — Product Requirements Document

## Originaler Auftrag
B2B-Plattform "Starter/Growth AI Agenten AG" (NeXifyAI) — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium-Architektur mit absolutem Fokus auf Produktionsreife, Sicherheit und System-Konsistenz.

## Architektur
- **Frontend**: React 18 SPA, Framer Motion, i18n (DE/NL/EN), Shadcn-Style Dark Theme
- **Backend**: FastAPI (modular: 10 Route-Module), APScheduler, MongoDB
- **Workers**: In-process JobQueue (Retry + Dead-Letter), Cron-Scheduler (7 Jobs)
- **LLM**: DeepSeek (Primär), GPT-5.2 Fallback via Emergent
- **Integrations**: Stripe, Object Storage, Resend (E-Mail)
- **Security**: JWT Auth, Rate Limiting (SlowAPI 200/min), Security Headers (CSP, X-Frame-Options, XSS, Referrer-Policy), CORS

## Implementierte Features (kumulativ)

### Backend (verifiziert)
- Modulare Route-Architektur (auth, public, admin, billing, portal, comms, contract, project, outbound, monitoring)
- Worker/Scheduler-Layer: 8 Handler, 7 Scheduler-Jobs (Zahlungsreminder, Mahnungen, Follow-ups, Buchungserinnerungen, Angebotsablauf, Health-Check, Dead-Letter-Alert)
- Oracle/Memory Service: write_classified, get_contact_oracle(), Oracle Snapshot
- Billing Overview Dashboard API
- Outbound Campaigns API
- Monitoring Aliases (health, workers) + Memory Stats
- Rate Limiting (SlowAPI 200/min global)
- Triple-secured action logic (MongoDB + Timeline + Memory Audit)
- **FIXED**: QuoteRequest-Model (discount_percent, customer_industry, use_case, special_items Felder)
- **FIXED**: Invoice-aus-Quote-Erstellung (upfront_eur statt activation_fee_eur, auto-Beschreibung)
- **FIXED**: Contract-aus-Quote-Erstellung (auto-Populate Kundendaten, Tarif, Kalkulation)
- System Health Endpoint erweitert (Workers, Scheduler, Memory Checks)

### Frontend (verifiziert)
- Unified Login (2-Spalten Premium)
- Landing Page: 12 Sektionen
- Standalone Termin-Seite (/termin) — Premium 2-Spalten-Layout mit Trust-Signalen
- BookingModal (2-Step)
- LiveChat mit KI-Backend
- Legal Pages (Impressum, Datenschutz, AGB, KI-Hinweise) — 3 Sprachen
- Animated Pricing mit Custom Quote Request
- Customer Portal, Admin Dashboard (mit System Health Panel), Quote Portal
- **FIXED**: Registrierungsprozess (DSGVO-Checkbox, Trust-Row, verbesserter Erfolgsseite mit Booking-CTA)
- **FIXED**: UnifiedLogin Footer-Links (/de/impressum statt /impressum)
- **NEU**: Admin System-Health-Panel (6 Health-Cards: System, Datenbank, Workers, KI-Engine, Scheduler, Memory)

## E2E-Prozesskette (verifiziert)
Lead → Booking → Quote → Invoice → Contract → Payment (vollständig getestet)
- Contact-Formular → Lead-Erstellung ✅
- Termin-Buchung → Booking-Erstellung ✅
- KI-Chat → Response mit Preisinfo ✅
- Quote-Anfrage → Lead + Anfrage ✅
- Admin: Quote → Invoice (korrekte Beträge) ✅
- Admin: Quote → Contract (auto-populate) ✅

## Key API Endpoints
- `/api/health` — System Health
- `/api/auth/login` — Admin JWT Login
- `/api/booking`, `/api/booking/slots` — Terminbuchung
- `/api/contact` — Kontaktformular
- `/api/chat/message` — KI-Chat
- `/api/quote/request` — Angebotsanfrage
- `/api/admin/quotes` — Angebote CRUD
- `/api/admin/invoices` — Rechnungen CRUD
- `/api/admin/contracts` — Verträge CRUD
- `/api/admin/billing/overview` — Billing-Dashboard
- `/api/admin/outbound/campaigns` — Outbound-Kampagnen
- `/api/admin/oracle/snapshot` — Oracle IST-Stand
- `/api/admin/oracle/contact/{id}` — Kontakt-Oracle
- `/api/admin/memory/stats` — Memory-Statistiken
- `/api/admin/audit/health` — System-Gesundheit (mit Workers/Scheduler/Memory)
- `/api/admin/monitoring/health`, `/api/admin/monitoring/workers` — Monitoring-Aliase

## DB-Schema
leads, customers, quotes, invoices, bookings, contracts, projects, timeline_events, customer_memory, messages, chat_sessions, conversations, documents, audit_log, legal_audit, webhook_events, jobs, outbound_leads, contract_appendices, contract_evidence

## Testing Status
- Iteration 48: 100% (30/30) — Backend API + Frontend ✅
- Iteration 49: 100% (25/25) — Phase 2 Härtung + E2E ✅
- Alle Admin-Endpunkte: 200 ✅
- Worker: 4 aktiv, 7 Scheduler-Jobs ✅
- Oracle: Operational ✅
- Rate Limiting: Aktiv ✅
- Security Headers: Vollständig ✅
- E2E-Prozesskette: Quote → Invoice → Contract ✅

## Nächste Schritte (Backlog)
1. **P2**: Content & Copywriting Overhaul — perfektionierte Texte für alle Flows
2. **P3**: Security Hardening — CORS-Einschränkung für Produktion, Firewall-Regeln, Secrets-Audit
3. **P4**: E2E Browser-Verifikation aller kritischen Pfade
4. **P5**: DeepSeek Live-Migration
5. **P6**: Legal & Compliance Guardian
6. **P7**: Outbound Lead Machine Härtung
7. **P8**: Next.js Migration
8. **P9**: PydanticAI + LiteLLM + Temporal Adoption

## Credentials
- Admin: p.courbois@icloud.com / 1def!xO2022!!
