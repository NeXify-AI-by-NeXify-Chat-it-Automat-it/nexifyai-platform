# NeXifyAI — Technische Architektur-Dokumentation

## 1. Worker, Trigger & Monitoring — Bestandsnachweis

### 1.1 Aktive Worker / Dienste

| Worker | Typ | Trigger | Retry/Fallback | Status |
|--------|-----|---------|----------------|--------|
| **FastAPI Backend** | Supervisor-managed | Auto-Start, Hot-Reload | supervisorctl restart | AKTIV |
| **React Frontend** | Supervisor-managed | Auto-Start, Hot-Reload | supervisorctl restart | AKTIV |
| **MongoDB** | System-Dienst | Container-Start | Automatisch | AKTIV |
| **Orchestrator** | In-Process (FastAPI) | API-Call `/api/admin/agents/execute` | try/except + Audit-Log | AKTIV |
| **MemoryService** | In-Process (FastAPI) | Jeder Chat/CRUD | Inline-Error-Handling | AKTIV |
| **Email-Worker** | Async (asyncio.to_thread) | Quote-Send, Invoice-Send, Magic Link | try/except + Logger | AKTIV |

### 1.2 Trigger-Matrix

| Flow | Trigger | Worker | Audit | Memory |
|------|---------|--------|-------|--------|
| Login (Admin) | POST /api/admin/login | JWT-Generierung | `login_success`/`login_failed` | — |
| Login (Kunde) | POST /api/auth/verify-token | JWT-Generierung | `customer_login_magic_link` | Ja (system_agent) |
| Magic Link | POST /api/auth/request-magic-link | Email-Worker | `magic_link_requested` | — |
| Lead-Erstellung | POST /api/contact | Lead-Insert + Email | Timeline `lead_created` | — |
| Angebot versenden | POST /api/admin/quotes/{id}/send | Email-Worker + Access-Link | `quote_sent` + Timeline | Ja (admin_agent) |
| Rechnung erstellen | POST /api/admin/invoices | Invoice-Insert | Timeline `invoice_created` | — |
| Rechnung bezahlt | POST /api/admin/invoices/{id}/mark-paid | Status-Update | `invoice_marked_paid` | Ja (finance_agent) |
| Chat-Nachricht | POST /api/chat/message | KI-Orchestrator | Timeline (intern) | Ja (chat_agent) |
| Termin erstellen | POST /api/admin/bookings | Booking-Insert | Timeline `booking_created` | — |
| Portalzugang | POST /api/admin/customers/portal-access | Token-Generierung + Access-Link | Timeline `portal_access_created` | Ja (admin_agent) |
| Statuswechsel | PATCH /api/admin/quotes/{id} | Status-Update | Timeline `quote_status_*` | Ja (admin_agent) |

### 1.3 Monitoring-Endpunkte

| Endpunkt | Funktion | Prüfungen |
|----------|----------|-----------|
| `GET /api/health` | Basis-Healthcheck | Status + Version + Timestamp |
| `GET /api/admin/audit/health` | Erweiterter System-Health | DB-Ping, Collections, Agent-Layer, WA-Status, LLM-Key, Fehler-24h, Pricing |
| `GET /api/admin/audit/timeline` | Audit-Timeline | Alle Events der letzten N Stunden |
| `GET /api/admin/audit/collection-stats` | DB-Statistiken | Dokumentanzahl pro Collection |
| `GET /api/admin/memory/agents` | Memory-Agent-Status | Alle registrierten Agent-IDs |
| `GET /api/admin/memory/by-agent/{id}` | Agent-History | Memory-Einträge pro Agent |

### 1.4 Self-Healing & Fallback

| Szenario | Verhalten |
|----------|-----------|
| Email-Versand fehlgeschlagen | Logger.error + Audit-Eintrag, Operation fortgesetzt |
| LLM-Key fehlt | Health-Check meldet "missing", Chat-Fallback auf Standard-Antwort |
| MongoDB nicht erreichbar | Health-Check "error", Supervisor-Auto-Restart |
| Rate-Limit überschritten | HTTP 429, automatische Sperre für Window-Dauer |
| Token abgelaufen | HTTP 401/403, Client-Redirect zu /login |
| Agent-Execution fehlgeschlagen | try/except, Fallback-Antwort + Audit-Log |

