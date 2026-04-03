# NeXifyAI — Product Requirements Document

## Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" — API-First, Unified Communication, Deep Customer Memory (mem0), KI-Orchestrator, Manuelles CRM, Gemeinsamer Login-Stack, Dynamische Floating Actions.

## Architecture
- **API-First**: Domain → Channel → Connector → Agent → Event/Audit Layer
- **Unified Auth**: /login → Admin (Passwort) / Kunde (Magic Link) → Role-based JWT
- **mem0 Memory Layer**: Pflicht-Scoping (user_id, agent_id, app_id, run_id)
- **KI-Orchestrator**: GPT-5.2 via Emergent LLM Key (MOCKED, temporär — Migrationspfad dokumentiert)

## What's Implemented & Verified

### Auth & Login — VERIFIZIERT
- Login-Button im Public Header (Desktop/Tablet/Mobile, i18n DE/NL/EN)
- /login als allgemeine Auth-Seite (Home-Link, Legal: Impressum/Datenschutz/AGB)
- Admin-Flow (E-Mail → Rollen-Badge → Passwort → /admin)
- Kunden-Flow (E-Mail → Magic Link → /portal)
- JWT Rollentrennung (admin/customer), serverseitig + UI-seitig

### Admin CRM — VERIFIZIERT
- Vollständige Arbeitsoberfläche: Leads/Kunden/Angebote/Rechnungen/Termine CRUD
- Rabatt, Sonderpositionen, Status, Notizen, Audit-Trail
- KI-Agenten-Steuerung, Kommunikation, Timeline

### Customer Portal — VERIFIZIERT
- JWT-Auth + Legacy Magic Link, Dashboard mit Angeboten/Rechnungen/Terminen
- Logout, Login-Link bei Fehler

### Mobile Floating Actions — VERIFIZIERT
- Dynamisch: Cookie → bottom:120px, kein Cookie → bottom:24px (Delta 96px bewiesen)
- CSS transition 0.4s, z-index 910, Safe-Area iOS

### Kommerzielle Konsistenz — VERIFIZIERT (Code)
- Rabatt + Sonderpositionen in Quote-PDF und Invoice-PDF

### Breakpoint-Testing — VERIFIZIERT
- 11 Breakpoints (1920→360): Nav, Login-Button, Floating Actions, Login-Seite alle OK
- Floating Actions Cookie-Wechsel dynamisch bewiesen (120px → 24px)

### Worker/Monitoring/Alerting — DOKUMENTIERT
- 6 Worker, 11 Trigger, 6 Monitoring-Endpunkte, 4 Alerts, Self-Healing
- Dokumentiert in TECHNICAL_DOCS.md

### Orchestrator-Architektur — DOKUMENTIERT
- 9 Agenten + Orchestrator, Guardrails, Migrationspfad
- Dokumentiert in TECHNICAL_DOCS.md

### Email-Signatur & DSGVO — VERIFIZIERT
- Zentrale email_template() mit Signatur + DSGVO-Footer
- Impressum/Datenschutz/AGB Links, KvK, USt-ID

### mem0 Memory Layer — VERIFIZIERT
- MemoryService, 13 Agent-IDs, Pflicht-Scoping

## Testing Status
- Iteration 21: 100% | 22: 100% | 23: 100% | 24: 100%
- Breakpoints: 11/11 bestanden

## Remaining Tasks
- P2: Outbound Lead Machine
- P2: server.py Refactoring (>3900 Zeilen → modulare Struktur)
- P2: Kanalübergreifender Kommunikationskern vollenden
- P2: Revolut/Billing/Status-Sync
