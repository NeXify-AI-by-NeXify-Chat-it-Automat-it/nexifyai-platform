# Incident Postmortem Template

**Datum:** YYYY-MM-DD
**Severity:** SEV0 | SEV1 | SEV2 | SEV3 | SEV4
**Dauer:** [Startzeit] – [Endzeit] (XX Minuten)
**Autor:** [Rolle]
**Incident-ID:** INC-YYYY-NNN
**Referenz:** [[INDEX|Incident Index]] — Alle Incidents im Überblick

---

## Zusammenfassung
[Ein-Satz-Beschreibung des Vorfalls. Was ist passiert? Wer war betroffen?]

---

## Timeline (alle Zeiten in UTC)

| Zeit | Ereignis |
|------|----------|
| HH:MM | Erste Erkennung (Watchdog-Alert / User-Report / Monitoring) |
| HH:MM | Diagnose beginnt |
| HH:MM | Root Cause identifiziert |
| HH:MM | Fix deployed |
| HH:MM | Verifikation abgeschlossen |
| HH:MM | Service vollständig wiederhergestellt |

---

## Root Cause
[Technische Ursache. Nicht "Server war down" sondern WARUM.]

**Kategorie:**
- [ ] Code-Fehler (Bug)
- [ ] Infrastruktur (Server, Docker, Netzwerk)
- [ ] Externer Dienst (OpenRouter, Supabase, Vercel)
- [ ] Konfiguration (falsche .env, Traefik-Route)
- [ ] Human Error
- [ ] Security Incident

**Detaillierte Analyse:**

[Technische Erklärung. Logs, Stack-Traces, relevante Config-Snippets.]

---

## Impact

| Metrik | Wert |
|--------|------|
| Betroffene Nutzer | N |
| Davon aktiv gestört | N |
| Datenverlust | Ja / Nein |
| Finanzieller Schaden | €X (geschätzt) |
| Ausfallzeit (Total) | XX Minuten |
| Ausfallzeit (Partial) | XX Minuten |

---

## Resolution

[Was wurde konkret getan, um den Vorfall zu beheben?]

1. Schritt 1: [Beschreibung + Befehl/Code]
2. Schritt 2: [Beschreibung + Befehl/Code]
3. Verifikation: [Wie wurde geprüft dass es funktioniert?]

---

## Detection

**Wie wurde der Vorfall entdeckt?**
- [ ] Automatisch (Watchdog / Health-Check)
- [ ] User-Report
- [ ] Manuell (Monitoring-Dashboard)
- [ ] Externer Hinweis

**Time to Detect:** XX Minuten
**Time to Resolve:** XX Minuten

---

## Prevention (Action Items)

- [ ] **Maßnahme 1:** [Beschreibung] — Verantwortlich: [Rolle] — Deadline: YYYY-MM-DD
- [ ] **Maßnahme 2:** [Beschreibung] — Verantwortlich: [Rolle] — Deadline: YYYY-MM-DD
- [ ] **Maßnahme 3:** [Beschreibung] — Verantwortlich: [Rolle] — Deadline: YYYY-MM-DD

---

## Lessons Learned

1. [Was haben wir gelernt?]
2. [Was würden wir nächstes Mal anders machen?]
3. [Welcher Skill / welche Doku muss aktualisiert werden?]

---

## Anhänge

- Log-Auszug: `[Pfad]`
- Grafana/Screenshot: `[URL]`
- Related PR: `[URL]`
- Related ADR: `[ADR-NNN]`

---

**Postmortem erstellt:** YYYY-MM-DD
**Review durch:** [Rolle]
**Freigabe:** [Rolle]
