# Verzeichnis von Verarbeitungstätigkeiten (VVT)
# gemäß Art. 30 DSGVO
# neXify - Chat it. Automat it. (KvK 90483944)

**Verantwortlicher:** Pascal Courbois, CEO
**Stand:** 2026-05-08

---

## 1. Plattform-Betrieb (SaaS-Dienstleistung)

| Feld | Inhalt |
|------|--------|
| **Verarbeitungstätigkeit** | Betrieb der NeXifyAI-Plattform (SaaS) |
| **Zweck** | Bereitstellung von KI-Agenten, Automationen und Web-Applikationen |
| **Rechtsgrundlage** | Art. 6(1)(b) DSGVO (Vertragserfüllung) |
| **Datenkategorien** | Kontaktdaten, Vertragsdaten, Kommunikationsdaten |
| **Betroffene Personen** | Kunden, Interessenten |
| **Empfänger** | Subprozessoren (OpenRouter, Vercel, Resend, Hostinger) |
| **Speicherdauer** | Vertragslaufzeit + 10 Jahre (gesetzliche Aufbewahrung) |
| **TOM** | TLS, RBAC, RLS, Audit-Logging, Backups |
| **Drittlandtransfer** | US (OpenRouter, Vercel, Resend) — mit DPA |

---

## 2. Kundenkommunikation (E-Mail, Chat, WhatsApp)

| Feld | Inhalt |
|------|--------|
| **Verarbeitungstätigkeit** | KI-gestützte Kundenkommunikation |
| **Zweck** | Support, Lead-Management, Automations |
| **Rechtsgrundlage** | Art. 6(1)(b) DSGVO, Art. 6(1)(f) DSGVO (berechtigtes Interesse) |
| **Datenkategorien** | Kommunikationsinhalte, Kontaktdaten, Metadaten |
| **Betroffene Personen** | Kunden, Interessenten, Website-Besucher |
| **Empfänger** | OpenRouter (LLM-Verarbeitung), Hostinger (E-Mail-Hosting) |
| **Speicherdauer** | 3 Jahre nach letztem Kontakt |
| **TOM** | TLS, End-to-End-Verschlüsselung (WhatsApp) |

---

## 3. Web-Analytics und Tracking

| Feld | Inhalt |
|------|--------|
| **Verarbeitungstätigkeit** | Anonymisierte Web-Analytics (Plausible CE, internes Tracking) |
| **Zweck** | Nutzungsanalyse, Conversion-Optimierung, System-Monitoring |
| **Rechtsgrundlage** | Art. 6(1)(f) DSGVO (berechtigtes Interesse) |
| **Datenkategorien** | Seitenaufrufe, Klicks, Scroll-Tiefe (anonymisiert) |
| **Betroffene Personen** | Website-Besucher |
| **Empfänger** | Keine (Self-Hosted Plausible CE) |
| **Speicherdauer** | 26 Monate (aggregiert), 90 Tage (Rohdaten) |
| **TOM** | IP-Anonymisierung, kein Cookie (Plausible), Opt-out möglich |

---

## 4. Cookie-Consent-Management

| Feld | Inhalt |
|------|--------|
| **Verarbeitungstätigkeit** | Speicherung von Cookie-Einwilligungen |
| **Zweck** | DSGVO-Compliance-Nachweis (Art. 7 DSGVO) |
| **Rechtsgrundlage** | Art. 6(1)(c) DSGVO (rechtliche Verpflichtung) |
| **Datenkategorien** | Consent-Präferenzen, IP-Hash, Zeitstempel |
| **Betroffene Personen** | Website-Besucher |
| **Empfänger** | Keine |
| **Speicherdauer** | 2 Jahre (gesetzliche Nachweisfrist) |
| **TOM** | IP-Hashing, Supabase RLS |

---

## 5. E-Mail-Marketing (Newsletter, Automations)

| Feld | Inhalt |
|------|--------|
| **Verarbeitungstätigkeit** | Newsletter-Versand und E-Mail-Automationen |
| **Zweck** | Marketing-Kommunikation, Lead-Nurturing |
| **Rechtsgrundlage** | Art. 6(1)(a) DSGVO (Einwilligung) |
| **Datenkategorien** | E-Mail-Adresse, Name, Consent-Datum, Interaktionsdaten |
| **Betroffene Personen** | Newsletter-Abonnenten |
| **Empfänger** | Resend (Transaktions-E-Mails) |
| **Speicherdauer** | Bis Widerruf der Einwilligung |
| **TOM** | Double-Opt-in, Abmelde-Link in jeder E-Mail |

---

**Letzte Aktualisierung:** 2026-05-08
**Nächste Prüfung:** 2026-08-08 (quartalsweise)
