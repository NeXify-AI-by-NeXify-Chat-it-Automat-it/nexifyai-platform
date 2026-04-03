# NeXifyAI — Product Requirements Document

## Originalauftrag
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator. Premium, hochsichere Architektur. Unified Login Stack, Worker/Scheduler Layer, Admin/Agenten strikt nicht öffentlich. Ziel-LLM: DeepSeek.

## Architektur
```
/app/
├── backend/
│   ├── server.py (FastAPI, >5500 Zeilen)
│   ├── commercial.py (PDF-Generation, Tarife)
│   ├── domain.py (Datenmodelle, Enums, Factories)
│   ├── memory_service.py (mem0-Integration)
│   ├── services/
│   │   ├── billing.py (BillingService)
│   │   ├── comms.py (CommunicationService)
│   │   ├── outbound.py (OutboundLeadMachine)
│   │   ├── llm_provider.py (LLM-Abstraktionsschicht)
│   │   └── legal_guardian.py (Legal & Compliance Guardian)
│   ├── workers/ (manager, job_queue, scheduler)
├── frontend/
│   ├── src/
│   │   ├── App.js & App.css
│   │   ├── pages/
│   │   │   ├── Admin.js (Alle Admin-Views inkl. Projekte, Verträge, Billing, Outbound, Legal)
│   │   │   ├── CustomerPortal.js (Verträge mit Signatur, Projekte mit Chat)
│   │   │   └── UnifiedLogin.js
│   │   └── components/Scene3D.js
```

## Tarife (Commercial Source of Truth)
- Starter AI Agenten AG — NXA-SAA-24-499 — 499 EUR/Monat — 24 Monate — 30% Anzahlung 3.592,80 EUR
- Growth AI Agenten AG — NXA-GAA-24-1299 — 1.299 EUR/Monat — 24 Monate — 30% Anzahlung 9.352,80 EUR

## DB-Schema (MongoDB)
leads, customers, quotes, invoices, bookings, timeline_events, customer_memory, messages, conversations, projects, project_sections, project_chat, project_versions, contracts, contract_appendices, contract_evidence, webhook_events, legal_audit, legal_risks, opt_outs, suppression_list, outbound_leads, access_links, documents

## Implementiert und verifiziert

### P0: Architektur & Design (verifiziert — Iter 25-27)
- Worker/Scheduler Layer (APScheduler), Services-Scaffolding, Auth Security by Obscurity, 3D Hero, Design-Harmonisierung

### P1 Backend: Projektchat / Build-Handover-Kontext (verifiziert — Iter 28)
- 22 Pflicht-Sektionen mit Versionierung, Projektchat (Admin + Kunden), Build-Ready-Markdown-Generierung, Startprompt (geheim), Vollständigkeits-Tracking, Download-Endpoint

### P2 Backend: Contract Operating System v1 (verifiziert — Iter 29)
- Mastervertrag + 7 Anlagetypen, 3 Vertragstypen, Digitale Annahme mit Evidenzpaket, 6 Rechtsmodule, Ablehnung / Änderungsanfrage / Versionierung

### P3 Backend: Billing/Webhooks (verifiziert — Iter 30)
- Revolut + Stripe Webhooks (idempotent), Manuelle Zahlungsbestätigung, Reminder/Mahnlogik (3 Stufen), Billing-Status-Dashboard, Status-Sync

### P4 Backend: Legal & Compliance Guardian (verifiziert — Iter 31)
- 10 Compliance-Checks, 4 Gate-Prüfungen, Risikomanagement, Audit-Log, Opt-Out, Operativ an Vertragsversand gekoppelt

### P5 Backend: DeepSeek Live-Pfad (teilweise verifiziert — Iter 32)
- Provider-Abstraktionsschicht, ENV-basierte Umschaltung, Test-Endpoint. DEEPSEEK_API_KEY nicht gesetzt → Emergent-Fallback aktiv

### P6 Backend: Outbound Lead Machine (verifiziert — Iter 32)
- 16-stufige Pipeline, Legal-Guardian-Gate, Response-Tracking, Handover (Quote/Meeting/Nurture)

### Neue P1 Frontend: Kundenportal Vertragsansicht + Signatur (verifiziert — Iter 33)
- Signatur-Canvas (Touch/Maus), Namenseingabe, Rechtsmodul-Checkboxen, Accept/Decline/Änderungsanfrage, Evidenzpaket, Statusmeldungen

### P2-P7 Frontend: Sichtbarkeitsschicht (verifiziert — Iter 34)
- Admin: Billing-Dashboard, Outbound-Pipeline-View, Legal Guardian View
- Admin: Projekt Download-Handover, Startprompt-Endpoint
- Kundenportal: Projekte-Tab mit Detail, Sektionen, Chat, Build-Handover

## Nächste Schritte

### P8: server.py Modular Refactoring
- auth_routes.py, portal_routes.py, contract_routes.py, billing_routes.py, outbound_routes.py, comms_routes.py, monitoring_routes.py, workers_routes.py
- Keine Regression, bestehende APIs stabil

## Offene Punkte
- DEEPSEEK_API_KEY: Vom Kunden zu konfigurieren
- Revolut/Stripe Live-Keys: Benötigen Produktions-Credentials
- Portal-Finance-Ansicht: Rechnungen/Zahlungsstatus im Kundenportal noch nicht sichtbar
