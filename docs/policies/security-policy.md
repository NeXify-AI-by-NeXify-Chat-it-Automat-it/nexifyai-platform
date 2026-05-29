# Security Policy
# DOS v2.0 Chapter 14: Security & Compliance

**Stand:** 2026-05-29 (aktualisiert)
**Verantwortlich:** NeXifyAI Security Officer / Pascal Courbois
**Geltungsbereich:** NeXifyAI Plattform & alle angeschlossenen Systeme

---

## 1. Grundprinzipien

1. **Defense in Depth** — Mehrere Sicherheitsschichten (Netzwerk, Applikation, Daten, Prozess)
2. **Least Privilege** — Minimal notwendige Rechte für jede Rolle
3. **Security by Design** — Sicherheit von Anfang an, nicht nachträglich
4. **Zero Trust** — Keine implizite Vertrauenswürdigkeit, jede Anfrage wird verifiziert
5. **Continuous Monitoring** — Automatisierte Überwachung aller Systeme

---

## 2. Basis-Sicherheitsstandard (alle Projekte)

| Massnahme | Status | Nachweis |
|-----------|--------|----------|
| HTTPS überall, HSTS gesetzt | ✅ | Traefik/Kong: HSTS 63072000s, includeSubDomains |
| CSP (Content Security Policy) | ✅ | In Vercel-Config definiert |
| RBAC (Role-Based Access Control) | ✅ | Admin/Kunde/System-Rollen |
| 2FA/MFA für Admin-Zugaenge | ✅ | JWT + Passwort + Magic Link |
| Secrets Management | ✅ | Nur in .env, vault, nie in Git |
| Dependency Scanning | ✅ | Dependabot in CI (taeglich) |
| Secret Scanning | ✅ | Gitleaks Pre-Commit Hook + CI |
| Input-Validierung | ✅ | Pydantic-Modelle fuer alle Endpoints |
| Rate Limiting | ✅ | SlowAPI 200/Min (Admin), 20/300s (Auth) |
| Audit-Logging | ✅ | Alle Aktionen in audit_log-Tabelle |

---

## 3. Erhoehter Standard (B2B/Enterprise)

| Massnahme | Status | Nachweis |
|-----------|--------|----------|
| AVV vor Produktiv-Deployment | ✅ | docs/legal/dpa-nexifyai.md |
| DSGVO-Dokumentation (VVT) | ✅ | docs/legal/vvt.md (vollstaendig) |
| DSFA bei risikoreichen Verarbeitungen | ✅ | docs/legal/dsfa.md (NEU) |
| EU AI Act Assessment | ✅ | docs/legal/eu-ai-act-assessment.md (NEU) |
| Incident Response Plan | ✅ | docs/policies/incident-response-plan.md (NEU) |
| Backup-Konzept (RPO/RTO definiert) | ✅ | 6 Systeme mit RPO/RTO |
| Loeschkonzept (DSGVO Art. 17) | ✅ | docs/legal/loeschkonzept.md (NEU) |
| Penetration-Test (jaehrlich) | ❌ Geplant | Externer Auditor Q3 2026 |
| Zugriffsaudits (quartalsweise) | ⏳ In Planung | Manuell via Audit-Log |

---

## 4. Technische Sicherheitsmassnahmen

### 4.1 Netzwerk

| Massnahme | Konfiguration |
|-----------|--------------|
| Firewall | Docker-Netzwerk-Isolation (Bridge-Netzwerke) |
| TLS | Traefik terminiert TLS an Edge, interne Kommunikation HTTP |
| VPN | Cloudflared Tunnel fuer Admin-Zugriff |
| Port-Exposure | Nur Ports 80/443 (Traefik), 8000 (Kong) nach aussen |

### 4.2 Applikation

| Massnahme | Implementierung |
|-----------|----------------|
| Authentifizierung | JWT (Admin) + Magic Link (Kunde) + Passwort (Portal) |
| Autorisierung | Supabase RLS auf allen Tabellen + RBAC |
| Session-Management | JWT mit 24h-Expiry, Refresh-Token |
| CSRF-Schutz | Same-Origin Policy + CORS-Whitelist |
| Security Headers | HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy |

### 4.3 Daten

| Massnahme | Implementierung |
|-----------|----------------|
| Verschlüsselung at Rest | PostgreSQL (Supabase) + MongoDB (kenein) |
| Verschlüsselung in Transit | TLS 1.3 fuer alle externen Verbindungen |
| Passwort-Hashing | bcrypt (Kundenkonten) |
| Pseudonymisierung | SHA-256-Hashing bei Archivdaten |
| Backups | WAL (PostgreSQL) + taegliche MongoDB-Dumps |

---

## 5. Retrieval-First vor jeder Integration

1. **CVE-Pruefung** (National Vulnerability Database)
2. **Lizenzpruefung** (MIT, Apache 2.0, BSD, ISC -- blockiert: GPL, AGPL, SSPL)
3. **Wartungsstatus** (aktiv maintained?)
4. **Breaking Changes** in letzten Releases
5. **Security Advisories** des Anbieters
6. **CI-Faehigkeit** (automatisierbar?)
7. **Template-Verfuegbarkeit** (erprobte Integration?)

---

## 6. Incident Response

| Dokument | Beschreibung |
|----------|-------------|
| `docs/policies/incident-response-plan.md` | Vollstaendiger IRP (neu) |
| `docs/incidents/INDEX.md` | Incident-Register |
| `docs/incidents/INCIDENT_TEMPLATE.md` | Postmortem-Vorlage |
| `docs/incidents/INCIDENT-002-*.md` | Historische Incidents |

---

## 7. Compliance-Dokumente (vollstaendig)

| Bereich | Dokumente | Status |
|---------|----------|--------|
| **DSGVO** | VVT, AVV, DSFA, Loeschkonzept, Datenschutzerklaerung, Cookie-Banner, Impressum | ✅ 9 Docs |
| **EU AI Act** | Risk Assessment | ✅ 1 Doc |
| **Incident Management** | IRP, Incident-Template | ✅ 2 Docs |
| **Sicherheit** | Security Policy, Vulnerability Policy | ✅ 2 Docs |
| **Governance** | Operational Constitution, DOS Compliance Matrix | ✅ 2 Docs |
| | **Gesamt: 16 Compliance-Dokumente** | ✅ **Vollstaendig** |
