# NeXifyAI — Product Requirements Document

## Originalanforderung
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator.

## Ziel-Architektur
- **LLM**: DeepSeek (PRIMÄR — LIVE) → Emergent GPT (Fallback)
- **Backend**: FastAPI + MongoDB + APScheduler
- **Frontend**: React 18 SPA
- **Auth**: JWT (Admin, Customer)
- **Payments**: Stripe (LIVE via emergentintegrations) + Revolut (konfiguriert)
- **E-Mail**: Resend (PRODUKTIV)
- **Storage**: Emergent Object Storage (LIVE) + MongoDB (Fallback)
- **Compliance**: Legal Guardian (DSGVO, UWG, EU AI Act)

## Status — Verifiziert (Iteration 39)

### Stripe Live — VERIFIZIERT
- Checkout-Sessions via emergentintegrations (echte Stripe-URLs)
- Status-Polling: /api/payments/checkout/status/{session_id}
- Webhook: /api/webhooks/stripe (idempotent, Signaturverifikation)
- Payment-Transaction-Tracking in payment_transactions Collection
- Automatische Invoice/Quote-Status-Synchronisation bei Zahlung

### Object Storage — VERIFIZIERT
- Emergent Object Storage initialisiert beim Start
- PDF-Archivierung: Verträge, Angebote, Rechnungen
- Download: Object Storage primär, MongoDB-Fallback
- Monitoring zeigt Storage-Status und Dokument-Verteilung

### Self-Healing/Recovery Dashboard — VERIFIZIERT
- 5 operative Recovery-Items: LLM, Dead Letter, Email, Payment, Storage
- Handlungsempfehlungen bei Problemen sichtbar
- Master-Agent kann Störungen klar erkennen

### Projekt Derived Status — VERIFIZIERT
- Phase-Kette: discovery → quote_pending → contract_pending → payment_pending → build_ready
- Admin: derived_status mit Quote/Contract/Invoice-Referenzen
- Customer: project_phase mit deutschen Labels

### DeepSeek LIVE — VERIFIZIERT
### Resend E-Mail — VERIFIZIERT (Audit-Trail aktiv)
### Contract PDF-Archivierung — VERIFIZIERT (Object Storage)
### Cookie-Banner/Chat-Fix — VERIFIZIERT
### Legal Guardian — VERIFIZIERT (Gates in Accept + Send Flows)
### Monitoring Dashboard — VERIFIZIERT (12 System-Status-Cards + Recovery)
### E2E-Flow — VERIFIZIERT (100% Pass)

## Ausstehend
- P7: server.py Modular Refactoring (>6500 Zeilen → modulare Routen)
