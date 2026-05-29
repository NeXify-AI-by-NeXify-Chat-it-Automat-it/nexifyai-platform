# Incident Response Plan (IRP)

**Stand:** 2026-05-29
**Verantwortlich:** NeXifyAI Security Officer / Pascal Courbois
**Geltungsbereich:** NeXifyAI Plattform (gesamte Infrastruktur)

---

## 1. Incident-Klassifikation

| Stufe | Name | Beispiele | Reaktionszeit | Eskalation |
|-------|------|-----------|---------------|------------|
| **SEV1** | Critical | Datenleck, Ausfall aller Systeme, Security-Breach | < 15 Min | CEO + Security Officer |
| **SEV2** | High | Teilausfall (z.B. Brain API down), Performance-Degradation | < 1 Std | Tech Lead + DevOps |
| **SEV3** | Medium | Einzelfeatures nicht verfuegbar, UI-Fehler | < 4 Std | Developer |
| **SEV4** | Low | Kosmetische Fehler, Dokumentationsluecken | < 48 Std | Product Owner |

## 2. Detection-Quellen

| Quelle | Mechanismus | Reaktionszeit |
|--------|-------------|---------------|
| Prometheus/Alerts | Grafana Dashboard + Alertmanager | Echtzeit |
| Uptime Kuma | HTTP-Health-Checks alle 60s | 1 Min |
| Health-Score Cron | Alle 30 Min | 30 Min |
| Dead-Letter-Queue | Alle 2 Std | 2 Std |
| Dependabot | GitHub Security Alerts | Taeglich |
| Gitleaks | Pre-Commit Hook | Commit-Zeitpunkt |
| Kunden-Support | E-Mail / Chat | 4 Std (Geschaeftszeiten) |

## 3. Incident-Response-Prozess

### 3.1 Triage (15 Min bei SEV1, 1h bei SEV2)

1. **Betroffene Systeme** identifizieren (Brain, API, Frontend, DB)
2. **Schweregrad** bestimmen (SEV1-SEV4)
3. **Erste Massnahme** festlegen (Containment / Fix / Beobachten)
4. **Verantwortlichen** zuweisen

### 3.2 Containment

| SEV | Containment-Massnahme |
|-----|---------------------|
| SEV1 | System isolieren, Zugriff entziehen, Backup aktivieren |
| SEV2 | Service neustarten, Feature deaktivieren, Traffic umleiten |
| SEV3 | Hotfix deployen, Workaround dokumentieren |
| SEV4 | Ticket erstellen, naechster Sprint |

### 3.3 Root Cause Analysis (RCA)

Jeder SEV1/SEV2 Incident erhaelt eine RCA:
1. **Timeline** des Incidents
2. **Ursache** (technisch/menschlich/prozessual)
3. **Impact** (betroffene Kunden, Daten, Systeme)
4. **Gegenmassnahme** (was wurde gemacht)
5. **Praeventivmassnahme** (was verhindert Wiederholung)

### 3.4 Postmortem

Jeder Incident >= SEV2 erhaelt ein Postmortem in `docs/incidents/`:
- Format: `INCIDENT-NNN-title.md`
- Template: `docs/incidents/INCIDENT_TEMPLATE.md`
- Enthaelt: 5 Whys, Lessons Learned, Prevention Registry Eintrag

## 4. Kommunikationsmatrix

| Stakeholder | SEV1 | SEV2 | SEV3 | SEV4 |
|-------------|------|------|------|------|
| CEO (Pascal) | Sofort telefonisch | 30 Min E-Mail | Taeglich E-Mail | Woechentlich |
| Team (DevOps) | Sofort | Sofort | 1 Std E-Mail | Ticket |
| Kunden | 1 Std E-Mail | 4 Std E-Mail | Keine Info | Keine Info |
| Aufsichtsbehoerde | 72 Std E-Mail (DSGVO) | Nur bei Datenleck | - | - |

## 5. Wiederherstellungsziele (RPO/RTO)

| System | RPO (Datenverlust) | RTO (Ausfallzeit) |
|--------|-------------------|-------------------|
| Supabase (PostgreSQL) | 1 Std (WAL-Backups) | 15 Min |
| MongoDB | 1 Std (konsistentes Backup) | 30 Min |
| Qdrant (Vektordaten) | 24 Std (Snapshots) | 1 Std |
| Redis (Cache) | 0 (nicht persistent) | 5 Min |
| Brain API | 24 Std | 30 Min |
| Frontend (Vercel) | 0 (Git-gesichert) | 2 Min |

## 6. Praevention & Kontinuierliche Verbesserung

| Massnahme | Rhythmus | Verantwortlich |
|-----------|----------|---------------|
| Health-Score Auswertung | Taeglich | NeXifyAI |
| Dependabot Review | Woechentlich | Tech Lead |
| Log-Review (Security) | Woechentlich | Security Officer |
| Backup-Restore-Test | Monatlich | DevOps |
| Incident-Review | Nach jedem SEV1/SEV2 | Team |
| Pen-Test (geplant) | Jaehrlich | Externer Auditor |

## 7. Verweise

- [Security Policy](./security-policy.md)
- [Vulnerability Policy](./vulnerability-policy.md)
- [Incidents (aktiv)](../incidents/INDEX.md)
- [Incident Template](../incidents/INCIDENT_TEMPLATE.md)
- [RACI-Matrix](../governance/raci.yaml)
- [operational-constitution.md](../../operational-constitution.md)