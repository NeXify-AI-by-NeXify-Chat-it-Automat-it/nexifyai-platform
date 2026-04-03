# NeXifyAI — Product Requirements Document

## Originalanforderung
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium-Architektur mit Unified Login Stack, Worker/Scheduler Layer, strikter Trennung Admin/Portal.

## Ziel-Architektur
- **LLM**: DeepSeek (PRIMÄR — LIVE) → Emergent GPT (Fallback)
- **Backend**: FastAPI + MongoDB + APScheduler
- **Frontend**: React 18 SPA
- **Auth**: JWT mit Rollen (Admin, Customer)
- **Payments**: Revolut (konfiguriert) + Stripe (ausstehend)
- **E-Mail**: Resend (PRODUKTIV — Audit-Trail aktiv)
- **Compliance**: Legal Guardian (DSGVO, UWG, EU AI Act)

## Commercial Source of Truth
- Starter AI Agenten AG — NXA-SAA-24-499 — 499,00 EUR netto / Monat — 24 Monate — 30% Aktivierungsanzahlung 3.592,80 EUR
- Growth AI Agenten AG — NXA-GAA-24-1299 — 1.299,00 EUR netto / Monat — 24 Monate — 30% Aktivierungsanzahlung 9.352,80 EUR

## Implementiert und verifiziert (Iteration 38)

### P1: DeepSeek LIVE — VERIFIZIERT
- DEEPSEEK_API_KEY gesetzt und aktiv
- LLM_PROVIDER=deepseek
- Health-Check: healthy (1682ms)
- Agent-Flow-Test: passed (Session-Kontinuität bestätigt)
- Öffentlicher Chat: über DeepSeek, Premium-Qualität
- Commercial Source of Truth: korrekt reproduziert (Growth-Tarif NXA-GAA-24-1299)
- Legal-Kontext: korrekte rechtliche Einordnung
- Emergent GPT als Fallback: operativ, automatische Umschaltung

### P2: Webhook-Härtung — VERIFIZIERT
- Revolut Signatur-Verifikation (HMAC-SHA256)
- Idempotente Webhooks mit webhook_events Collection
- Reconciliation-Endpoint (Quote ↔ Contract ↔ Invoice ↔ Payment)
- Webhook-History für Audit

### P3: Resend / E-Mail — VERIFIZIERT
- Resend produktiv (Test-E-Mail erfolgreich, resend_id bestätigt)
- Audit-Trail: email_events Collection (category, ref_id, status, resend_id)
- Alle kritischen Pfade mit Audit: portal_access, invoice, reminder, contract
- Admin-Endpoints: /api/admin/email/stats, /api/admin/email/test
- E-Mail-Template: CI-konform mit Impressum, Datenschutz, AGB, DSGVO

### P4: Contract PDF-Archivierung — VERIFIZIERT
- generate_contract_pdf: CI-branded PDF mit Kundeninfo, Finanzübersicht, Anlagen, Rechtsmodulen, Evidenzpaket
- Automatische PDF-Archivierung bei Vertragsannahme
- Admin: POST /api/admin/contracts/{id}/generate-pdf
- Download: GET /api/documents/contract/{id}/pdf (HTTP 200, valid PDF)
- Frontend: PDF-Button im Admin Contract-Detail
- has_pdf-Info im Admin- und Customer-Contract-Detail

### P5: E2E-Flow — VERIFIZIERT
- 6 Check-Typen: quote_has_invoice, contract_has_quote, payment_status_sync, reminder_on_paid, llm_provider_healthy, contract_evidence_complete
- 100% Pass Rate mit DeepSeek aktiv

### P6: Legal Guardian — VERIFIZIERT
- Legal Gate im Contract-Accept-Flow (Compliance-Check vor Annahme)
- Legal Gate im Outreach-Send-Flow
- Compliance-Summary, Risk Management, Audit Log

### P7: Monitoring Dashboard — VERIFIZIERT
- /api/admin/monitoring/status: Konsolidierter System-Status
- 10 Status-Cards: API, DB, Worker, Email, LLM/DeepSeek, Revolut, Stripe, Webhooks, Memory/Audit, Dead Letter
- Admin-UI: "Monitoring" Nav-Item mit Refresh

### P8: Outbound Machine — VERIFIZIERT
- Legal Gate im Send, Response-Tracking, Handover zu Quote/Meeting/Nurture

### Cookie-Banner/Chat-Fix — VERIFIZIERT
- Desktop (≥769px): body.cookie-visible .chat-trigger{bottom:100px}
- Smooth Transition: transition bottom 0.4s

## Testing
- Iteration 38: Backend 100% (15/15), Frontend 95% → Fix angewendet (PDF-Button)

## Ausstehend
- P9: server.py Modular Refactoring (>6000 Zeilen → modulare Routen)
- Stripe Live-Keys aktivieren