### 1.5 Alerting

| Alert | Bedingung | Zielgruppe |
|-------|-----------|------------|
| `recent_errors_24h` | > 0 Fehler in Timeline | Admin (Audit-View) |
| `database.status == error` | MongoDB nicht erreichbar | Admin (Health-Check) |
| `agents.status == error` | Agent-Layer nicht verfügbar | Admin (Health-Check) |
| `llm.status == missing` | LLM-Key fehlt | Admin (Health-Check) |

### 1.6 Restrisiken

- **Kein separater Background-Worker**: Email-Versand und KI-Orchestrator laufen im FastAPI-Prozess. Bei hoher Last könnte dies den Hauptprozess beeinträchtigen.
- **Kein Mahnwesen-Cron**: Zahlungserinnerungen erfordern manuellen Admin-Eingriff.
- **Kein Webhook-Retry**: Eingehende WhatsApp-Webhooks werden einmalig verarbeitet.

---

## 2. KI-Orchestrator — Architektur

### 2.1 Aktueller Zustand: TEMPORÄR (GPT-5.2 via Emergent LLM Key)

Der KI-Orchestrator und alle 9 Sub-Agenten nutzen **GPT-5.2 über den Emergent LLM Key**. Dies ist eine funktionale Übergangslösung.

### 2.2 Agent-Architektur

```
Orchestrator (GPT-5.2)
├── intake_agent      — Leadaufnahme, Discovery, Klassifikation
├── research_agent    — Firmenanalyse, Lead-Enrichment
├── outreach_agent    — Erstansprache, Follow-ups
├── offer_agent       — Angebotserstellung, Tarifberatung
├── planning_agent    — Projektplanung, Architektur
├── finance_agent     — Rechnungsstellung, Zahlungen
├── support_agent     — Kundenbetreuung, Problemlösung
├── design_agent      — Design-Konzeption, SEO
└── qa_agent          — Qualitätssicherung, Audit
```

### 2.3 Guardrails

- Dedizierter System-Prompt pro Agent (`/app/backend/agents/`)
- Routing-Logik im Orchestrator
- Memory-Pflicht: read() vor Arbeit, write() nach Änderung
- Audit-Trail pro Execution
- Agenten empfehlen Aktionen, Business-Logik liegt in API-Endpunkten

### 2.4 Migrationspfad (DeepSeek / anderes LLM)

1. Neuen API-Key in `.env`
2. Model-Name in Agent-Definitionen ändern
3. System-Prompts ggf. optimieren
4. Regressionstests

### 2.5 Architektur-Grundsatz

- API-First bleibt führend
- LLM berät und formuliert, entscheidet nicht
- QR-WhatsApp = gekapselte Bridge, austauschbar

---

## 3. Email-Signatur & DSGVO-Footer

### Aktuelle Signatur (alle E-Mails)
Pascal Courbois — Geschäftsführer | Tel: +31 6 133 188 56 | nexifyai@nexifyai.de

### DSGVO-Footer (alle E-Mails)
NeXify Automate — Graaf van Loonstraat 1E, 5921 JA Venlo, NL | KvK: 90483944 | USt-ID: NL865786276B01
Impressum | Datenschutz | AGB | DSGVO (EU) 2016/679

Zentral über `email_template()` — konsistent in Lead-Bestätigung, Angebot, Rechnung, Magic Link, Statusbenachrichtigungen.

---

## 4. Kommerzielle Source of Truth

| Tarif | Kennung | Preis | Laufzeit | Anzahlung |
|-------|---------|-------|----------|-----------|
| Starter AI Agenten AG | NXA-SAA-24-499 | 499 EUR/Mo | 24 Mo | 30% = 3.592,80 EUR |
| Growth AI Agenten AG | NXA-GAA-24-1299 | 1.299 EUR/Mo | 24 Mo | 30% = 9.352,80 EUR |

Weitere: Website (2.990–14.900), Apps (9.900–24.900), SEO (799–1.499/Mo), Bundles (3.990–39.900+)
Zentral in `commercial.py` TARIFF_CONFIG.
