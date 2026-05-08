# Data Processing Agreement (DPA) — Auftragsverarbeitungsvertrag (AVV)
# neXify - Chat it. Automat it. (KvK 90483944)

## 1. Vertragsparteien

**Verantwortlicher (Kunde):**
- Unternehmen: [KUNDENNAME]
- Adresse: [KUNDENADRESSE]
- Ansprechpartner: [KONTAKT]

**Auftragsverarbeiter (NeXify):**
- Unternehmen: neXify - Chat it. Automat it.
- Adresse: Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande
- KvK: 90483944
- USt-ID: NL865786276B01
- Kontakt: support@nexify-automate.com | +31 6 133 188 56

---

## 2. Gegenstand und Dauer der Verarbeitung

**Gegenstand:** Bereitstellung von KI-Agenten, Automations-Workflows und Web-Applikationen als SaaS-Dienstleistung.

**Dauer:** Laufzeit des Hauptvertrags zzgl. gesetzlicher Aufbewahrungsfristen.

---

## 3. Art und Zweck der Datenverarbeitung

| Verarbeitung | Zweck | Rechtsgrundlage |
|-------------|-------|----------------|
| Kundenkommunikation (E-Mail, Chat) | Support, Lead-Management, Automations | Art. 6(1)(b) DSGVO |
| Vertragsdaten (Angebote, Rechnungen) | Vertragserfüllung, Buchhaltung | Art. 6(1)(b) DSGVO |
| Nutzungsdaten (Analytics, Logs) | System-Optimierung, Security | Art. 6(1)(f) DSGVO |
| Cookie-Consent-Daten | DSGVO-Compliance-Nachweis | Art. 6(1)(c) DSGVO |

---

## 4. Kategorien betroffener Personen

- Kunden und Interessenten des Verantwortlichen
- Mitarbeiter des Verantwortlichen (bei internen KI-Agenten)
- Website-Besucher (bei Analytics und Cookie-Consent)

---

## 5. Datenkategorien

| Kategorie | Beispiele |
|-----------|----------|
| Kontaktdaten | Name, E-Mail, Telefon, Unternehmen |
| Vertragsdaten | Angebote, Rechnungen, Vertragsdokumente |
| Kommunikationsdaten | Chat-Verläufe, E-Mails, Support-Tickets |
| Nutzungsdaten | Seitenaufrufe, Klicks, Session-Dauer (anonymisiert) |
| Consent-Daten | Cookie-Präferenzen, Einwilligungszeitpunkt |

---

## 6. Technische und organisatorische Maßnahmen (TOM)

| Maßnahme | Beschreibung |
|----------|-------------|
| Zugangskontrolle | SSH-Key-Auth, 2FA für Admin-Zugänge, Firewall (UFW) |
| Zugriffskontrolle | RBAC (public, portal, staff, admin), Row-Level-Security |
| Weitergabekontrolle | TLS 1.3 (HTTPS), API-Key-Auth für externe Endpunkte |
| Eingabekontrolle | Protokollierung aller Datenzugriffe (audit_logs) |
| Auftragskontrolle | Isolierte Tenant-Umgebungen, keine Datenvermischung |
| Verfügbarkeitskontrolle | Tägliche Backups, Watchdog-Monitoring, 99.9% Uptime |
| Trennungskontrolle | Separate Supabase-Schemas/RLS pro Tenant |

---

## 7. Unterauftragsverhältnisse

Der Auftragsverarbeiter setzt folgende Subprozessoren ein:

| Subprozessor | Zweck | Sitz | DPA |
|-------------|-------|-----|-----|
| OpenRouter | LLM API | US | ✅ Vorhanden |
| Vercel | Frontend Hosting | US/EU | ✅ Vorhanden |
| Resend | Transaktions-E-Mails | US | ✅ Vorhanden |
| Hostinger | VPS Hosting | EU (NL) | ❌ Fehlt |
| Supabase (Self-Hosted) | Datenbank + Auth | EU (VPS) | N/A (selbst gehostet) |

Änderungen an Subprozessoren werden dem Verantwortlichen 30 Tage vorab mitgeteilt.

---

## 8. Betroffenenrechte

Der Auftragsverarbeiter unterstützt den Verantwortlichen bei der Erfüllung von Betroffenenrechten:
- **Auskunft (Art. 15):** Datenexport innerhalb 30 Tage
- **Berichtigung (Art. 16):** Direkte Korrektur in Datenbank
- **Löschung (Art. 17):** Automatisierte Lösch-Routinen
- **Einschränkung (Art. 18):** Account-Suspendierung
- **Datenportabilität (Art. 20):** Export in maschinenlesbarem Format (JSON/CSV)

---

## 9. Weisungsbefugnisse und Kontrollrechte

Der Verantwortliche hat das Recht:
- Weisungen zur Datenverarbeitung zu erteilen
- Die Einhaltung der TOM zu überprüfen (Audit, 1x jährlich)
- Bei Verstößen fristlose Kündigung des AVV

---

## 10. Meldepflichten bei Datenschutzverletzungen

Bei einer Datenschutzverletzung (Art. 33, 34 DSGVO) meldet der Auftragsverarbeiter:
- An den Verantwortlichen: **innerhalb 24 Stunden**
- An die Aufsichtsbehörde: **innerhalb 72 Stunden** (durch den Verantwortlichen)
- An betroffene Personen: **unverzüglich** bei hohem Risiko

---

**Unterschrift (Verantwortlicher):**
_________________________
[Datum, Ort, Name]

**Unterschrift (Auftragsverarbeiter):**
_________________________
Pascal Courbois, CEO neXify - Chat it. Automat it.
