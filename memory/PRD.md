# NeXifyAI — Product Requirements Document

## Produkt
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator (DeepSeek).

## Architektur
- **Frontend**: React 18 SPA
- **Backend**: FastAPI (Python 3.11) — Modular Route Architecture
- **Datenbank**: MongoDB (Motor async)
- **LLM**: DeepSeek (Primär), GPT-5.2 (Fallback via Emergent)
- **Object Storage**: Emergent Object Storage (für alle Dokumente)
- **Payments**: Stripe (via emergentintegrations)
- **E-Mail**: Resend (mit Audit-Trail)

## Modulare Backend-Architektur (v3.1)
```
server.py (419 Zeilen — Orchestrator)
routes/
├── shared.py       (405 — State Container S, Auth, Helpers)
├── auth_routes.py  (214 — Login, Magic Links, Me)
├── public_routes.py(~740 — Health, Contact, Booking, Chat, Products)
├── admin_routes.py (604 — CRM: Leads, Customers, Bookings)
├── billing_routes.py(1454 — Quotes, Invoices, Stripe, Documents)
├── portal_routes.py(711 — Customer Portal, Dashboard, Finance)
├── comms_routes.py (577 — Conversations, WhatsApp, Memory)
├── contract_routes.py(552 — Contract OS, Appendices, Evidence)
├── project_routes.py(564 — Projects, Sections, Handover)
├── outbound_routes.py(243 — Lead Machine)
├── monitoring_routes.py(567 — Monitoring, LLM, Workers, Audit, E2E)
```

## Domain-Modelle (17 Pflichtobjekte)
Contact, Lead, Conversation, Message, Timeline, Memory, WhatsAppSession, Project, ProjectSection, ProjectVersion, Contract, ContractAppendix, ContractEvidence, Payment, Audit, PromptHandover, BuildStatus, ReviewCycle, Deliverable

## Implementierungsstatus

### P0 — Restlücken-Verifikation (Abgeschlossen)
- Stripe: teilweise verifiziert (Test-Key aktiv, Webhook Secret benötigt Produktionskey)
- Object Storage: verifiziert (30/30 Dokumente)
- Monitoring: verifiziert (12 Subsysteme)

### P1 — server.py Modular Refactoring (Abgeschlossen)
- 6530 Zeilen Monolith → 10 modulare Route-Dateien + 419 Zeilen Orchestrator
- 0 API-Regression (Testing Iteration 40: 100% Pass)

### P2 — Domain-Layer-Härtung (Abgeschlossen)
- 17 Pflichtobjekte modelliert, 6 neue Factories, 5 neue Enums

### P3 — Memory/Audit Systematik (Abgeschlossen)
- write_classified(), audit_action(), audit_verified() mit Pflicht-Klassifizierung

### P4 — Legacy-Dokumente (Abgeschlossen)
- 29/29 MongoDB-Dokumente → Object Storage migriert

### P5 — UnifiedLogin UI/UX Perfektionierung (Abgeschlossen — 2026-02-04)
- Premium 2-Spalten-Design, Framer-motion, Trust-Badges
- Testing Iteration 41: 100% Pass (14/14)

### P6 — Chat-Bug + Mobile Floating Buttons (Abgeschlossen — 2026-02-04)
- Chat-Endpoint: get_system_prompt() + generate_response_fallback() fehlten nach Refactoring
- Mobile: body.chat-open CSS-Klasse → WhatsApp + ChatTrigger ausgeblendet bei Chat-Öffnung
- Testing Iteration 42: 100% Pass (Backend 8/8, Frontend alle Tests)

## Offene Punkte
- Stripe Webhook Secret (benötigt Produktionskey vom Kunden)
- Next.js Migration (Zielarchitektur)
- PydanticAI, LiteLLM, Temporal (Ziel-Stack)

## Admin Credentials
- Email: p.courbois@icloud.com
- Password: NxAi#Secure2026!
