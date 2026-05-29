# Betroffenenrechte-Verfahren (DSGVO Art. 15–22)

**Stand:** 2026-05-30
**Verantwortlich:** NeXifyAI / Pascal Courbois

---

## 1. Übersicht

| Recht | Artikel | Prozess | Frist |
|-------|---------|---------|-------|
| **Auskunft** | Art. 15 | E-Mail an support@nexify-automate.com → Identitätsprüfung → Datenexport | 30 Tage |
| **Berichtigung** | Art. 16 | E-Mail oder Portal → Korrektur in DB | Unverzüglich |
| **Löschung** | Art. 17 | Siehe Löschkonzept | 30 Tage |
| **Einschränkung** | Art. 18 | Account-Suspendierung | 24h |
| **Datenportabilität** | Art. 20 | Export als JSON/CSV | 30 Tage |
| **Widerspruch** | Art. 21 | Opt-Out-Mechanismus (Portal) | Sofort |

---

## 2. Auskunftsverfahren (Art. 15)

### 2.1 Antragstellung
1. Kunde sendet E-Mail an support@nexify-automate.com mit Betreff "Auskunft Art. 15"
2. Alternativ: Formular im Kundenportal
3. Keine bestimmte Form erforderlich

### 2.2 Identitätsprüfung
1. E-Mail-Adresse muss mit hinterlegter Kontakt-E-Mail übereinstimmen
2. Bei Unsicherheit: Zusätzliche Verifikation (Video-Ident)
3. Bei unzureichender Identität: Ablehnung mit Aufforderung zur Nachbesserung

### 2.3 Datenzusammenstellung
```sql
-- Supabase: Kundendaten exportieren
SELECT * FROM contacts WHERE email = 'kunde@example.com';
SELECT * FROM customer_accounts WHERE email = 'kunde@example.com';
```

```javascript
// MongoDB: Business-Daten exportieren
db.leads.find({email: 'kunde@example.com'});
db.conversations.find({'participants.email': 'kunde@example.com'});
db.quotes.find({'customer.email': 'kunde@example.com'});
db.invoices.find({'customer.email': 'kunde@example.com'});
db.support_tickets.find({customer_email: 'kunde@example.com'});
```

### 2.4 Antwortformat
- Maschinenlesbar (JSON) + menschenlesbar (PDF)
- Enthält: Verarbeitungszweck, Datenkategorien, Empfänger, Speicherdauer
- Versand per E-Mail (verschlüsselt auf Wunsch)

### 2.5 Ausnahmen
- Bei Gefährdung der Rechte anderer Personen
- Bei Geschäftsgeheimnissen
- Bei offensichtlich unbegründeten Anträgen (Art. 12 Abs. 5)

---

## 3. Berichtigungsverfahren (Art. 16)

1. **Self-Service:** Kunde kann Profildaten im Portal selbst korrigieren
2. **Admin-Support:** Bei Fehlern in Vertragsdaten → E-Mail an support
3. **Automatisiert:** Chat-Adressen werden bei erkannten Änderungen aktualisiert
4. **Bestätigung:** Bestätigungs-E-Mail nach Berichtigung

---

## 4. Löschungsverfahren (Art. 17)

Siehe [Löschkonzept](./loeschkonzept.md)

### 4.1 Technische Umsetzung
```sql
-- Supabase: Löschung
DELETE FROM contacts WHERE email = 'kunde@example.com';
-- Anonymisierung für aufbewahrungspflichtige Daten
UPDATE invoices SET customer_email = SHA256(customer_email) WHERE customer_email = 'kunde@example.com';
```

```javascript
// MongoDB: Löschung
db.contacts.deleteOne({email: 'kunde@example.com'});
db.conversations.deleteMany({'participants.email': 'kunde@example.com'});
```

### 4.2 Löschbestätigung
- Automatisierte E-Mail mit Lösch-ID (DEL-YYYYMMDD-NNN)
- Dokumentation im Löschregister

---

## 5. Einschränkungsverfahren (Art. 18)

1. Kunde beantragt Einschränkung per E-Mail
2. Account wird auf "restricted" gesetzt:
   - Keine neuen Transaktionen
   - Bestehende Daten bleiben erhalten
   - Keine Löschung während Prüfung
3. Aufhebung der Einschränkung nach Abschluss der Prüfung

---

## 6. Datenportabilitätsverfahren (Art. 20)

1. Kunde beantragt Export per E-Mail oder Portal
2. Daten werden zusammengestellt (siehe 2.3)
3. Export erfolgt als:
   - **JSON:** Für technische Nutzer (strukturiert, API-kompatibel)
   - **CSV:** Für Business-Analyse (tabellarisch)
4. Versand als ZIP-Datei per E-Mail
5. Frist: 30 Tage, maximal 3 Exporte pro Jahr

---

## 7. Widerspruchsverfahren (Art. 21)

### 7.1 Direktwerbung (Art. 21 Abs. 2)
- Opt-Out-Link in jeder E-Mail
- Portal: Einstellungen → Benachrichtigungen
- **Widerspruch wird sofort wirksam**

### 7.2 Profiling / Berechtigtes Interesse (Art. 21 Abs. 1)
- Kunde legt Widerspruch ein
- Prüfung: Überwiegt das berechtigte Interesse?
- Dokumentation der Abwägung
- Bei Ablehnung: Rechtsmittelbelehrung

---

## 8. Automatisierte Entscheidungen (Art. 22)

| Verarbeitung | Automatisiert? | Human-in-the-Loop? |
|-------------|---------------|-------------------|
| Lead-Scoring | Ja (KI) | Admin-Kontrolle |
| Angebotserstellung | Ja (KI) | Admin-Review |
| Kredit-/Bonitätsprüfung | Nein | — |
| Outreach-Entscheidung | Ja (KI) + Legal Gate | Admin-Eskalation |

Auf Wunsch des Kunden: Manuelle Prüfung durch Admin.

---

## 9. Verantwortlichkeiten

| Rolle | Verantwortung |
|-------|--------------|
| CEO (Pascal Courbois) | Gesamtverantwortung, Entscheidung bei Widerspruch |
| Support-Team | Bearbeitung von Anträgen (Auskunft, Löschung, Berichtigung) |
| NeXifyAI (System) | Automatisierte Prozesse (Opt-Out, Export, Lösch-Cron) |
| Datenschutzbeauftragter | (Noch nicht benannt — bei Bedarf extern bestellbar) |

---

## 10. Verweise

- [Löschkonzept (Art. 17)](./loeschkonzept.md)
- [DSFA (Art. 35)](./dsfa.md)
- [VVT (Art. 30)](./vvt.md)
- [Datenschutzerklärung](./datenschutzerklaerung.md)
- [AVV/DPA](./dpa-nexifyai.md)
- [Cookie-Banner](./cookie-banner.md)