# ADR-023: CI/CD-Shared-Workflows — Composite Actions für Enterprise CI

**Status:** proposed
**Datum:** 2026-05-21
**Autor:** DevOps-Agent / AI-CEO (AIC-64)
**Stakeholder:** DevOps, alle Entwickler

## Kontext
Die DevOps-Analyse hat gezeigt: **agentur-repo und sicher-repo haben 11+ Workflows, die fast identisch sind.** 
- Gitleaks, CodeQL, Trivy, SBOM, Test, Deploy — jeder Workflow existiert 2x
- Änderungen müssen in beiden Repos manuell synchronisiert werden
- Inkonstistente Konfiguration führt zu unterschiedlichen Sicherheits-Levels

## Problem
Duplizierte CI/CD-Workflows verursachen doppelten Wartungsaufwand und führen zu Drift zwischen Repos.

## Optionen
1. **Option A: GitHub Composite Actions** (Gewählt)
   - Pro: Einmal definieren, überall nutzen, versionsverwaltet
   - Contra: GitHub-native, nur innerhalb GitHub

2. **Option B: Reusable Workflows** (GitHub)
   - Pro: Job-Level-Wiederverwendung
   - Contra: Komplexer als Composite Actions

3. **Option C: Akzeptieren + manuelle Sync**
   - Pro: Kein Aufwand
   - Contra: Drift wird schlimmer

## Entscheidung
Option A: **GitHub Composite Actions in `agentur-repo/.github/actions/`**
- `security-scan/` → Gitleaks + Trivy + CodeQL in einer Action
- `deploy/` → Deployment mit Rollback-Vorbereitung
- `test/` → Python-Tests + Coverage
- Jede Action hat Version-Tag (v1, v2) für stabile Referenzen

## Konsequenzen
### Positiv
- ✅ Single Source of Truth für CI/CD
- ✅ Versionierte Actions mit Breaking-Change-Management
- ✅ Konsistente Security-Standards
- ✅ Einfacheres Onboarding neuer Repos

### Negativ
- ⏱️ Initialer Migrationsaufwand
- 📚 Team muss Composite Actions verstehen

## Rollback-Plan
1. Alte Workflows als Backup behalten bis alle Repos migriert sind
2. Feature-Branch für Migration → Review durch DevOps-Team

## Verweise
- [DevOps Audit](docs/tasks/devops-infrastructure-audit.md)
- GitHub Docs: Composite Actions
- ADR-010: CI/CD Pipeline
