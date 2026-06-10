# Master-Projektplan NeXify AI Gesamtbetrieb V1

**Status:** V1 — 2026-06-10
**Owner:** Pascal Courbois / NeXify AI CEO
**Repo:** https://github.com/NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform.git

## Ziel

NeXify AI wird in kurzer Zeit in einen steuerbaren, beweisgeführten, autonomen Agentur-Betrieb überführt.

## Ausgangslage

Das Repo `nexifyai-platform` enthält Web-/Admin-/API-Strukturen, Node-Workspaces und Python-Backend-Abhängigkeiten für FastAPI, LangChain/LangGraph, Qdrant, Crawl4AI und Resend. Die Plattform ist bereits breit genug für Workstation, API, Brain, Agenten, Routing, Crawling und Kommunikation.

## Kernproblem

Widersprüchliche Governance-Annahmen: Ältere Dateien stellen Hermes/Oracle/Autopilot als Legacy dar, während die aktuelle NeXify-Strategie Hermes/Workstation, User-Chat-Driver, Automatik und Agentursteuerung als aktive P0-Grundlage nutzt.

## Zielbild

| Komponente | Rolle |
|------------|-------|
| Workstation | Zentrale Oberfläche |
| 12 Teams | Verantwortungseinheiten |
| User-Chat-Driver | Interne Fortsetzungslogik |
| Automation Controller | Steuerung der Automatik |
| Dispatcher | Aufgabenverteilung |
| Kanban | Operative Wahrheit |
| Brain | Langzeitwissen |
| agentmemory | Arbeitszustand |
| Skills/MCPs/Tools | Fähigkeitsschicht |
| 9Router | Modell-/Provider-/Kosten-/Fallback-Schicht |
| GitHub/Vercel/Cloudflare/Supabase | Betriebs- und Deployment-Schicht |
| Evidence/QR | Abschluss- und Vertrauenssystem |

## Phasen

1. **Konfliktbereinigung und Führungsgrundlage** — ADR, Legacy-Übersteuerung, Governance-Konsolidierung
2. **Betriebssystem V1** — 12 Teams, Automation Controller, Dispatcher, Queues, Schalter
3. **Technischer Anschluss** — User-Chat-Driver, Hermes-Hook, 9Router, Brain-Sync
4. **Live-/Repo-Betrieb** — GitHub, Vercel, Cloudflare, SSL, Rollback, DNS
5. **Workstation-Qualität** — Graphite-CI, Deutsch, Performance, Branding, UX
6. **Agenturwirtschaft** — Produkte, Zielgruppen, Angebote, Support, Retention

## Heute P0

User-Chat-Driver + Automatik + Team-System + Dispatcher + Kanban + Evidence.

## Policy Gates

| Aktion | Gate |
|--------|------|
| Git Push/Merge/Deployment | Pascal-Freigabe erforderlich |
| DNS/Cloudflare/Vercel Änderungen | Pascal-Freigabe erforderlich |
| Secrets/Provider Keys | Pascal-Freigabe erforderlich |
| Kundennachrichten/E-Mail/SimpleX-Outbound | Pascal-Freigabe erforderlich |
| Interne Governance-Dokumente | WRITE_INTERNAL — erlaubt |
| Strukturdateien anlegen | WRITE_INTERNAL — erlaubt |
