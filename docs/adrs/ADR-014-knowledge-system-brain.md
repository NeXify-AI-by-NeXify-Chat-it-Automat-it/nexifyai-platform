# ADR-014: Knowledge System (Brain Architecture)

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), Alle Agenten

## Kontext

NeXifyAI braucht persistentes Gedaechtnis: Brain (SQLite + Qdrant Vektor-Store + Open Notebook). Agenten muessen Wissen konsistent speichern und abrufen koennen.

## Problem

KI-Agenten vergessen Kontext zwischen Sessions. Ohne Brain: keine Lernkurve, wiederholte Fehler, kein institutionelles Wissen.

## Optionen

1. **Option A: Kein persistentes Gedaechtnis**
   - Pro: Kein Overhead
   - Contra: Jede Session startet bei Null

2. **Option B: Multi-Tier Brain (GEWAEHLT)**
   - Pro: SQLite (struktiert), Qdrant (Vektor-Suche), Open Notebook (Quellen)
   - Contra: Sync-Komplexitaet, Embedding-Kosten

3. **Option C: Externe Memory-Plattform (Mem0, Zep)**
   - Pro: Managed Service
   - Contra: Vendor Lock-in, Kosten, Datenschutz

## Entscheidung

**Option B** -- Multi-Tier Brain:
- `brain.db` (SQLite): Memories, Tasks, Skills Cache, FTS5-Volltextsuche
- Qdrant: Vektor-Semantik-Suche (1482+ Points)
- Open Notebook: Quellen-Management (36+ Dokumente)
- BrainGovernor: Access Control (5 Write-Policies)
- prefill.md: Schnellreferenz fuer Agenten

## Konsequenzen

- **Positiv:** Institutionelles Wissen, semantische Suche, Lernkurve
- **Negativ:** Embedding-Kosten (OpenRouter qwen3-embedding-8b), Sync-Aufwand
- **Neutral:** Brain wird zu Single-Source-of-Truth

## Rollback-Plan

Brain.db kann neu erstellt werden. Qdrant-Collections koennen geloescht und neu indexiert werden. Open Notebook bleibt als unabhaengige Quellen-Sammlung bestehen.

## Verweise

- /opt/data/brain/brain.db
- Qdrant Port 6333
- Open Notebook Port 32770
- Skill: honcho-brain-integration
- DOS v2.0 Teil XXI: Knowledge System
