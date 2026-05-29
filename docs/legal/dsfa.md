# Datenschutz-Folgenabschaetzung (DSFA)
# gemaess Art. 35 DSGVO

**Stand:** 2026-05-29
**Verantwortlicher:** Pascal Courbois, CEO
**Erstellt durch:** NeXifyAI (goose, automated compliance scan)

---

## 1. Beschreibung der Verarbeitungstaetigkeit

| Feld | Inhalt |
|------|--------|
| **Name** | KI-gestuetzte Kundenkommunikation & Automation |
| **Zweck** | Automatisierte Lead-Bearbeitung, Angebotserstellung, Kundenkommunikation via Chat/E-Mail/Portal |
| **System** | NeXifyAI Plattform (FastAPI Backend + React Frontend + Qdrant Vector DB + OpenRouter LLM) |
| **Verantwortlicher** | Pascal Courbois, neXify (KvK 90483944) |
| **Rechtsgrundlage** | Art. 6(1)(b) DSGVO (Vertragserfuellung), Art. 6(1)(f) DSGVO (berechtigtes Interesse) |

## 2. Risikobewertung

### 2.1 Kategorien betroffener Personen
- Kunden (Bestandskunden mit Vertrag)
- Interessenten (Leads, Website-Besucher)
- Mitarbeiter des Kunden (bei internen KI-Agenten)

### 2.2 Datenkategorien
| Kategorie | Sensitivitaet | Begruendung |
|-----------|-------------|------------|
| Name, E-Mail, Telefon | Niedrig | Standard-Kontaktdaten |
| Kommunikationsinhalte | Mittel | Koennen sensible Geschaeftsinformationen enthalten |
| Vertragsdaten (Angebote, Rechnungen) | Mittel | Enthalten Umsatz- und Preisinformationen |
| Chat-Verlaeufe | Mittel | Koennen strategische Informationen enthalten |

### 2.3 Risikomatrix

| Risiko | Eintrittswkeit | Schwere | Risikowert | Massnahme |
|--------|----------------|---------|------------|----------|
| Unbefugter Zugriff auf Kundenkonten | Niedrig | Hoch | Mittel | 2FA, JWT, Rate-Limiting, Audit-Log |
| Datenleck durch LLM-Provider | Niedrig | Hoch | Mittel | DPA mit OpenRouter, keine Speicherung von Rohdaten beim Provider |
| Falsch-positive Lead-Klassifikation | Mittel | Niedrig | Niedrig | Human-in-the-Loop bei kritischen Entscheidungen |
| DSGVO-Verstoss durch automatischen Outreach | Niedrig | Mittel | Niedrig | Legal Gate (legal_guardian.py) vor jedem Outreach |
| Verlust von Kundendaten | Niedrig | Hoch | Mittel | Taegliche Backups, MongoDB Replica Set |

### 2.4 Technische und organisatorische Massnahmen (TOM)

| Bereich | Massnahme | Status |
|---------|----------|--------|
| Zugriffskontrolle | JWT + RBAC (Admin/Kunde/System) | ✅ |
| Verschlüsselung | TLS fuer alle externen Endpoints | ✅ |
| Datenminimierung | Nur notwendige Daten fuer jeweiligen Prozess | ✅ |
| Loeschkonzept | Automatisierte Loesch-Cron-Jobs + manueller Prozess | ✅ |
| Auftragsverarbeitung | AVV mit allen Subprozessoren | ✅ |
| Pseudonymisierung | SHA-256-Hashing bei Archivdaten | ✅ |
| Audit-Trail | Alle Aktionen protokolliert (audit_log) | ✅ |

## 3. Notwendigkeit der DSFA

Gemaess Art. 35 Abs. 1 DSGVO ist eine DSFA erforderlich wenn:
- Systematische und umfassende Bewertung persoenlicher Aspekte (KI-Agenten analysieren Kunden)
- Verarbeitung in grossem Umfang (SaaS-Plattform mit potenziell vielen Kunden)
- Ueberwachung oeffentlich zugaenglicher Bereiche (Website-Tracking)

**Ergebnis: DSFA erforderlich -- hiermit durchgefuehrt.**

## 4. Ergebnis

| Bewertung | Wert |
|-----------|------|
| Gesamtrisiko | **GERING** (nach Massnahmen) |
| Restrisiko | Akzeptabel |
| Prioritaet | Keine zusaetzlichen Massnahmen erforderlich |
| Naechste Ueberpruefung | 2026-08-29 (quartalsweise) |

## 5. Verweise

- [VVT (Verarbeitungsverzeichnis)](./vvt.md)
- [Loeschkonzept (DSGVO Art. 17)](./loeschkonzept.md)
- [AVV / DPA](./dpa-nexifyai.md)
- [Datenschutzerklaerung](./datenschutzerklaerung.md)
- [Cookie-Banner](./cookie-banner.md)