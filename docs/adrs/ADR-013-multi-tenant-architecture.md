# ADR-013: Multi-Tenant Architecture

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), Kunden-Projekte

## Kontext

NeXifyAI betreibt Kundenprojekte (KI-Fabrik, zukuenftige Kunden). Jeder Kunde braucht isolierte Infrastruktur: eigenes Repo, eigenes Deployment, eigene Datenbank.

## Problem

Kundendaten duerfen nicht vermischt werden. Jeder Kunde braucht: eigenes GitHub-Repo, eigenes Vercel-Projekt, eigenes Supabase-Schema, eigene Credentials.

## Optionen

1. **Option A: Shared Infrastructure**
   - Pro: Geringere Kosten
   - Contra: Datenschutz-Risiko, Komplexitaet bei Isolation

2. **Option B: Vollstaendige Tenant-Isolation (GEWAEHLT)**
   - Pro: Maximale Isolation, einfache Abrechnung, eigenes Lifecycle
   - Contra: Hoehere Infrastrukturkosten pro Kunde

3. **Option C: Schema-based Multi-Tenancy (Supabase Schemas)**
   - Pro: Geteilte Instanz, isolierte Schemas
   - Contra: Schema-Migration komplex, Shared-Ressourcen-Risiko

## Entscheidung

**Option B** -- Vollstaendige Tenant-Isolation:
- Eigener GitHub-Ordner: `/opt/data/customers/{kunde}/`
- Eigene Branch-Struktur: `customer/{kunde}/{feature}`
- Eigene Credentials in `10-CREDENTIALS/`
- Kein Cross-Kunden-Zugriff
- Brain pro Kunde indexiert

## Konsequenzen

- **Positiv:** Maximale Datenschutz-Compliance, einfache Kuendigung
- **Negativ:** Mehr Infrastruktur pro Kunde
- **Neutral:** Orchestrator verwaltet N isolierte Tenants

## Rollback-Plan

Migration zu Shared Infrastructure moeglich, aber Daten-Migration aufwendig.

## Verweise

- Skill: nexifyai-multi-tenant-architecture
- /opt/data/customers/ Verzeichnis
- DOS v2.0 Teil XX: Multi-Tenant
