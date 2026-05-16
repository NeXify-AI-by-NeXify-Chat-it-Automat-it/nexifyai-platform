# ADR-015: Health Monitoring Strategy

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), DevOps

## Kontext

NeXifyAI hat multiple Services (Backend, Frontend, Qdrant, Open Notebook, Supabase, Traefik). Ohne Monitoring: Ausfaelle werden erst durch Kundenbeschwerden bemerkt.

## Problem

System-Health muss kontinuierlich gemessen werden: Service-Erreichbarkeit, Response-Zeiten, Fehlerquoten, Resource-Auslastung.

## Optionen

1. **Option A: Manuelles Monitoring**
   - Pro: Kein Tooling
   - Contra: Reaktiv, nicht skalierbar

2. **Option B: Automatisiertes Health-Score-System (GEWAEHLT)**
   - Pro: health-score.py berechnet Gesamtscore, Cron-basiert, Brain-Dokumentation
   - Contra: Score-Berechner kann Bugs haben (siehe T11, T2)

3. **Option C: Externes Monitoring (Uptime Robot, Datadog)**
   - Pro: Professionelles Dashboard
   - Contra: Kosten, Vendor Lock-in

## Entscheidung

**Option B** -- Automatisiertes Health-Score-System:
- `health-score.py` prueft: Backend, Frontend, Cron, Docker, Disk, Security
- Topology-aware: Services haben Dependencies (Backend -> Supabase)
- Score > 80% = gesund, < 60% = SEV1-Eskalation
- Taeglicher System-Check via Cron
- Connection-Health-Inventory als woechentlicher Tiefenscan

## Konsequenzen

- **Positiv:** Frueherkennung von Problemen, messbare Qualitaet
- **Negativ:** health-score.py Bugs koennen False Positives produzieren (T11)
- **Neutral:** Health-Score wird zu KPI im Dashboard

## Rollback-Plan

health-score.py kann deaktiviert werden. Manuelles Monitoring via `curl` und `docker ps`.

## Verweise

- /opt/nexifyai-platform/automations/cron/health-score.py
- Skill: health-score-real-metrics
- DOS v2.0 Teil XXIV: System Health
