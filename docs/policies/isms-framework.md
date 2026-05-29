# ISMS-Rahmendokument (ISO 27001)

**Stand:** 2026-05-30
**Verantwortlich:** NeXifyAI Security Officer / Pascal Courbois
**Norm:** ISO/IEC 27001:2022 — Informationssicherheits-Managementsystem

---

## 1. Geltungsbereich

Das ISMS gilt für die NeXifyAI-Plattform (nachfolgend "die Plattform"):
- FastAPI Backend (services/api/)
- React Frontend (apps/web/)
- Qdrant Vector Database
- Supabase (Auth, DB, Storage)
- Kong API Gateway
- MongoDB (Business-Daten)
- Redis Cache
- Monitoring (Prometheus, Grafana, Loki)

## 2. Sicherheitsziele (CIA)

| Ziel | Beschreibung | Metrik |
|------|-------------|--------|
| **Vertraulichkeit** | Kein unbefugter Zugriff auf Kundendaten | RLS auf allen Tabellen, RBAC |
| **Integrität** | Keine unbefugte Änderung von Daten | Audit-Log, Gitleaks, CI/CD |
| **Verfügbarkeit** | System läuft zuverlässig | Health-Score > 90%, Uptime 99.9% |

## 3. Risikomanagement

### 3.1 Risiko-Bewertungsprozess
1. **Identifikation** — Automatisierte Scans (Gitleaks, Dependabot, Trivy)
2. **Bewertung** — Severity-Klassifikation (SEV1-SEV4)
3. **Behandlung** — Fix/Workaround/Akzeptanz
4. **Überwachung** — Health-Score, Prometheus, Grafana
5. **Review** — Wöchentliche Sicherheits-Reviews

### 3.2 Akzeptierte Restrisiken
| Risiko | Begründung |
|--------|------------|
| LLM-Provider (OpenRouter) | DPA vorhanden, keine Rohdaten-Speicherung beim Provider |
| Single-VPS (kein Failover) | Für aktuelle Last ausreichend, Failover geplant Q3 2026 |
| Kein Pen-Test-Programm | Geplant für Q3 2026, manuelle Reviews aktiv |

## 4. Organisatorische Maßnahmen

| Bereich | Maßnahme | Status |
|---------|----------|--------|
| **Sicherheitsorganisation** | Security Officer (NeXifyAI), CEO (Gesamtverantwortung) | ✅ |
| **Richtlinien** | Security Policy, Vulnerability Policy, Incident Response Plan | ✅ |
| **Schulung** | Security-Awareness via automatisierte Scans | 🔄 Geplant |
| **Lieferantenmanagement** | AVV mit Subprozessoren (OpenRouter, Vercel, Resend) | ✅ |

## 5. Technische Maßnahmen

| Bereich | Maßnahme | Status |
|---------|----------|--------|
| **Zugriffskontrolle** | JWT + RBAC + Supabase RLS | ✅ |
| **Verschlüsselung** | TLS 1.3 für alle externen Endpoints | ✅ |
| **Netzwerksicherheit** | Docker-Netzwerk-Isolation, Cloudflared Tunnel | ✅ |
| **Endpoint-Security** | Gitleaks, Dependabot, Trivy in CI/CD | ✅ |
| **Logging & Monitoring** | Prometheus, Grafana, Loki, Audit-Log | ✅ |
| **Backup** | WAL (PostgreSQL), tägliche MongoDB-Dumps | ✅ |
| **Patch-Management** | Dependabot automatisierte PRs, wöchentliches Review | ✅ |

## 6. Incident-Management

Siehe [Incident Response Plan](../policies/incident-response-plan.md)

| Phase | Beschreibung | Verantwortlich |
|-------|-------------|---------------|
| Erkennung | Prometheus, Uptime Kuma, Health-Score | Automatisiert |
| Triage | SEV1-SEV4 Klassifikation (< 15 Min) | Security Officer |
| Eindämmung | Service-Isolation, Backup-Aktivierung | DevOps |
| Behebung | Hotfix/Rollback | Tech Lead |
| Nachbereitung | Postmortem, Lessons Learned | Team |

## 7. Kontinuierliche Verbesserung

| Maßnahme | Rhythmus | Nachweis |
|----------|----------|----------|
| Health-Score Auswertung | Täglich | Cron-Job (health-score.py) |
| Dependabot Review | Wöchentlich | GitHub Security Tab |
| Log-Review (Security) | Wöchentlich | Grafana/Loki |
| Incident-Review | Nach jedem SEV1/SEV2 | Postmortem-Dokument |
| ISMS-Review | Quartalsweise | Dieses Dokument |
| Pen-Test | Jährlich | Externer Auditor |

## 8. Verweise

- [Security Policy](../policies/security-policy.md)
- [Vulnerability Policy](../policies/vulnerability-policy.md)
- [Incident Response Plan](../policies/incident-response-plan.md)
- [VVT (Verarbeitungsverzeichnis)](../legal/vvt.md)
- [DSFA (Datenschutz-Folgenabschätzung)](../legal/dsfa.md)
- [RACI-Matrix](../governance/raci.yaml)
- [Operational Constitution](../../operational-constitution.md)