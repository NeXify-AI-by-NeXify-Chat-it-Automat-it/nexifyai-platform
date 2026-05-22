# ADR-022: Docker-Hardening-Standard — Multi-Stage, Non-Root, Security

**Status:** accepted
**Datum:** 2026-05-21
**Autor:** DevOps-Agent / AI-CEO (AIC-64)
**Stakeholder:** DevOps, Security, Frontend, Backend

## Kontext
Die DevOps-Analyse (Iteration 3) hat identifiziert, dass **keines der 4 Dockerfiles** im System Enterprise-Security-Standards erfüllt:
- ❌ Kein Multi-Stage-Build → unnötig große Images (500MB+ statt ~100MB)
- ❌ Kein Non-Root-User → Security-Breach bei Container-Escape
- ❌ Teilweise kein HEALTHCHECK → kein automatisches Restart
- ❌ Kein .dockerignore → Build-Kontext enthält node_modules/ und .git/

ISO 27001 A.8.2 (Informationssicherheit) und OWASP Docker Top 10 fordern diese Standards.

## Problem
Große Images mit Root-Usern erhöhen die Angriffsfläche. Ohne Multi-Stage-Build sind Images unnötig groß (längere Deployments, mehr Speicher).

## Optionen
1. **Option A: Multi-Stage + Non-Root + HEALTHCHECK** (Gewählt)
   - Pro: Vollständige Security, minimale Images, ISO-konform
   - Contra: Initialer Refactoring-Aufwand für alle Dockerfiles

2. **Option B: Nur Non-Root-User**
   - Pro: Einfach
   - Contra: Images bleiben groß

## Entscheidung
Option A wird verbindlicher Standard für ALLE Dockerfiles:
1. `FROM ... AS builder` + `FROM ... AS runtime` — Trennung von Build & Runtime
2. `adduser --system --uid 1001 appuser` + `USER appuser` — Non-Root
3. `HEALTHCHECK --interval=30s ... CMD curl -f http://localhost:8000/health` — Selbstheilung
4. `.dockerignore` mit node_modules, .git, __pycache__ — minimale Builds
5. `COPY --from=builder` — nur binäre Artefakte übernehmen

## Konsequenzen
### Positiv
- 🔒 Reduzierte Angriffsfläche (Non-Root)
- 📦 Kleinere Images (50-80% Reduktion)
- 🩺 Automatische Container-Heilung (HEALTHCHECK)
- ✅ ISO 27001, OWASP-konform

### Negativ
- ⏱️ Dockerfiles müssen aktualisiert werden
- ⚠️ COPY --chown kann Permission-Probleme verursachen

## Rollback-Plan
1. Alte Dockerfiles als `.bak` sichern
2. Staging-Test vor Production-Deployment

## Verweise
- [Docker Hardening Template](docs/operations/docker-hardening-template.md)
- [Docker Hardening Tasks](docs/tasks/docker-hardening-tasks.md)
- ADR-004: Monorepo Package Structure
- OWASP Docker Top 10
- ISO 27001:2022 A.8.2
