# NeXifyAI — Product Requirements Document

## Originalanforderung
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium-Architektur mit Unified Login Stack, Worker/Scheduler Layer, strikter Trennung Admin/Portal.

## Ziel-Architektur
- **LLM**: DeepSeek (Primär) → Emergent GPT (Fallback)
- **Backend**: FastAPI + MongoDB + APScheduler
- **Frontend**: React 18 SPA
- **Auth**: JWT mit Rollen (Admin, Customer)
- **Payments**: Revolut + Stripe (Webhooks)
- **E-Mail**: Resend (produktiv)
- **Compliance**: Legal Guardian (DSGVO, UWG, EU AI Act)

## Commercial Source of Truth
- Starter AI Agenten AG — NXA-SAA-24-499 — 499,00 EUR netto / Monat — 24 Monate — 30% Aktivierungsanzahlung 3.592,80 EUR
- Growth AI Agenten AG — NXA-GAA-24-1299 — 1.299,00 EUR netto / Monat — 24 Monate — 30% Aktivierungsanzahlung 9.352,80 EUR

## Implementiert und verifiziert

### Cookie-Banner / Chat-Trigger Fix — VERIFIZIERT
- Desktop (≥769px): `body.cookie-visible .chat-trigger{bottom:100px}` → kein Overlap
- Tablet (768px): Cookie-Banner-Anpassung via Mobile-Regeln → kein Overlap
- Smooth Transition beim Dismissal: `transition: bottom 0.4s cubic-bezier(0.4,0,0.2,1)`

### P1: DeepSeek Live — TEILWEISE VERIFIZIERT
- Architektur produktionsbereit: Provider-Abstraktionsschicht mit Retry, Circuit-Breaker, Metriken
- `LLM_PROVIDER=deepseek` in .env gesetzt
- Fallback zu Emergent GPT funktioniert korrekt
- **Restrisiko**: DEEPSEEK_API_KEY nicht gesetzt → bei Key-Eingabe sofortige Umschaltung

### P2: Live-Provider-Webhooks — VERIFIZIERT
- Revolut Signatur-Verifikation (HMAC-SHA256)
- Reconciliation-Endpoint (Quote ↔ Contract ↔ Invoice ↔ Payment)
- Webhook-History für Audit
- Idempotente Verarbeitung

### P3: Resend / E-Mail-Delivery — VERIFIZIERT
- Resend produktiv: Test-E-Mail erfolgreich gesendet (resend_id bestätigt)
- Audit-Trail: email_events Collection mit category, ref_id, status, resend_id
- Admin-Endpoints: /api/admin/email/stats, /api/admin/email/test
- E-Mail-Template mit Impressum, Datenschutz, AGB, DSGVO

### P4: Portal-Finance-Ansicht — VERIFIZIERT
- /api/customer/finance: Rechnungen, Zahlungsstatus, Fälligkeit, Beträge, PDF, Payment-Links, Banküberweisung
- Summary mit total_outstanding, total_paid, open_invoices, overdue_invoices
- Mahnstufen-Anzeige, Premium-UX

### P5: Contract OS im Portal — VERIFIZIERT
- Versionshistorie, Evidenzpaket, Signatur-Vorschau, PDF-Download, Änderungsanfrage-Detail

### P6: E2E-Flow-Verifikation — VERIFIZIERT
- 6 Check-Typen: quote_has_invoice, contract_has_quote, payment_status_sync, reminder_on_paid, llm_provider_healthy, contract_evidence_complete
- 100% Pass Rate

### P7: Legal Guardian — VERIFIZIERT
- Legal Gate im Contract-Accept-Flow und Outreach-Send-Flow
- Compliance-Summary, Risk Management, Audit Log

### P8: Outbound Lead Machine — VERIFIZIERT
- Legal Gate im Send, Response-Tracking, Handover zu Quote/Meeting/Nurture

### Monitoring Dashboard — VERIFIZIERT (NEU)
- /api/admin/monitoring/status: Konsolidierter System-Status
- 10 Status-Cards: API, DB, Worker, Email, LLM, Revolut, Stripe, Webhooks, Memory/Audit, Dead Letter Queue
- Sichtbar im Admin unter "Monitoring"

## Testing
- Iteration 37: 100% (Backend 9/9, Frontend 100%, Cookie-Fix + Monitoring + Email + E2E)

## Ausstehend
- P9: server.py Modular Refactoring (>6000 Zeilen → modulare Routen)
- DEEPSEEK_API_KEY produktionsnah setzen und live testen
- Stripe Live-Keys aktivieren
- PDF-Archivierung in Object Storage (P4 aus User-Roadmap)
