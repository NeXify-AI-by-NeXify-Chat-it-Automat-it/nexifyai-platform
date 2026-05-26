# Playwright MCP Evidence Runner

## Zweck

Playwright MCP dient als Browser-Evidence-Runner für:
- UI-Audits von Agenturseite und Kundenportal
- Screenshot-Evidence für Deployment-Verifikation
- Smoke Tests der GitHub UI nach Config-Änderungen
- Accessibilitäts-Audits

## Sicherheitsrichtlinie

| Regel | Begründung |
|:------|:-----------|
| `--headless` immer | Kein sichtbarer Browser nötig |
| `--sandbox` immer | Browser-Sandbox gegen Escape |
| `--isolated` immer | Keine Disk-Persistenz von Sessions |
| KEINE `--secrets` Datei | Keine Login-Secrets an Playwright |
| KEIN `--no-sandbox` | Sicherheitsrisiko |
| `--blocked-origins` | Blocke externe Tracking-Domains |

## Konfiguration

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--sandbox",
        "--isolated",
        "--blocked-origins",
        "doubleclick.net;google-analytics.com;facebook.com"
      ]
    }
  }
}
```

## Alternativ: Playwright CLI + Skills

Laut Playwright-Dokumentation ist CLI + SKILLS token-effizienter als MCP für Coding Agents. Für NeXify:
- **MCP** für dedizierte Browser-Evidence-Runner (autonome Workflows)
- **CLI** für Goose-Worker-internes Browser-Testing

## Verbotene Aktionen

- KEIN Form-Submit mit echten Credentials
- KEIN Login in Kundenportale
- KEINE Session-Persistenz
- KEINE Screenshots mit Secrets im Viewport

## Erlaubte Aktionen

- Screenshot von öffentlichen Seiten
- Accessibility Tree Scans
- HTML-Struktur-Analyse
- Console-Log-Prüfung
- Performance-Audits
