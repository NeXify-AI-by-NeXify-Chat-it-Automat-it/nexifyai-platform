# ADR-004: Monorepo-Struktur und Package-Grenzen

**Status:** accepted
**Datum:** 2026-05-08
**Autor:** NeXifyAI (Lead Agent)
**Stakeholder:** Technical Lead, DevOps

## Kontext

DOS v1.1 definiert eine Monorepo-Struktur mit `/apps`, `/packages`, `/ops`, `/automations`. Das aktuelle Repository (`nexifyai-website-sicherheitskopie`) ist organisch gewachsen und folgt keiner klaren Package-Struktur. Frontend (CRA) und Backend (FastAPI) liegen im Root, es gibt keine geteilten Packages.

## Problem

Ohne definierte Package-Grenzen:
- Kein geteiltes Designsystem (Verstoß gegen "No One-Off UI")
- Events-Taxonomie nicht zentralisiert
- Keine klaren API-Verträge zwischen Frontend und Backend
- Config-Duplikation (.env, thresholds, feature-flags)
- CI kann Änderungen nicht nach Package scopen (immer Full-Build)

## Optionen

### Option A: Monorepo mit klaren Packages (GEWÄHLT)
- **Pro:** Geteilte Packages, klare Grenzen, versionierte Abhängigkeiten, CI-Optimierung
- **Contra:** Initialer Refactoring-Aufwand, Tooling (Turborepo/Nx) optional

### Option B: Polyrepo (separate Repos pro Service)
- **Pro:** Isolierte CI/CD, unabhängige Versionierung
- **Contra:** Kein geteiltes Designsystem, Config-Drift, komplexeres Setup

### Option C: Status Quo (flache Struktur)
- **Pro:** Kein Aufwand
- **Contra:** Verstößt gegen DOS v1.1 und v2.0, skaliert nicht

## Entscheidung

**Option A: Monorepo mit klaren Packages** nach DOS-Standard.

Struktur:
```
/apps/chat-it/        → Next.js Frontend (Ziel)
/packages/ui/         → Designsystem-Komponenten + Tokens
/packages/events/     → Event-Taxonomy + Zod-Validatoren  
/packages/config/     → Zentrale Konfiguration (KPI, Feature-Flags, API)
/packages/content/    → Copy-Blueprints, Glossar, Claims
/ops/ci/              → CI-Templates (GitHub Actions)
/ops/infra/           → Docker, Compose, Migrationen
/ops/policies/        → PR-Policy, Commit-Policy, Security
/automations/cron/    → Cron-Jobs (bereits live)
```

## Konsequenzen

- **Positiv:** DOS-konforme Struktur, geteiltes Designsystem, klare Ownership
- **Negativ:** Pfad-Änderungen in bestehenden Scripten; Übergangsphase mit Dual-Struktur
- **Neutral:** `frontend/` und `backend/` bleiben vorerst als Legacy-Roots erhalten

## Rollback-Plan

- Neue Packages sind additiv — bestehende `frontend/` und `backend/` werden nicht gelöscht
- Package-Imports sind optional; kein Breaking Change für bestehenden Code
- Migration erfolgt schrittweise (Package für Package)

## Verweise

- DOS v2.0 Kapitel 10: Tech-Stack (Monorepo-Struktur)
- DOS v2.0 Kapitel 9: Design-System
- DOS v2.0 Kapitel 11: Event-Taxonomy
- ADR-001: DOS v2.0 Einführung
