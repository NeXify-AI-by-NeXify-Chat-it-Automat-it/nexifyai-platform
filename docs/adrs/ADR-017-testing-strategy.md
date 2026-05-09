# ADR-017: Testing Strategy

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), DevOps

## Kontext

NeXifyAI hat Backend (Python/FastAPI) und Frontend (React). Tests muessen automatisiert laufen: Unit, Integration, E2E. CI-Gates erfordern gruene Tests.

## Problem

Ohne Testing-Strategie: Regressions erst in Production entdeckt, CI-Gates blockiert, Kunden betroffen.

## Optionen

1. **Option A: Keine Tests**
   - Pro: Kein Overhead
   - Contra: Regressions, instabile Deployments

2. **Option B: Multi-Layer Testing (GEWAEHLT)**
   - Pro: Pytest (Backend), Jest (Frontend), CI-Integration
   - Contra: Test-Wartungsaufwand

3. **Option C: E2E-first (Playwright, Cypress)**
   - Pro: Realistische Tests
   - Contra: Langsam, flaky, hoher Wartungsaufwand

## Entscheidung

**Option B** -- Multi-Layer Testing:
- Backend: Pytest mit Fixtures, Mock-frei wo moeglich
- Frontend: Jest + React Testing Library
- CI: Beide muessen gruen sein fuer Merge
- E2E: Playwright fuer kritische Pfade (optional)
- Test-Files in `backend/tests/` und `frontend/src/**/*.test.*`

## Konsequenzen

- **Positiv:** Fruehe Fehlererkennung, sichere Deployments
- **Negativ:** Test-Wartung, langsamer CI bei vielen Tests
- **Neutral:** Test-Coverage wird zu KPI

## Rollback-Plan

Tests koennen aus CI-Gates entfernt werden (continue-on-error). Nicht empfohlen.

## Verweise

- .github/workflows/ci.yml
- backend/tests/
- frontend/src/**/*.test.*
- DOS v2.0 Teil XIX: Testing
