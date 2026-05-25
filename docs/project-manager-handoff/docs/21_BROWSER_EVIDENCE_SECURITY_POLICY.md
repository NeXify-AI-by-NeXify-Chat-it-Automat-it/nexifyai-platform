# Browser Evidence Runner Security Policy

**Version:** 1.0
**Stand:** 2026-05-25
**Status:** active_managed
**Owner:** Project Manager

---

## Zweck

Diese Policy regelt den sicheren Einsatz von browserbasierten Evidence-Runnern (wie Microsoft Webwright) unter der NeXify Project Manager Control Plane.

## Grundregeln

### 1. Keine echten Secrets im Browser-Agent

**Verboten:**
- Produktive Admin-Passwörter
- Echte Kunden-Zugangsdaten
- API-Keys (Brain, GitHub, Supabase, Vercel, 9Router)
- Persönliche Tokens
- Produktive Service-Accounts

**Erlaubt:**
- Dedizierte Testaccounts mit minimalen Rechten
- Kurzlebige Tokens (max 1h)
- Read-only Zugänge
- Sandbox-/Staging-Umgebungen

### 2. Domain-Allowlist

Nur getestete Domains dürfen angesteuert werden:

**Erlaubte Domains (konfigurierbar):**
- Agenturseite: `nexifyai.cloud`, Staging-Domains
- Kundenprojekte: Explizit freigegebene Kundendomains
- Eigene Services: Brain, GitHub (nur UI-Checks)

**Verboten:**
- Beliebige externe Domains ohne Freigabe
- Wettbewerber-Seiten
- Seiten mit Login-Walls, deren ToS automatisierte Zugriffe verbieten

### 3. Keine Passwörter in Prompts

Passwörter, Tokens, API-Keys werden NUR via geschützte Environment Variables gesetzt, nie im Prompt, nie im Log, nie im Repo.

### 4. Output Secret-Leak Scan

Jeder Browser-Run muss auf Secret-Leaks gescannt werden:
- Screenshots auf sichtbare Credentials prüfen
- Logs auf Token-Muster scannen
- Kein Output darf Secrets enthalten

### 5. Rate Limits

| Resource | Limit |
|----------|-------|
| Requests pro Domain | Max 10/min |
| Parallele Browser-Sessions | Max 3 |
| Parallele Tests gesamt | Max 5 |
| Screenshots pro Run | Max 50 |
| Run-Dauer | Max 30min |
| Speicher pro Run | Max 500MB |

### 6. Keine produktiven Schreibaktionen

**Verboten ohne explizite Freigabe:**
- Formulare absenden (außer Testformulare)
- Bestellungen auslösen
- Daten löschen
- Admin-Aktionen
- Deployment-Trigger
- Zahlungsvorgänge

**Erlaubt mit Read-Only-Modus:**
- Seiten laden
- Screenshots erstellen
- DOM inspizieren
- Links prüfen (HEAD/GET)
- Console-Logs erfassen

### 7. Screenshot- und Log-Redaction

Vor Speicherung:
- IP-Adressen maskieren
- Session-Cookies aus Logs entfernen
- PII (Namen, E-Mails, Telefonnummern) maskieren
- Interne URLs normalisieren
- Keine Full-Page-Screenshots von Seiten mit Kundendaten

### 8. Keine aggressiven Scraper

**Verboten:**
- robots.txt ignorieren
- Crawl-Delays unterschreiten
- CAPTCHAs automatisch lösen
- Login-Walls umgehen
- ToS/Datenschutz verletzen
- DSGVO-Verstöße

**Pflicht:**
- robots.txt respektieren
- User-Agent identifizierbar setzen
- Crawl-Delays einhalten
- Nur öffentliche oder explizit freigegebene Seiten

### 9. Isolierte Ausführung

Jeder Browser-Run läuft in einer isolierten Umgebung:
- Eigener Workspace
- Keine persistierten Cookies/Sessions zwischen Runs
- Kein Zugriff auf Produktivdatenbanken
- Kein Zugriff auf andere Goose-Workspaces

### 10. Audit und Evidence

Jeder Run erzeugt:
- Task-ID Referenz
- Start/End-Timestamp
- Liste der besuchten URLs
- Anzahl Requests
- Screenshots (redacted)
- Logs (redacted)
- Erfolg/Fehler-Status
- Security-Scan-Ergebnis

## Enforcement

### Automatisch (geplant)

- Pre-Run Domain-Allowlist-Check
- Post-Run Secret-Scan
- Rate-Limit-Enforcement
- Timeout-Kill-Switch

### Manuell

- Neue Domains: nur nach Freigabe durch Project Manager
- Testaccounts: nur nach Security-Review
- Schreibaktionen: nur mit explizitem Approval-Flag

## Eskalation

Bei Verstoß:

1. **Run sofort stoppen**
2. **Logs sichern**
3. **Security-Issue erstellen**
4. **Project Manager Review**
5. **Domain/Account sperren bis Klärung**

## Integration

Diese Policy wird referenziert von:
- Project Manager Control Plane
- Goose Execution Policy
- Resource Lifecycle Policy
- Webwright Integration (wenn aktiviert)
