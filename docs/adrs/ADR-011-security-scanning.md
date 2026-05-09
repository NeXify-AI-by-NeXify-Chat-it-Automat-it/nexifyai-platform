# ADR-011: Security Scanning Pipeline

**Status:** accepted
**Datum:** 2026-05-09
**Autor:** NeXifyAI (Orchestrator)
**Stakeholder:** Pascal Courbois (CEO), Security

## Kontext

NeXifyAI verarbeitet Kundendaten und API-Keys. Security-Scanning muss automatisiert erfolgen: Secret-Leak-Detection, CVE-Scanning, Dependency-Auditing.

## Problem

Ohne automatisierte Security-Scans: Leaked Secrets in Git, verwundbare Dependencies, Compliance-Luecken.

## Optionen

1. **Option A: Manuelle Security-Reviews**
   - Pro: Kein Tooling
   - Contra: Nicht skalierbar, menschliche Fehler

2. **Option B: Multi-Layer Security Pipeline (GEWAEHLT)**
   - Pro: Gitleaks (Secrets), npm audit + safety (CVEs), Trivy (Container)
   - Contra: False Positives, Wartungsaufwand

## Entscheidung

**Option B** -- 3 Security-Workflows:
1. `security-secrets.yml` -- Gitleaks Secret-Scan bei jedem Push
2. `security-dependencies.yml` -- npm audit + pip safety fuer CVEs
3. `security-container.yml` -- Trivy Container-Scan

Alle 3 muessen gruen sein fuer Security-Score 100%. `.gitleaks.toml` fuer erlaubte False Positives.

## Konsequenzen

- **Positiv:** Automatisierte Secret-Detection, CVE-Tracking, Compliance
- **Negativ:** Gitleaks-Tuning noetig (False Positives bei Test-Files)
- **Neutral:** Security-Score wird zu KPI im Health-Check

## Rollback-Plan

Security-Workflows koennen deaktiviert werden. `.gitleaks.toml` kann alle Regeln ignorieren.

## Verweise

- .github/workflows/security-*.yml
- .gitleaks.toml
- Skill: gitleaks-ci-fix-allowlist
