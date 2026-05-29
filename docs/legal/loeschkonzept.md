# Löschkonzept nach DSGVO Art. 17

**Stand:** 2026-05-29  
**Verantwortlich:** NeXifyAI / Pascal Courbois  
**Rechtsgrundlage:** Art. 17 DSGVO (Recht auf Löschung / „Recht auf Vergessenwerden")

---

## 1. Geltungsbereich

Dieses Löschkonzept gilt für alle personenbezogenen Daten, die durch die NeXifyAI-Plattform verarbeitet werden:

| Kategorie | Beispiele | Speicherort |
|-----------|-----------|-------------|
| Kundenstammdaten | Name, E-Mail, Telefon, Adresse | Supabase (PostgreSQL), MongoDB |
| Kontaktdaten (Leads) | Firmenname, E-Mail, Branche | Qdrant, MongoDB, Supabase |
| Kommunikationsdaten | Chat-Verläufe, E-Mails, Portal-Nachrichten | MongoDB, Qdrant |
| Vertragsdaten | Angebote, Rechnungen, Verträge | Supabase, MongoDB |
| Zahlungsdaten | Transaktionshistorie (nur Status, keine Karten) | Supabase |
| Systemdaten | IP-Adressen, Logs, Audit-Trails | Prometheus, Loki, OTEL |

---

## 2. Löschfristen

| Datenkategorie | Regellöschfrist | Löschgrund |
|---------------|-----------------|------------|
| Chat-Verläufe | 36 Monate nach letzter Aktivität | Vertragsbeendigung + gesetzl. Aufbewahrung |
| Leads (nicht konvertiert) | 12 Monate nach Ersterfassung | Keine Rechtsgrundlage mehr |
| Leads (opt-out) | **Sofort** nach Opt-Out | Widerspruch Art. 21 DSGVO |
| Kundenkonten | 36 Monate nach Vertragsende | Steuerliche Aufbewahrungspflicht (§ 147 AO) |
| Angebote/Rechnungen | 10 Jahre nach Erstellung | Gesetzliche Aufbewahrungspflicht |
| Audit-Logs | 12 Monate | Nachweispflicht, dann irrelevant |
| Web-Analytics | 26 Monate (TTDSG-konform) | Maximale Speicherdauer nach TTDSG |
| Sicherheits-Logs | 6 Monate | Erkennung von Angriffsmustern |
| IP-Adressen (anonymisiert) | 7 Tage | Log-Aufbewahrung |

---

## 3. Löschprozess

### 3.1 Kundeninitiierte Löschung (Art. 17 Abs. 1)

Der Kunde kann jederzeit die Löschung seiner Daten verlangen:

1. **Formloser Antrag** per E-Mail an support@nexify-automate.com
2. **Identitätsprüfung** durch Support (E-Mail-Bestätigung + optional Video-Ident)
3. **Löschung innerhalb von 30 Tagen** (Art. 17 Abs. 2 DSGVO)

```yaml
Löschprozess:
  - Schritt 1: Antragseingang → Ticket im System
  - Schritt 2: Identitätsprüfung (24h)
  - Schritt 3: Prüfung auf Ausnahmen (§ 147 AO, Art. 17 Abs. 3)
  - Schritt 4: Löschung der nicht-aufbewahrungspflichtigen Daten
  - Schritt 5: Anonymisierung der aufbewahrungspflichtigen Daten
  - Schritt 6: Löschbestätigung an Kunden
  - Schritt 7: Dokumentation im Löschregister
```

### 3.2 Automatisierte Löschung (Cron-Jobs)

| Job | Rhythmus | Aktion |
|-----|----------|--------|
| `cleanup-expired-leads` | Täglich 03:00 | Löscht Leads > 12 Monate ohne Conversion |
| `cleanup-optouts` | Stündlich | Löscht Leads mit aktivem Opt-Out sofort |
| `cleanup-anonymized-ips` | Täglich 03:00 | Löscht IPs > 7 Tage |
| `cleanup-stale-sessions` | Täglich 03:00 | Löscht Sessions > 90 Tage ohne Aktivität |

### 3.3 Technische Löschung

| System | Löschmethode | Besonderheit |
|--------|-------------|--------------|
| Supabase | `DELETE FROM ... WHERE ...` | Kaskadierte Löschung über Foreign Keys |
| MongoDB | `db.collection.deleteMany(...)` | Indexierte Löschung nach `email` |
| Qdrant | `DELETE points WHERE payload.email = ...` | Filter-basierte Löschung |
| Prometheus/Loki | Datenablauf via Retention-Konfiguration | Keine gezielte Löschung möglich |
| OTEL | Datenablauf via Span/Label-Expiry | Keine gezielte Löschung |

---

## 4. Ausnahmen von der Löschung (Art. 17 Abs. 3)

Folgende Daten unterliegen **keiner** vorzeitigen Löschung:

| Daten | Grund | Aufbewahrung |
|-------|-------|-------------|
| Rechnungen | § 147 AO / § 257 HGB | 10 Jahre |
| Verträge | § 147 AO / § 257 HGB | 10 Jahre |
| AVV-Dokumentation | Art. 28 DSGVO | 10 Jahre |
| Einwilligungsnachweise | Art. 7 Abs. 1 DSGVO | 3 Jahre nach Widerruf |
| Streitbehaftete Daten | Prozessrisiko | Bis Rechtskraft + 3 Jahre |

### 4.1 Anonymisierung statt Löschung

Bei aufbewahrungspflichtigen Daten werden personenbezogene Felder anonymisiert:

```sql
-- Supabase: Anonymisierung statt Löschung
UPDATE invoices SET 
    customer_email = SHA256(customer_email),  -- Einweg-Hash
    customer_name = '[ANONYMIZED]',
    billing_address = '[ANONYMIZED]'
WHERE status = 'archived' AND customer_email = 'kunde@example.com';
```

---

## 5. Löschregister

Jede Löschung wird dokumentiert:

```json
{
  "loeschung_id": "DEL-20260529-001",
  "datum": "2026-05-29T10:00:00Z",
  "antragsteller": "kunde@example.com",
  "grund": "Art. 17 Abs. 1 lit. a DSGVO — Einwilligung widerrufen",
  "betroffene_systeme": ["supabase", "mongodb", "qdrant"],
  "geloeschte_datensaetze": 47,
  "ausnahmen": ["invoice_2024-001 (Aufbewahrung § 147 AO)"],
  "durchgefuehrt_von": "cleanup-expired-leads (cron)",
  "status": "completed"
}
```

---

## 6. Verantwortlichkeiten

| Rolle | Verantwortung |
|-------|--------------|
| CEO (Pascal Courbois) | Datenschutzrechtliche Gesamtverantwortung |
| NeXifyAI (System) | Automatisierte Löschprozesse, Cron-Jobs |
| Support-Team | Manuelle Löschanträge bearbeiten |
| Security-Agent | Überwachung der Löschfristen |

---

## 7. Technische Umsetzung

### 7.1 Supabase Lösch-Query (Beispiel)

```sql
-- Kaskadierte Löschung eines Kunden
WITH deleted_contact AS (
    DELETE FROM contacts WHERE email = 'kunde@example.com'
    RETURNING id
)
DELETE FROM conversations WHERE contact_id IN (SELECT id FROM deleted_contact);

-- Anonymisierung aufbewahrungspflichtiger Daten
UPDATE invoices SET
    customer_email = encode(sha256(customer_email::bytea), 'hex'),
    customer_name = '[GELÖSCHT]',
    billing_address = '[GELÖSCHT]',
    updated_at = NOW()
WHERE customer_email = 'kunde@example.com';
```

### 7.2 MongoDB Lösch-Query (Beispiel)

```javascript
// Komplette Löschung
db.contacts.deleteOne({ email: 'kunde@example.com' });
db.conversations.deleteMany({ 'participants.email': 'kunde@example.com' });
db.messages.deleteMany({ sender_email: 'kunde@example.com' });

// Anonymisierung
db.invoices.updateMany(
    { customer_email: 'kunde@example.com' },
    { $set: { 
        customer_email: crypto.createHash('sha256').update('kunde@example.com').digest('hex'),
        customer_name: '[GELÖSCHT]'
    }}
);
```

---

## 8. Nachweis der Löschung

Nach erfolgter Löschung erhält der Kunde:

1. **Automatisierte Bestätigungs-E-Mail** mit Lösch-ID (DEL-YYYYMMDD-NNN)
2. **Eintrag im Löschregister** (für Nachweise gegenüber Aufsichtsbehörden)
3. **Status im Kundenportal** (falls Konto vor Löschung existierte)

---

## 9. Verweise

- [Datenschutzerklärung](./datenschutz.md)
- [AVV (Auftragsverarbeitungsvertrag)](./dpa-nexifyai.md)
- [Cookie-Banner](./cookie-banner.md)
- DSGVO Art. 17 — Recht auf Löschung
- DSGVO Art. 21 — Widerspruchsrecht
- § 147 AO — Aufbewahrungspflichten
- TTDSG — Telekommunikation-Telemedien-Datenschutz-Gesetz