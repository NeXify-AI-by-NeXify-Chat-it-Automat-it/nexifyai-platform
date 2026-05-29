# System 2 — Agenturstruktur & CRM

spec_id: SYS-002 | version: 2.0 | date: 2026-05-30 | owner: crm-automation-specialist
Status: IMPLEMENTED (Phase 2 vollstaendig)

---

## 1. CRM ARCHITECTURE

| Component | Technologie | Status |
|-----------|-------------|--------|
| Backend | FastAPI + MongoDB | 🟢 Aktiv |
| Auth | JWT via Supabase Auth + Magic Link | 🟢 Aktiv |
| Frontend | React (QuotePortal.jsx, CustomerPortal.jsx) | 🟢 Aktiv |
| Kommunikation | CommunicationService (kanaluebergreifend) | 🟢 Aktiv |
| KI | Oracle Engine + Agent Orchestrator | 🟢 Aktiv |
| E-Mail | Resend API | 🟢 Aktiv |

## 2. CUSTOMER PORTAL — Backend Endpoints

| Endpoint | Funktion | Status |
|----------|---------|--------|
| GET /api/customer/dashboard | Projektuebersicht | 🟢 |
| GET /api/customer/finance | Finanzuebersicht (Rechnungen, Zahlungen) | 🟢 |
| GET /api/customer/profile | Kundenprofil | 🟢 |
| PATCH /api/customer/profile | Profil aktualisieren | 🟢 |
| GET /api/customer/documents | Dokumente | 🟢 |
| GET /api/customer/consents | Einwilligungen | 🟢 |
| POST /api/customer/consents/opt-out | Opt-Out | 🟢 |
| POST /api/customer/consents/opt-in | Opt-In | 🟢 |
| POST /api/customer/requests | Anfrage erstellen | 🟢 |
| GET /api/customer/requests | Anfragen auflisten | 🟢 |
| POST /api/customer/bookings | Termin buchen | 🟢 |
| POST /api/customer/messages | Nachricht senden | 🟢 |
| GET /api/customer/messages | Nachrichten abrufen | 🟢 |
| GET /api/customer/sla | **SLA-Status (NEU in Phase 2)** | 🟢 |
| POST /api/customer/support-tickets | Support-Ticket erstellen | 🟢 |
| GET /api/customer/support-tickets | Tickets auflisten | 🟢 |

## 3. QUOTE PORTAL

| Endpoint | Funktion | Status |
|----------|---------|--------|
| GET /api/portal/quote/{id} | Angebot abrufen | 🟢 |
| POST /api/portal/setup-account | Konto erstellen | 🟢 |
| POST /api/portal/quote/{id}/accept | Angebot annehmen | 🟢 |
| POST /api/portal/quote/{id}/decline | Angebot ablehnen | 🟢 |
| POST /api/portal/quote/{id}/revision | Ueberarbeitung anfordern | 🟢 |

## 4. TICKET SYSTEM

Status: IMPLEMENTED (Backend + Frontend)

Flow: TICKET_CREATED -> TRIAGE -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
  (mit REJECTED und ESCALATED -> CEO als Nebenpfaden)

Priority Mapping: P0-P3 via Oracle Engine Routing Matrix.

## 5. SLA SYSTEM

Status: IMPLEMENTED (NEU in Phase 2)

| Tier | Response | Resolution | Support Hours | Priority |
|------|----------|------------|---------------|----------|
| Enterprise | 15 min | 4h | 24/7 | P0-P1 |
| Business | 1h | 8h | Business hours | P1-P2 |
| Standard | 4h | 24h | Business hours | P2-P3 |

Endpoint: GET /api/customer/sla (tarifabhaengig)

## 6. COMMUNICATION PIPELINE

| Channel | Direction | Implementierung | Status |
|---------|-----------|----------------|--------|
| E-Mail | Inbound/Outbound | Resend API | 🟢 |
| Chat (Web) | Inbound/Outbound | Admin Chat Gateway | 🟢 |
| Kundenportal | Inbound/Outbound | JWT-Auth | 🟢 |
| WhatsApp | Inbound/Outbound | Telegram Bridge | 🟢 |

## 7. OUTBOUND LEAD MACHINE

| Pipeline-Schritt | Status |
|-----------------|--------|
| Discovery | 🟢 |
| Vorqualifizierung | 🟢 |
| KI-Website-Analyse | 🟢 |
| Legal Gate | 🟢 |
| KI-Outreach | 🟢 |
| KI-Follow-up | 🟢 |
| Bulk-Import | 🟢 |

## 8. AGENT INTEGRATION

| Agent | Rolle via Oracle Engine |
|-------|----------------------|
| Care | Customer Success, CRM, Support, Retention |
| Forge | Technische Umsetzung |
| Scout | Marktforschung, Monitoring |
| Scribe | Content, E-Mail |

## 9. CONSTRAINTS (unveraenderlich)

- NEVER: Client data in plain text logs
- NEVER: Ticket without priority assessment
- NEVER: Communication without audit trail
- NEVER: Outreach ohne Legal Gate (legal_guardian.py)