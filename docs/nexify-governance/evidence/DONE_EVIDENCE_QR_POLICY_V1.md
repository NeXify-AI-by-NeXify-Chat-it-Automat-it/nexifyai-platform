# DONE / Evidence / QR / Policy V1

**Status:** V1 — 2026-06-10
**Owner:** Team 12 — Review / QR / Evidence / DONE Audit
**Geltungsbereich:** Fertigstellungslogik, Evidence-Pflicht, Qualitätsreview und Policy Gates

## Verboten

- PARTIAL_DONE als DONE melden
- Datei erstellt = fertig
- Plan geschrieben = umgesetzt
- Lokal getestet = live
- Cron/Hook enabled = Autonomie
- UI sichtbar = funktional
- Brain behauptet = Brain nachgewiesen
- Evidence erwähnt = Evidence erstellt

## DONE-Definition

Eine Aufgabe ist erst DONE wenn alle diese Punkte erfüllt sind:

- [ ] Ziel verstanden
- [ ] Kontext geladen
- [ ] Repo/Live geprüft (falls relevant)
- [ ] Policy Gate entschieden
- [ ] Umsetzung erfolgt
- [ ] Integration hergestellt
- [ ] Getestet/geprüft
- [ ] Security geprüft (falls relevant)
- [ ] Evidence geschrieben
- [ ] Kanban aktualisiert
- [ ] Brain-Entscheidung getroffen
- [ ] agentmemory aktualisiert
- [ ] Folgeaufträge erzeugt
- [ ] Risiken dokumentiert
- [ ] Keine Secrets in Logs/Chat/Repo
- [ ] Keine ungenehmigten externen Writes

## Policy-Level

| Level | Bedeutung | Beispiele |
|-------|-----------|-----------|
| READ_ONLY | Nur lesen | Brain abfragen, Logs lesen |
| PLAN_ONLY | Nur planen | Architektur skizzieren, Konzept schreiben |
| WRITE_INTERNAL | Interne Writes | Governance-Dokumente, Strukturdateien, lokale Config |
| WRITE_CUSTOMER_RESTRICTED | Kundenprojekt-Writes | Kundendateien, Kunden-Brain (nur mit Scope-Prüfung) |
| ADMIN_APPROVAL_REQUIRED | Freigabe nötig | DNS, Deploy, Push, Secrets, Kundennachrichten |
| FORBIDDEN | Niemals ausführen | Secret-Logging, Datenvermischung, Fremdbranding |

## QR-Prozess

```text
Ergebnis
→ Evidence prüfen (vollständig?)
→ DONE-Checkliste abarbeiten
→ Policy-Level einhalten?
→ Keine Secrets?
→ Kanban/Brain/agentmemory aktuell?
→ Nächste Schritte dokumentiert?
→ QR bestanden? DONE
→ QR nicht bestanden? → PARTIAL_DONE + Korrektur auftrag
```

## Evidence-Pflicht

Jede relevante Arbeit erzeugt:
- Was wurde gemacht
- Welche Dateien/Systeme betroffen
- Tests/Prüfungen
- Risiken/Blocker
- Nächste Schritte
- Owner

