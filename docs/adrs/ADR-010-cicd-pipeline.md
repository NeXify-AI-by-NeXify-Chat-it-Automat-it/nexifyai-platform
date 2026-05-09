# ADR-010: CI/CD Pipeline Strategy

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), DevOps

## Kontext

NeXifyAI nutzt GitHub Actions fuer CI/CD mit Vercel-Deployment. Die Pipeline hat Quality Gates (Gitleaks, ESLint, Pytest, Jest). Mehrere Commits auf main hatten failing Gates.

## Problem

CI/CD muss: Secret-Scans, Linting, Tests, Build, Deploy zuverlaessig ausfueren. Failing Gates blocken Deployments. Verified Commits-Problem (Root-Commits werden von GitHub geblockt).

## Optionen

1. **Option A: Keine CI/CD** -- Manuelles Deployment
   - Pro: Kein Overhead
   - Contra: Fehleranfaellig, keine Qualitaetssicherung

2. **Option B: GitHub Actions + Vercel (GEWAEHLT)**
   - Pro: Automatisiert, Quality Gates, Preview-Deployments
   - Contra: GitHub-Token-Management, Verified-Commits-Problem

3. **Option C: Selbst-gehostetes CI (Jenkins, Drone)**
   - Pro: Volle Kontrolle
   - Contra: Wartungsaufwand, Single-Point-of-Failure

## Entscheidung

**Option B** -- GitHub Actions mit:
- Gitleaks fuer Secret-Scanning
- ESLint + Prettier fuer Frontend
- Pytest fuer Backend
- Jest fuer Frontend-Tests
- Vercel fuer Deployment (Preview + Production)
- Workaround fuer Verified Commits: Vercel Deploy Hook oder PAT-Token

## Konsequenzen

- **Positiv:** Automatisierte Qualitaetskontrolle, Preview-URLs, schnelle Deployments
- **Negativ:** GitHub-Token-Rotation noetig, CI-Kosten
- **Neutral:** main-Branch ist immer deployable (wenn Gates gruen)

## Rollback-Plan

Manuelles Vercel-Deployment via `vercel deploy` oder Vercel Dashboard.

## Verweise

- .github/workflows/ Verzeichnis
- ADR-001: DOS v2.0 Adoption
