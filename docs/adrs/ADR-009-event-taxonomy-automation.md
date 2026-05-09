# ADR-009: Event Taxonomy & Automation

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), DevOps

## Kontext

NeXifyAI hat multiple Event-Quellen: Cron-Jobs, Webhooks, User-Actions, System-Events. Ohne einheitliche Taxonomie sind Events nicht filterbar, nicht routbar, nicht auditierbar.

## Problem

Events muessen klassifiziert, geroutet und verarbeitet werden koennen. Ohne Taxonomie: Chaos bei Incident-Response, keine automatisierte Eskalation.

## Optionen

1. **Option A: Ad-hoc Event-Handling**
   - Pro: Kein Overhead
   - Contra: Nicht skalierbar, keine Automatisierung

2. **Option B: Einheitliche Event-Taxonomie (GEWAEHLT)**
   - Pro: Klassifizierung (system, business, security, compliance), Routing, Automatisierung
   - Contra: Initiale Definitionsaufwand

## Entscheidung

**Option B** -- Event-Taxonomie mit Kategorien: system, business, security, compliance, brain. Jedes Event hat: type, severity (P0-P3), source, timestamp. Routing ueber Cron-Scheduler und Notification-System.

## Konsequenzen

- **Positiv:** Automatisierte Eskalation, filterbare Logs, Incident-Response
- **Negativ:** Bestehende Events muessen migriert werden
- **Neutral:** Event-Store wird zu zentraler Datenquelle fuer Audits

## Rollback-Plan

Event-Taxonomie ist eine Konvention, kein technisches System. Zurueck zu Ad-hoc durch Ignorieren der Klassifizierung.

## Verweise

- DOS v2.0 Teil VIII: Event Taxonomy & Automation
- /automations/cron/ Verzeichnis
