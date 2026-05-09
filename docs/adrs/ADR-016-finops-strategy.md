# ADR-016: FinOps Strategy

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), Buchhaltung

## Kontext

NeXifyAI hat multiple Kostenquellen: OpenRouter (LLM), Vercel (Hosting), Supabase (Datenbank), Hostinger (VPS), Domains. Ohne FinOps-Tracking: Kostenexpllosion unbemerkt.

## Problem

LLM-Kosten (OpenRouter) sind variabel und skalieren mit Nutzung. Hosting-Kosten sind fix. Profitabilitaet pro Kunde muss gemessen werden.

## Optionen

1. **Option A: Kein Kosten-Tracking**
   - Pro: Kein Overhead
   - Contra: Kostenexpllosion, keine Profitabilitaetsanalyse

2. **Option B: Integriertes FinOps (GEWAEHLT)**
   - Pro: Kosten pro Kunde, Profit-Tracking, Budget-Alerts
   - Contra: Tracking-Overhead

## Entscheidung

**Option B** -- FinOps mit:
- Kosten-Tracking pro Kunde in `25-COSTS/`
- OpenRouter-Kosten via API-Monitoring
- Vercel-Kosten via Dashboard
- Profit-Marge pro Kunde berechnen
- Monatlicher FinOps-Report

## Konsequenzen

- **Positiv:** Kostentransparenz, profitable Kundenidentifikation
- **Negativ:** Tracking-Aufwand pro Kunde
- **Neutral:** FinOps-Daten werden fuer Pricing-Entscheidungen genutzt

## Rollback-Plan

FinOps-Tracking kann auf manuelle Monatsberichte reduziert werden.

## Verweise

- DOS v2.0 Teil XVIII: FinOps
- /opt/data/customers/{kunde}/25-COSTS/
