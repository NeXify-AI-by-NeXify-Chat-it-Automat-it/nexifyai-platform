# NeXifyAI — Product Requirements Document

## Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" mit API-First Architektur. Unified Communication Layer (Chat, Mail, WhatsApp, Portal), Deep Customer Memory (mem0), KI-Orchestrator mit Sub-Agents, Automated B2B Outbound Lead Machine, Live Admin CRM.

## Architecture
- **API-First**: Domain Layer, Channel Layer, Connector Layer, Agent Layer, Event/Audit Layer
- **WhatsApp Bridge**: QR-Pairing als isolierter Connector, austauschbar gegen offizielle API
- **Unified Communications**: AI-Chat, Email, WhatsApp, Portal in einer Timeline/Identity
- **KI-Orchestrator**: GPT-5.2 via Emergent LLM Key mit Sub-Agents
- **Outbound Machine**: Lead-Enrichment, Scoring, personalisierte Outreach

## Tech Stack
- Frontend: React 18 SPA
- Backend: FastAPI + Motor (MongoDB async)
- Database: MongoDB
- LLM: Emergent LLM Key (OpenAI GPT-5.2)
- Email: Resend API (nexifyai@nexifyai.de)

## Core Data Models (domain.py)
- Customer/Contact (unified across channels)
- Conversation (multi-channel, timestamped)
- Message (with direction, channel, AI flag)
- Timeline Event (audit trail)
- WhatsApp Session (bridge connector state)
- Customer Memory (mem0-style facts)

## Tariffs (Source of Truth)
- Starter AI Agenten AG: 499 EUR/Monat, 24 Mo, 30% Anzahlung (3.592,80 EUR)
- Growth AI Agenten AG: 1.299 EUR/Monat, 24 Mo, 30% Anzahlung (9.352,80 EUR)

## What's Implemented

### Block 1-2: WhatsApp Button (DONE)
- Desktop: Vertikal, flush links, Abrundung nur rechts, Rotation-kompensiert
- Tablet: Angepasste Größe, Content Safe Area
- Mobile: Horizontaler Pill-Button, bottom:140px
- Admin/Portal: Versteckt via body.hide-wa

### Block 3: Admin UI (DONE)
- 10 Sidebar-Navigationspunkte
- Dashboard, Commercial, Leads, Kommunikation, AI-Chats, WhatsApp, Timeline, Kalender, Kunden, KI-Agenten
- Responsive Tabellen, saubere Action-Bars

### Block 4: WhatsApp QR-Connector (DONE)
- Session-Status: unpaired/pairing/connected/reconnecting/disconnected/failed
- QR-Code generieren, Session zurücksetzen, Trennen, Reconnect
- Simulate-Connect (Dev/Test)
- Nachrichten senden/empfangen
- Message History in Admin-Tabelle
- Nachrichten in Unified Timeline
- Bridge-Architektur: Isolierter Adapter, austauschbar

### Block 5: Customer Memory / mem0 (DONE)
- Kanalübergreifend: WhatsApp, Email, Chat, Portal
- Sources: Lead, Quotes, Invoices, Bookings, Chat Sessions, Contact Forms, Unified Conversations, Memory Facts
- Memory Facts API: Manuell hinzufügen via Admin
- Automatische Injektion in KI-Agent-Kontexte

### Block 6: KI-Orchestrator + Sub-Agents (DONE)
- Orchestrator: Zentrale Routing-Instanz (GPT-5.2)
- Research Agent: Lead-Recherche, Firmenanalyse
- Outreach Agent: Personalisierte Erstansprache, Follow-ups
- Offer Agent: Angebotserstellung, Tarifberatung
- Support Agent: Kundenbetreuung, Problemlösung
- Admin UI: KI-Agenten-View mit Task-Input + Customer Memory Injection
- Audit Trail: Alle Agent-Aktionen in Timeline Events

## Pending / Upcoming Tasks
- P1: Outbound Lead Machine (Automatisiertes Lead-Enrichment, Scoring, Email-Outreach)
- P1: Email-Professionalisierung (Zentrale KI-Orchestrierung, CI-Signatur)
- P1: Customer Portal Vollausbau (Angebote, Rechnungen, PDF-Downloads)
- P1: Revolut/Billing/Status-Sync (Quote → Invoice → Payment → App-Status)
- P1: Kanalübergreifender Kommunikationskern vollenden
- P2: Autonome Dokumentation & QA
- P2: Refactoring server.py → modulare Struktur
