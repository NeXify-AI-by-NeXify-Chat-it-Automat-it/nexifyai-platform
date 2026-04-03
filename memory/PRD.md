# NeXifyAI — Product Requirements Document

## Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" mit API-First Architektur. Unified Communication Layer (Chat, Mail, WhatsApp, Portal), Deep Customer Memory (mem0), KI-Orchestrator mit 9 Sub-Agents, Manuelles CRM als vollständige Arbeitsoberfläche, Dynamische Mobile Floating Actions.

## Source of Truth — Gesamtkonzept
1. `NeXifyAI_Emergent_Auftrag_Premium_FineTuned_20260403.txt` — Auftragsspezifikation
2. `NeXifyAI_Gesamtkonzept_Premium_FineTuned_20260403 (1).md` — Architektur & Features
3. `NeXifyAI_Gesamtkonzept_Premium_FineTuned_20260403 (2).md` — Design System, Format, QA
4. `NeXifyAI_Emergent_Zusatzauftrag_Memory_Beweispflicht_20260403.txt` — Memory & Beweispflicht

## Architecture
- **API-First**: Domain Layer, Channel Layer, Connector Layer, Agent Layer, Event/Audit Layer
- **mem0 Memory Layer**: Pflicht-Scoping (user_id, agent_id, app_id, run_id), MemoryService als zentraler Dienst
- **Unified Communications**: AI-Chat, Email, WhatsApp, Portal in einer Timeline/Identity
- **KI-Orchestrator**: GPT-5.2 via Emergent LLM Key mit 9 Sub-Agents

## Tech Stack
- Frontend: React 18 SPA
- Backend: FastAPI + Motor (MongoDB async)
- Database: MongoDB (nexifyai)
- LLM: Emergent LLM Key (OpenAI GPT-5.2)
- Email: Resend API
- Memory: mem0-konformer MemoryService

## What's Implemented

### Admin CRM — Vollständige Arbeitsoberfläche (DONE — 2026-04-03)
Alle Daten sind nicht nur sichtbar, sondern vollständig bearbeitbar:
- **Leads**: Anlegen, Bearbeiten (alle Felder), Status ändern, Notizen, Edit-Modal
- **Kunden**: Anlegen, Bearbeiten (alle Felder), Edit-Modal, Portalzugang generieren
- **Angebote**: Erstellen (mit Tarif, Rabatt, Sonderpositionen), Bearbeiten (Status, Rabatt, Felder), Versenden, Kopieren, PDF, Versionierung
- **Rechnungen**: Erstellen (aus Angebot), Bearbeiten (Status, Zahlungsstatus, Notizen), Als bezahlt markieren, Versenden, PDF
- **Termine**: Manuell anlegen (Kalender-Modal), Bearbeiten (Status, Datum, Zeit), Notizen, Löschen
- **Slots blockieren**: Anlegen, Löschen
- **Kommunikation**: Konversationen einsehen + inline antworten (Chat, WA, Email, Admin)
- **KI-Agenten**: Aufgaben an einzelne Agenten oder Orchestrator senden
- **Audit**: System-Health, Timeline, Collection-Stats

### Dynamische Mobile Floating Actions (DONE — 2026-04-03)
- WhatsApp + Chat **side-by-side** unten rechts auf Mobile (<768px)
- **Zustandsbasiert**: Cookie-Banner sichtbar → bottom:120px, Cookie weg → bottom:24px
- **Smooth Transition**: 0.4s cubic-bezier, kein Sprung, kein Geisterabstand
- CSS-Klasse `body.cookie-visible` steuert Position
- z-index 910 (über Cookie-Banner 300)
- Safe-Area iOS-kompatibel

### mem0 Memory Layer (DONE — 2026-04-03)
- MemoryService (backend/memory_service.py) als zentraler Pflicht-Layer
- Pflicht-Scoping: user_id, agent_id, app_id, run_id pro Eintrag
- 13 definierte Agent-IDs
- read/write/search/get_agent_history Methoden
- Automatische Memory-Writes im Chat-Flow + Admin CRUD
- Admin API: /memory/agents, /by-agent/{id}, /search

### Customer Portal (DONE)
- 6 Tabs: Übersicht, Angebote, Rechnungen, Termine, Kommunikation, Aktivität
- Quote Accept/Decline/Revision via Magic Link
- PDF-Downloads

### KI-Orchestrator + 9 Sub-Agents (DONE)
- Orchestrator mit GPT-5.2 Routing
- 9 spezialisierte Agenten

### Premium Admin Login (DONE)
- Redesigned, komplett Deutsch

## Key API Endpoints
- `POST /api/admin/leads` — Lead anlegen
- `PATCH /api/admin/leads/{lead_id}` — Lead bearbeiten (alle Felder)
- `POST /api/admin/customers` — Kunde anlegen
- `PATCH /api/admin/customers/{email}` — Kunde bearbeiten
- `POST /api/admin/customers/portal-access` — Portalzugang erstellen
- `POST /api/admin/quotes` — Angebot erstellen
- `PATCH /api/admin/quotes/{quote_id}` — Angebot bearbeiten
- `POST /api/admin/quotes/{quote_id}/send` — Angebot versenden
- `POST /api/admin/quotes/{quote_id}/copy` — Angebot kopieren
- `POST /api/admin/invoices` — Rechnung erstellen
- `PATCH /api/admin/invoices/{invoice_id}` — Rechnung bearbeiten
- `POST /api/admin/invoices/{invoice_id}/mark-paid` — Als bezahlt markieren
- `POST /api/admin/bookings` — Termin manuell anlegen
- `PATCH /api/admin/bookings/{booking_id}` — Termin bearbeiten
- `GET /api/admin/memory/agents` — Agent-IDs
- `GET /api/admin/memory/by-agent/{id}` — Memory pro Agent
- `GET /api/admin/memory/search` — Memory-Suche

## Pending Tasks
- P1: Gemeinsamer Login-Stack (Admin + Kunde über gleichen Einstieg, Rollentrennung)
- P1: Kundenzugangslogik ab Angebotsanfrage systemisch (Lead→Kunde→Portal automatisch)
- P1: Kommerzielle Konsistenz (Rabatt/Sonderpositionen in PDF/Portal/Rechnung synchron)
- P1: Admin/Portal UX Feintuning
- P1: Email-Signatur-Standards & DSGVO-Footer
- P1: Breakpoint-Testing (1920→360)
- P2: Outbound Lead Machine
- P2: server.py Refactoring (>3600 Zeilen)

## Testing Status
- Iteration 19: 100% Pass
- Iteration 20: 96% → 100% (Portal Token fix)
- Iteration 21: 100% (19/19) — Customer/Portal/mem0
- Iteration 22: 100% (23/23) — Full CRUD + Dynamic Floating
