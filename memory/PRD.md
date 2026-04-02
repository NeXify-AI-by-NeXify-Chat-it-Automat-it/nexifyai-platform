# NeXifyAI — Product Requirements Document

## Product Vision
NeXifyAI by NeXify Automate: B2B-first KI-Agenten-Platform fuer DACH/Benelux. 
Landing Page + CRM + Commercial Engine + AI Chat Discovery.

## Core Requirements
- **Brand**: NeXifyAI (AI in CI-Farbe)
- **Languages**: DE (primary), NL, EN
- **Target**: Mittelstand B2B, DACH/Benelux
- **Authentication**: JWT Admin Login
- **3D UI**: Three.js Hero, Integrations Globe, Process Scene

---

## TARIFF MODEL (Single Source of Truth)

### 1. Starter AI Agenten AG (NXA-SAA-24-499)
- Tarifpreis: 499 EUR/Monat (netto)
- Vertragslaufzeit: 24 Monate
- Gesamtvertragswert: 11.976 EUR
- Aktivierungsanzahlung (30%): 3.592,80 EUR
- Monatliche Folgerate: 349,30 EUR (24 Raten)
- 2 KI-Agenten, Shared Cloud, E-Mail-Support (48h)

### 2. Growth AI Agenten AG (NXA-GAA-24-1299)
- Tarifpreis: 1.299 EUR/Monat (netto)
- Vertragslaufzeit: 24 Monate
- Gesamtvertragswert: 31.176 EUR
- Aktivierungsanzahlung (30%): 9.352,80 EUR
- Monatliche Folgerate: 909,30 EUR (24 Raten)
- 10 KI-Agenten, Private Cloud, Priority Support (24h), CRM/ERP-Kit

---

## Company Data
- Name: NeXify Automate
- KvK: 90483944
- USt-ID: NL865786276B01
- IBAN: NL66 REVO 3601 4304 36
- BIC: REVONL22
- Intermediary BIC: CHASDEFX

---

## Architecture
```
/app/
├── backend/
│   ├── server.py (FastAPI, MongoDB, JWT, LLM Chat, Admin, Commercial Routes)
│   ├── commercial.py (Tariff Config, PDF Engine, Revolut API, Magic Links, FAQ)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.js (Landing Page, 3D, Chat with AI Discovery)
│   │   ├── App.css
│   │   ├── index.js (Routing: /, /de, /nl, /en, /admin, /angebot)
│   │   ├── i18n/ (LanguageContext.js, translations.js)
│   │   └── pages/ (Admin.js, LegalPages.js, QuotePortal.js)
│   └── package.json
└── memory/ (PRD.md, test_credentials.md)
```

---

## Implemented Features

### Phase 1: Landing Page & Brand (DONE)
- 3D Hero, Integrations Globe, Process Scene
- Multi-language (DE/NL/EN)
- Responsive Design, SEO, Cookie Consent
- Legal Pages (Impressum, Datenschutz, AGB, KI-Hinweise)

### Phase 2: AI Chat & Lead System (DONE)
- Emergent LLM Chat with booking flow
- Lead capture, qualification, analytics tracking
- Contact form with validation
- Email notifications via Resend

### Phase 3: Admin CRM (DONE)
- Admin login (JWT)
- Dashboard with stats
- Leads management (CRUD, status updates)
- Calendar (bookings, blocked slots)
- Customer database

### Phase 4: Commercial Engine v2.0 (DONE — Current Session)
- Central Tariff Config (Single Source of Truth)
- Quote management (create, send, PDF, magic links)
- Invoice engine (deposit, monthly, PDF generation)
- Customer Quote Portal (/angebot) with accept/decline/revision
- AI Chat Discovery flow (auto-generates quotes)
- Revolut integration (orders, webhooks, fallback to bank transfer)
- Admin Commercial Dashboard (quotes, invoices, stats, revenue)
- FAQ with 15 entries (tariffs, payment, bank details, DSGVO)
- All translations updated (DE/NL/EN)
- 100% test coverage (23/23 backend, all frontend verified)

---

## Pending / Backlog

### P1 — Upcoming
- E-Mail delivery: Connect Resend to all commercial events (currently backend-ready, needs live Resend key)
- Secure Customer Portal refinement: add document list view, invoice download
- SMTP fallback (Hostinger: nexifyai@nexifyai.de)

### P2 — Future
- DeepSeek/Mem0 integration for persistent chat memory
- Monthly recurring invoice auto-generation (cron/scheduler)
- Revolut Subscription API for recurring payments
- Admin CSV export
- App.js refactoring (>740 lines)
- Lighthouse performance optimization
- A/B testing framework

---

## 3rd Party Integrations
| Service | Status | Key Location |
|---------|--------|-------------|
| Emergent LLM | Active | backend/.env |
| Resend | Active | backend/.env |
| Revolut Merchant API | Test keys | backend/.env |
| MongoDB | Active | backend/.env |

---

## Test Reports
- Iteration 13: 100% tests PASSED (23/23 backend, all frontend verified)
- Test file: /app/backend/tests/test_commercial_engine.py
