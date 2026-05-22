# ADR-018: Secret-Management-Strategie

**Status:** accepted
**Datum:** 2026-05-21
**Autor:** Security-Agent
**Stakeholder:** Alle Entwickler, DevOps, CTO, Security-Team
**Superseded by:** ADR-024 (pgcrypto Vault)

## Kontext

Die NeXifyAI-Plattform betreibt eine Multi-Service-Architektur mit zahlreichen externen API-Integrationen. Secrets waren verstreut über `.env`-Dateien, Docker-Configs und Code.

## Problem

Wie können alle Service-Credentials zentral, sicher und auditierbar verwaltet werden, ohne Klartext-Secrets in Repos, Datenbanken oder Backups?

## Entscheidung

**Hybride Strategie:**
1. **Host-Ebene:** `/root/.secrets/credentials.env` (chmod 600) für Betriebs-Secrets
2. **Supabase-Ebene:** pgcrypto-basiertes Vault (siehe ADR-024)
3. **CI/CD-Ebene:** GitHub Secrets für Pipeline-Credentials
4. **Keine Secrets im Code:** `.env`-Dateien sind gitignored

## Konsequenzen

### Positiv
- Keine hartcodierten Secrets mehr
- Audit-Trail für Secret-Änderungen
- ISO 27001-konform

### Negativ
- Manuelle Key-Setzung bei Deployment
- Key-Verlust = Datenverlust
