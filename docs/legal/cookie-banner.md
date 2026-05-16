# Cookie-Banner (Deployment-Text)

## Banner-Titel
🍪 Cookie-Einstellungen

## Einleitungstext
Diese Website verwendet Cookies und ähnliche Technologien, um die Nutzererfahrung zu
verbessern, die Website-Funktionalität sicherzustellen und die Nutzung der Website zu
analysieren. Einige Cookies sind technisch notwendig, andere helfen uns, unser Angebot
zu verbessern. Sie können Ihre Einwilligung jederzeit mit Wirkung für die Zukunft
widerrufen. Weitere Informationen finden Sie in unserer Datenschutzerklärung.

## Cookie-Kategorien

### Notwendige Cookies (immer aktiv)
Diese Cookies sind für den technischen Betrieb der Website erforderlich und können
nicht deaktiviert werden.
- Session-Cookie: Speichert Ihre Sitzung (läuft mit Schließen des Browsers ab)
- Cookie-Einstellungen: Speichert Ihre Cookie-Präferenzen (1 Jahr)
- CSRF-Token: Schützt vor Cross-Site-Request-Forgery (Session)

### Analyse-Cookies (opt-in)
Diese Cookies helfen uns zu verstehen, wie Besucher mit der Website interagieren.
- Seitenaufrufe und Verweildauer
- Anonymisierte Nutzungsstatistiken
- Keine Weitergabe an Dritte für Werbezwecke

### Marketing-Cookies (opt-in)
Derzeit nicht verwendet. Sollten wir Marketing-Cookies einsetzen, informieren wir Sie
vorab und holen Ihre Einwilligung ein.

## Button-Texte
- **"Alle akzeptieren"** — Akzeptiert alle Cookie-Kategorien
- **"Nur notwendige"** — Akzeptiert nur technisch notwendige Cookies
- **"Einstellungen"** — Öffnet die detaillierte Auswahl

## Footer-Text
Weitere Informationen finden Sie in unserer
[Datenschutzerklärung](/datenschutz) und unserem [Impressum](/impressum).

## Technische Umsetzung (Hinweise für Entwickler)
- Cookie-Präferenzen im localStorage speichern (Schlüssel: `cookieConsent`)
- Banner wird beim ersten Besuch eingeblendet
- Bei "Nur notwendige" / vor Auswahl: KEINE Analyse-Skripte laden
- Re-Consent: Banner alle 12 Monate erneut anzeigen
- DSGVO-konform: Keine Cookies vor Einwilligung setzen (außer notwendige)

## Beispiel localStorage-Objekt
```json
{
  "cookieConsent": {
    "necessary": true,
    "analytics": false,
    "marketing": false,
    "timestamp": "2026-05-15T09:30:00Z",
    "version": 1
  }
}
```
