# Auftragsverarbeitungs-Verzeichnis (Art. 28 DSGVO)

**Stand:** 2026-05-30
**Verantwortlicher:** Pascal Courbois, NeXifyAI (KvK 90483944)
**Letzte Aktualisierung:** 30.05.2026

---

## 1. Identität des Verantwortlichen

| Feld | Wert |
|------|------|
| Unternehmen | NeXifyAI — neXify (Chat it. Automate it.) |
| Verantwortlicher | Pascal Courbois, Geschäftsführer |
| Adresse | Graaf van Loonstraat 1E, 5921 JA Venlo, Niederlande |
| E-Mail | support@nexify-automate.com |
| Telefon | +31 6 133 188 56 |
| Handelsregister | KvK 90483944 |
| USt-ID | NL865786276B01 |

---

## 2. Subprozessoren-Übersicht

| # | Subprozessor | Leistung | Standort | DPA-Status | Kritisch |
|---|-------------|----------|----------|------------|----------|
| 1 | **Supabase** (PostgreSQL, Auth, Storage) | Datenbank, Authentifizierung, Dateispeicher | USA (EU-Hosting wählbar) | ✅ Geschlossen | **Hoch** |
| 2 | **Vercel** | Frontend-Hosting, Deployment | USA (global CDN) | ✅ Geschlossen | Mittel |
| 3 | **OpenRouter** | LLM/Embedding-API (DeepSeek, Qwen) | USA | ✅ Geschlossen | **Hoch** |
| 4 | **Resend** | E-Mail-Versand (Transaktionsmails) | USA | ✅ Geschlossen | Mittel |
| 5 | **MongoDB** (Atlas/Self-Hosted) | Business-Daten (Leads, Conversations) | EU (Self-Hosted) | Nicht erforderlich | **Hoch** |
| 6 | **Cloudflare** | CDN, DNS, DDoS-Schutz, Tunnel | USA (global Edge) | ✅ Geschlossen | Mittel |
| 7 | **GitHub** | Source Code Management, CI/CD | USA | ✅ Geschlossen | Niedrig |
| 8 | **Stripe** (geplant) | Zahlungsabwicklung | USA | ⏳ In Prüfung | **Hoch** |
| 9 | **nscale** | GPU-Infrastruktur (via OpenRouter) | EU | ✅ Über OpenRouter-DPA | Mittel |

---

## 3. Detail: Kritische Subprozessoren

### 3.1 Supabase
| Feld | Wert |
|------|------|
| Verarbeitung | PostgreSQL-Datenbank, Authentifizierung, Dateispeicher |
| Datenkategorien | Kontaktdaten, Account-Daten, E-Mails |
| Standort | USA (US-East / EU-Frankfurt wählbar) |
| DPA | Geschlossen — Standard-Subprozessoren: AWS, Fly.io |
| Sub-Subprozessoren | AWS (Cloud Infrastructure), Fly.io (Hosting) |
| Weisungsgebundenheit | Vertraglich vereinbart |
| Kündigungsfrist | 30 Tage |

### 3.2 OpenRouter
| Feld | Wert |
|------|------|
| Verarbeitung | LLM-Inferenz (DeepSeek V4 Flash), Embedding (Qwen3-8B) |
| Datenkategorien | Chat-Verläufe (nicht gespeichert), Suchanfragen |
| Standort | USA |
| DPA | Geschlossen — API-Nutzung ohne dauerhafte Speicherung |
| Datenverarbeitung | Keine Speicherung von Input/Output nach Verarbeitung |
| Besonderheit | BYOK-Modell: Eigener API-Key, keine gemeinsame Tenant-Nutzung |

### 3.3 MongoDB (Self-Hosted)
| Feld | Wert |
|------|------|
| Verarbeitung | Business-Datenbank (Leads, Conversations, Quotes, Contracts) |
| Datenkategorien | Alle kundenbezogenen Geschäftsdaten |
| Standort | **EU** (Self-Hosted auf Hetzner VPS, Standort Deutschland/Niederlande) |
| DPA | **Nicht erforderlich** — Selbsterbrachte Verarbeitung im eigenen Verantwortungsbereich |
| Besonderheit | Kein Drittanbieter-Zugriff. Läuft in Docker auf eigenem VPS |

---

## 4. Auftragsverarbeitungs-Verträge (DPA)

| Subprozessor | DPA-Datum | DPA-Version | Prüfintervall |
|-------------|-----------|-------------|---------------|
| Supabase | Siehe DPA-Dokument | V1.0 | Jährlich |
| Vercel | Siehe DPA-Dokument | V1.0 | Jährlich |
| OpenRouter | Siehe DPA-Dokument | V1.0 | Jährlich |
| Resend | Siehe DPA-Dokument | V1.0 | Jährlich |
| Cloudflare | Siehe DPA-Dokument | V1.0 | Jährlich |
| GitHub | Siehe DPA-Dokument | V1.0 | Jährlich |

---

## 5. Verarbeitungstätigkeiten pro Subprozessor

| Subprozessor | Zweck | Datenkategorien | Speicherdauer | Löschbarkeit |
|-------------|-------|----------------|--------------|--------------|
| Supabase | Authentifizierung, DB-Speicherung | E-Mail, Name, Passwort-Hash | Vertragsdauer + 36 Monate | ✅ Kaskadiert |
| Vercel | Frontend-Auslieferung | Keine personenbezogenen Daten | - | - |
| OpenRouter | KI-Textgenerierung | Chat-Input (flüchtig) | 0 (nicht gespeichert) | ✅ Automatisch |
| Resend | Transaktions-E-Mails | E-Mail-Adresse, Name | 90 Tage (Logs) | ✅ Auf Anfrage |
| MongoDB | Business-Daten speichern | Leads, Conversations, Quotes | Vertragsdauer + 36 Monate | ✅ Manuell |
| Cloudflare | CDN, DDoS | IP-Adresse (anonymisiert) | 7 Tage | ✅ Automatisch |
| GitHub | Source Code, CI/CD | Keine Kundendaten | - | - |
| Stripe | Zahlungen | Transaktionsdaten (keine Karten) | 10 Jahre (gesetzlich) | ✅ Anonymisiert |
| nscale | GPU/Embedding | Embedding-Vektoren (anonym) | Dauerhaft (anonymisiert) | ✅ Über Qdrant |

---

## 6. Prüf- und Weisungsrechte

| Recht | Umsetzung |
|-------|-----------|
| **Prüfrecht** | Quartalsweise Prüfung der DPA-Einhaltung |
| **Weisungsrecht** | Jederzeit per E-Mail an Subprozessor (Support-Kopie) |
| **Kündigungsrecht** | 30 Tage Kündigungsfrist (Subprozessor-Vertrag) |
| **Datenherausgabe** | 30 Tage nach Vertragsende |
| **Datenlöschung** | 90 Tage nach Vertragsende (Nachfrist für Backup-Rotation) |

---

## 7. Änderungshistorie

| Datum | Version | Änderung |
|-------|---------|----------|
| 2026-05-30 | 1.0 | Initiale Erstellung — 9 Subprozessoren dokumentiert |

---

## 8. Verweise

- [DPA/AVV (Hauptdokument)](./dpa-nexifyai.md)
- [VVT (Verarbeitungsverzeichnis)](./vvt.md)
- [DSFA (Datenschutz-Folgenabschätzung)](./dsfa.md)
- [Löschkonzept](./loeschkonzept.md)
- [Betroffenenrechte](./betroffenenrechte.md)