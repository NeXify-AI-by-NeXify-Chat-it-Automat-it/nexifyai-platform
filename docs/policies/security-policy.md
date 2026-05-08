# Security Policy
# DOS v2.0 Chapter 14: Security & Compliance

## Basis-Sicherheitsstandard (alle Projekte)

- [x] HTTPS überall, HSTS gesetzt
- [ ] CSP (Content Security Policy) implementiert
- [x] RBAC (Role-Based Access Control)
- [x] 2FA/MFA für Admin-Zugänge
- [x] Secrets Management (nie in Git)
- [x] Dependency Scanning (automatisch in CI)
- [x] Secret Scanning (Gitleaks Pre-Commit Hook)

## Erhöhter Standard (B2B/Enterprise)

- [x] AVV vor Produktiv-Deployment
- [x] DSGVO-Dokumentation (VVT)
- [ ] DSFA bei risikoreichen Verarbeitungen
- [x] Incident Response Plan
- [x] Backup-Konzept (RPO/RTO definiert)
- [ ] Penetration-Test (Enterprise: jährlich)
- [ ] Zugriffsaudits (quartalsweise)

## Retrieval-First vor jeder Integration

1. CVE-Prüfung (National Vulnerability Database)
2. Lizenzprüfung (MIT, Apache 2.0, BSD, ISC — blockiert: GPL, AGPL, SSPL)
3. Wartungsstatus (aktiv maintained?)
4. Breaking Changes in letzten Releases
5. Security Advisories des Anbieters
6. CI-Fähigkeit (automatisierbar?)
7. Template-Verfügbarkeit (erprobte Integration?)

## Incident Response

Siehe `/docs/incidents/` — aktive Incidents und Postmortems.
