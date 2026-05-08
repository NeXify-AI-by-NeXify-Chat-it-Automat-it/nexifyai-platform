# ADR-002: Supabase als Primary Database (Ablösung MongoDB)

**Status:** accepted
**Datum:** 2026-05-08
**Autor:** NeXifyAI (Lead Agent)
**Stakeholder:** Pascal Courbois (CEO), DevOps

## Kontext

NeXifyAI betrieb seine Datenhaltung ursprünglich auf MongoDB (self-hosted, Docker). Mit der Einführung von Supabase (self-hosted, PostgreSQL) ergab sich die Möglichkeit, auf eine SQL-basierte, schema-strikte Datenbank mit integriertem Auth, Storage und Realtime zu migrieren. Die Entscheidung betrifft die gesamte Datenarchitektur und alle darauf aufbauenden Services.

## Problem

MongoDB und Supabase parallel zu betreiben verursacht:
- Dual-Write-Logik mit Inkonsistenz-Risiko
- Höhere Wartungskosten (zwei DB-Systeme)
- Keine referenzielle Integrität auf MongoDB-Seite
- Auth-Fragmentierung (MongoDB JWT + GoTrue JWT)
- Erschwerte Datenanalyse (NoSQL vs SQL)

## Optionen

### Option A: MongoDB bleibt Primary, Supabase nur Auth
- **Pro:** Keine Migration nötig
- **Contra:** Verpasst Schema-Governance, SQL-Analytics, RLS; MongoDB veraltet

### Option B: Supabase als alleinige Primary Database (GEWÄHLT)
- **Pro:** Einheitliche Datenhaltung, RLS, SQL-Analytics, Supabase-Ökosystem (Auth/Storage/Realtime), referenzielle Integrität
- **Contra:** Migrationsaufwand (2.481 Dokumente, 30 Collections)

### Option C: PostgreSQL direkt (ohne Supabase)
- **Pro:** Volle Kontrolle
- **Contra:** Verzicht auf Supabase-Ökosystem (Auth, Storage, Realtime, Studio)

## Entscheidung

**Option B: Supabase als alleinige Primary Database.** MongoDB wird nach vollständiger Migration stillgelegt.

Begründung:
1. Supabase PostgreSQL bietet Schema-Governance, die DOS fordert
2. Row-Level-Security (RLS) ermöglicht Multi-Tenant-Isolation auf DB-Ebene
3. GoTrue-Auth ist bereits live und akzeptiert
4. Supabase Storage ersetzt MongoDB GridFS
5. Migrationspfad ist erprobt (30 von 31 Collections migriert)

## Konsequenzen

- **Positiv:** Schema-strikte Datenhaltung, referenzielle Integrität, RLS, einheitliches Auth
- **Negativ:** MongoDB-Wissen obsolet; DualDbProxy-Wartung bis Migration komplett
- **Neutral:** SQL- statt NoSQL-Denken im Team; Migration von `col()`-Aufrufen

## Rollback-Plan

- MongoDB-Container bleibt bis 31.07.2026 als Read-Only-Fallback erhalten
- DualDbProxy kann im Notfall MongoDB priorisieren
- Vollständiger Rollback unwahrscheinlich, da Supabase bereits Produktionsdaten führt

## Verweise

- Supabase Phase A-D Dokumentation: `/docs/supabase/`
- Migrationen: `/ops/infra/migrations/`
- DOS v2.0 Kapitel 22: Datenarchitektur
- ADR-001: DOS v2.0 Einführung
