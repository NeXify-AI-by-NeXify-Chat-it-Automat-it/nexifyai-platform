# NeXifyAI — Incident Index
**Stand:** 2026-05-23 | **Owner:** system-doc-engineer
**Referenz:** `INCIDENT_TEMPLATE.md` — Vorlage für neue Incidents

---

## Aktive Incidents

| ID | Datum | SEV | Summary | Status |
|----|-------|-----|---------|--------|
| [INC-20260508-002](INCIDENT-002-build-error-blog-import.md) | 2026-05-08 | SEV2 | Build-Fehler blog.js/track.js Import | ✅ Closed |
| [INC-20260508-003](INCIDENT-003-vercel-deploy-all-errors.md) | 2026-05-08 | SEV1 | Alle Vercel-Deployments im Error (Double Export) | ✅ Closed |

---

## Incident Template

Neue Incidents mit `INCIDENT_TEMPLATE.md` anlegen. Benennung: `INCIDENT-NNN-kurzbeschreibung.md`.

### Template-Referenzen in bestehenden Incidents

- INC-20260508-002: deckt `{{INCIDENT_LINK}}` via Ad-hoc-Struktur ab
- INC-20260508-003: deckt `{{INCIDENT_LINK}}` via Ad-hoc-Struktur ab

---

## Postmortem-Verknüpfungen

| Incident | Postmortem |
|----------|-----------|
| INC-20260508-002 | `docs/incidents/INCIDENT-002-build-error-blog-import.md` |
| INC-20260508-003 | `docs/incidents/INCIDENT-003-vercel-deploy-all-errors.md` |

> **Hinweis:** Postmortems sind in denselben Dateien enthalten (== Incident-Datei). Keine separaten Postmortem-Dateien.
