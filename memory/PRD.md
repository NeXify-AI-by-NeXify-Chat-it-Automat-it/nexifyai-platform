# NeXifyAI — Product Requirements Document

## Problem Statement
B2B-Plattform "Starter/Growth AI Agenten AG" mit API-First Architektur. Unified Communication Layer (Chat, Mail, WhatsApp, Portal), Deep Customer Memory (mem0), KI-Orchestrator mit 9 Sub-Agents, Automated B2B Outbound Lead Machine, Live Admin CRM mit Audit-System.

## Source of Truth — Gesamtkonzept
Drei Referenzdokumente definieren die Gesamtanforderung:
1. `NeXifyAI_Emergent_Auftrag_Premium_FineTuned_20260403.txt` — Auftragsspezifikation
2. `NeXifyAI_Gesamtkonzept_Premium_FineTuned_20260403 (1).md` — Architektur & Features
3. `NeXifyAI_Gesamtkonzept_Premium_FineTuned_20260403 (2).md` — Design System, Format, QA

## Architecture
- **API-First**: Domain Layer, Channel Layer, Connector Layer, Agent Layer, Event/Audit Layer
- **WhatsApp Bridge**: QR-Pairing als isolierter Connector, austauschbar gegen offizielle API
- **Unified Communications**: AI-Chat, Email, WhatsApp, Portal in einer Timeline/Identity
- **KI-Orchestrator**: GPT-5.2 via Emergent LLM Key mit 9 Sub-Agents
- **Audit System**: Health-Checks, Timeline, Self-Healing

## Tech Stack
- Frontend: React 18 SPA
- Backend: FastAPI + Motor (MongoDB async)
- Database: MongoDB
- LLM: Emergent LLM Key (OpenAI GPT-5.2)
- Email: Resend API (nexifyai@nexifyai.de)

## Agent Layer (9 Agenten)
1. Intake — Leadaufnahme, Discovery, Klassifikation
2. Research — Firmenanalyse, Lead-Enrichment
3. Outreach — Personalisierte Erstansprache, Follow-ups
4. Offer — Angebotserstellung, Tarifberatung
5. Planning — Projektplanung, Architektur, Build-Handover
6. Finance — Rechnungsstellung, Zahlungen, Mahnwesen
7. Support — Kundenbetreuung, Problemlösung
8. Design — Design-Konzeption, Content-Strategie, SEO
9. QA — Qualitätssicherung, Audit, Selbstheilung

## Tariffs (Source of Truth)
- Starter AI Agenten AG: 499 EUR/Monat, 24 Mo, 30% Anzahlung (3.592,80 EUR)
- Growth AI Agenten AG: 1.299 EUR/Monat, 24 Mo, 30% Anzahlung (9.352,80 EUR)
- Websites: Starter 2.990, Professional 7.490, Enterprise 14.900
- Apps: MVP 9.900, Professional 24.900
- SEO: Starter 799/Mo (6 Mo), Growth 1.499/Mo (6 Mo)
- Bundles: Digital Starter 3.990, Growth Digital 17.490, Enterprise Digital ab 39.900

## What's Implemented

### WhatsApp Button (DONE)
- Desktop: Vertikal, flush links, Abrundung rechts, Rotation-kompensiert
- Tablet: Angepasste Größe, Content Safe Area
- Mobile: Horizontaler Pill-Button, bottom:140px
- Admin/Portal: Versteckt via body.hide-wa

### Admin CRM (DONE)
- 11 Sidebar-Tabs: Dashboard, Commercial, Leads, Kommunikation, AI-Chats, WhatsApp, Timeline, Kalender, Kunden, KI-Agenten, Audit
- WhatsApp Connect mit QR-Pairing, Messaging, Session-Management
- Conversations View mit Inline-Reply
- KI-Agenten View mit Task-Execution, Memory-Injection
- Audit View mit Health-Checks, Timeline, Collection-Stats

### WhatsApp QR-Connector (DONE)
- 8 Endpoints (pair/status/reconnect/simulate-connect/send/disconnect/reset/messages)
- Isolierte Bridge-Architektur

### KI-Orchestrator + 9 Sub-Agents (DONE)
- Orchestrator mit GPT-5.2 Routing
- 9 spezialisierte Agenten mit eigenem System-Prompt
- Audit Trail in Timeline Events
- Customer Memory Injection

### Customer Memory / mem0 (DONE)
- Kanalübergreifend: WhatsApp, Email, Chat, Portal
- Memory Facts API

### Customer Portal (DONE)
- 6 Tabs: Übersicht, Angebote, Rechnungen, Termine, Kommunikation, Aktivität
- Quote Accept/Decline/Revision via Magic Link
- Communication Tab (Chat + Unified Conversations)
- Timeline/Activity Tab
- PDF-Downloads

### Audit System (DONE)
- Health-Check: Database, Collections, Agents, WhatsApp, LLM, Errors, Pricing
- Timeline: Letzte 48h Ereignisse
- Admin UI mit Audit-View

### Mobile Chat Premium (DONE)
- Mobile-optimierte Bubble-Abstände, Padding, Zeilenhöhe
- Markdown-Formatierung (Tables, Code, Blockquotes, Lists)
- Safe-Area für iOS

## Pending / Upcoming Tasks
- P1: Outbound Lead Machine (Automatisiertes Lead-Enrichment, Scoring, Email-Outreach)
- P1: Email-Professionalisierung (Zentrale KI-Orchestrierung aller Emails)
- P1: Kanalübergreifender Kommunikationskern vollenden
- P1: Revolut/Billing/Status-Sync (Quote → Invoice → Payment → App-Status)
- P2: Responsive Fine-Tuning über alle Breakpoints (1920→360)
- P2: Autonome Dokumentation & QA Agent-Automatisierung
- P2: server.py Refactoring → modulare Struktur (/routes, /agents, /services)
