# WCAG 2.2 AA Compliance Assessment

**Stand:** 2026-05-30
**Verantwortlich:** NeXifyAI Design Lead / Pascal Courbois
**Standard:** WCAG 2.2 Level AA (Web Content Accessibility Guidelines)

---

## 1. Geltungsbereich

Geprueft werden folgende Frontend-Komponenten:
- Admin Cockpit (AdminCockpit.jsx)
- Admin Dashboard (Admin.jsx)
- Customer Portal (CustomerPortal.jsx)
- Quote Portal (QuotePortal.jsx)
- Booking Page (BookingPage.jsx)
- Pricing Page (PreisePage.jsx)
- Services Page (LeistungenPage.jsx)

## 2. Conformance-Statement

NeXifyAI strebt WCAG 2.2 Level AA-Konformitaet an.
**Aktueller Stand:** Teilweise konform (Stand 30.05.2026)

## 3. Kritische Luecken (P0)

| # | Kriterium | Problem | Fix-Vorschlag |
|---|-----------|---------|--------------|
| C1 | 2.4.1 | Skip-to-Content-Link fehlt | Skip-Link als erstes fokussierbares Element |
| C2 | 2.4.7 / 2.4.13 | Fokus-Indikator unsichtbar | `:focus-visible { outline: 2px solid #FE9B7B; }` |
| C3 | 2.1.1 | Tabellenzeilen nicht tastaturbedienbar | tabindex + onKeyDown auf Zeilen |
| C4 | 3.3.1 / 3.3.3 | Keine inline-Fehlermeldungen | aria-describedby + role=alert |
| C5 | 4.1.3 | Keine ARIA-Live-Regionen | aria-live=polite auf Chat |
| C6 | 2.5.8 | Icons unter 24px Zielgroesse | Sidebar-Icons auf 24x24 |
| C7 | 1.4.3 | text-muted Kontrast 3.2:1 < 4.5:1 | Farbe aufhellen |
| C8 | 1.4.10 | Fixed-Sidebar bei 320px | Mobile: Overlay statt Fixed |

## 4. Status nach Kategorie

| Kategorie | A geprueft | AA geprueft | Critical |
|-----------|-----------|-------------|----------|
| Wahrnehmbar | 7 | 6 | 2 |
| Bedienbar | 8 | 6 | 4 |
| Verstaendlich | 6 | 3 | 2 |
| Robust | 3 | 1 | 0 |
| **Gesamt** | **24** | **16** | **8** |

## 5. Erfuellte Kriterien (Auswahl)

- 1.1.1 Nicht-Text-Inhalt: alt-Texte auf Bildern (AdminCockpit.jsx, Admin.jsx, CustomerPortal.jsx)
- 1.3.1 Semantische Struktur: role-Attribute (navigation, menubar, listitem)
- 2.4.2 Seiten-Titel: H1 auf allen Seiten
- 3.1.1 Sprache: lang=de in index.html
- 3.3.7 Zug. Authentifizierung: Magic Link statt Passwort
- 4.1.1 Parsen: Valides HTML

## 6. Verweise

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Design Guidelines: /design_guidelines.json
- tokens.css: /packages/ui/tokens.css