# Einwilligungsverwaltung (DSGVO Art. 7)

**Stand:** 2026-05-30
**Verantwortlich:** NeXifyAI / Pascal Courbois

## 1. Einwilligungsarten

| Typ | Speicherort | Widerruf | Loeschfrist |
|-----|-------------|----------|-------------|
| Cookie-Consent | LocalStorage/Cookie | Cookie-Banner | 26 Monate |
| Marketing-E-Mail | customer_consents (MongoDB) | Opt-Out-Link / Portal | 3 Jahre nach Widerruf |
| KI-Analyse | customer_consents (MongoDB) | Portal-Einstellungen | 3 Jahre nach Widerruf |
| Datenweitergabe | customer_consents (MongoDB) | E-Mail an Support | 3 Jahre nach Widerruf |

## 2. Nachweispflicht (Art. 7 Abs. 1)

Jede Einwilligung wird dokumentiert:
- **Zeitpunkt** der Einwilligung
- **Text** der Einwilligungserklaerung
- **Methode** (Double-Opt-In, Checkbox, Cookie-Banner)
- **IP-Adresse** (anonymisiert)

## 3. Widerrufsprozess

1. Kunde widerruft via Portal, E-Mail oder Opt-Out-Link
2. System setzt Consent auf "revoked" + speichert Widerrufszeitpunkt
3. Bestaetigungs-E-Mail wird gesendet
4. Verarbeitung wird innerhalb von 30 Tagen eingestellt
5. Nachweis im Audit-Log

## 4. Verweise
- [Cookie-Banner](./cookie-banner.md)
- [Datenschutzerklaerung](./datenschutzerklaerung.md)
- [Betroffenenrechte](./betroffenenrechte.md)
- [Loeschkonzept](./loeschkonzept.md)