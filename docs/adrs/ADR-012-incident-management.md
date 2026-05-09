# ADR-012: Incident Management Process

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), DevOps, Support

## Kontext

NeXifyAI hatte mehrere SEV1-Incidents (DNS-Fail, SSH-Defekt, Backend-Down). Ohne strukturiertes Incident-Management: keine systematische Nachbereitung, wiederholte Fehler.

## Problem

Incidents muessen: klassifiziert (SEV1-3), dokumentiert, nachbereitet (Postmortem) werden. Root-Cause-Analyse verhindert Wiederholungen.

## Optionen

1. **Option A: Ad-hoc Incident-Handling**
   - Pro: Kein Prozess
   - Contra: Wiederholte Fehler, keine Lernkurve

2. **Option B: Strukturiertes Incident-Management (GEWAEHLT)**
   - Pro: SEV-Klassifikation, Postmortem-Template, Brain-Dokumentation
   - Contra: Prozess-Overhead

## Entscheidung

**Option B** -- Incident-Management mit:
- SEV1: System down, Datenverlust -> Sofortige Eskalation an Pascal
- SEV2: Degraded Service -> Autonome Behebung, Brain-Dokumentation
- SEV3: Minor Issue -> Ticket-Erstellung, naechster Cycle
- Postmortem-Template fuer alle SEV1/SEV2
- Brain-Eintrag fuer jede Root-Cause

## Konsequenzen

- **Positiv:** Systematische Fehlervermeidung, Wissensaufbau im Brain
- **Negativ:** Postmortem-Schreibaufwand bei jedem SEV2
- **Neutral:** Incident-Historie wird zu Trainingsdaten fuer Agenten

## Rollback-Plan

Incident-Management ist ein Prozess, kein System. Vereinfachung durch Weglassen von Postmortems moeglich.

## Verweise

- DOS v2.0 Teil XVII: Incident Management
- Brain: memories mit category='sev1', 'sev2'
