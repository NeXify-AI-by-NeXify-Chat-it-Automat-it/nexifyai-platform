# Release Policy
# DOS v2.0 Chapter 15: Release-Management

## SemVer (Pflicht)

| Level | Verwendung |
|---|---|
| MAJOR (X.0.0) | Breaking Changes (API, Designsystem) |
| MINOR (0.X.0) | Neue Features (rückwärts-kompatibel) |
| PATCH (0.0.X) | Bugfixes, Security, Performance |

## Release-Prozess

1. PR gemerged (alle Quality Gates grün)
2. Release Tag erstellen (vX.Y.Z)
3. Container Image bauen (multi-stage)
4. SBOM generieren (CycloneDX/Syft)
5. Security Scan (Trivy/Grype) — CRITICAL/HIGH = Block
6. Image signieren (cosign)
7. Changelog automatisch generieren
8. Deploy zu Staging (automatisch)
9. Smoke Test auf Staging
10. Deploy zu Production (Approval)

## Environment-Strategie

| Environment | Beschreibung |
|---|---|
| Preview (per PR) | Ephemere Preview-URL, für QA |
| Staging | Automatisch nach Merge zu main |
| Production | Nur via Release-Tag, manuelles Approval |

## Rollback

Jeder Release muss eine dokumentierte Rollback-Möglichkeit haben.
Bei SEV0/SEV1: automatischer Rollback auf letzten grünen Stand.
