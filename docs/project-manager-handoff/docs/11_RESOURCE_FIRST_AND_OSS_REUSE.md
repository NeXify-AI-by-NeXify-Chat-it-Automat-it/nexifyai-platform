# Resource-first and OSS Reuse

## Grundsatz

Vor jeder Neuentwicklung wird geprüft, ob eine vorhandene interne Ressource, ein Kundenprojekt-Pattern, eine OSS-Lösung, ein Template oder eine bestehende Komponente genutzt werden kann.

## Reihenfolge

1. Brain und Resource Catalog prüfen.
2. Repo und vorhandene Pakete prüfen.
3. Kundenprojekt-Patterns prüfen.
4. OSS-Lösungen prüfen.
5. shadcn, Next.js und Vercel Templates prüfen.
6. Erst danach Eigenentwicklung begründen.

## Clean Reuse

Kundenprojekt-Code wird nicht kopiert. Er darf als Pattern dienen, wenn keine Kundendaten, keine kundenspezifische Marke und keine nicht freigegebenen Inhalte übernommen werden.

## Ziel

Lösungen werden einmal zentral sauber gebaut, dokumentiert und wiederverwendet.

## Aktuelle OSS-Evaluierung

### Microsoft Webwright (2026-05-25)

| Attribut | Wert |
|----------|------|
| Lizenz | MIT |
| Sprache/Runtime | Python >=3.10, Playwright/Chromium |
| Code-Größe | ~1.5k LoC Core, ~3.7k gesamt |
| CLI | `webwright` (via `pip install webwright`) |
| Modell-Backends | OpenAI, Anthropic, **OpenRouter** (→ 9Router-kompatibel) |
| Goose-Integration | Skill-Plugin existiert für Claude Code/Codex → analog für Goose |
| Status | `planned` — evaluiert, nicht produktiv installiert |

**Geeignet für:** Browser-Evidence-Runner für Agenturseite, Kundenprojekt-Livegang-Checks, Formular-/CTA-/Login-Smoke-Tests, visuelle Evidence.

**Nicht geeignet für:** Brain-Ersatz, Goose-Ersatz, GitHub-API-Ersatz, Project-Manager-Control-Plane-Ersatz, autonomous Scraping ohne Kontrolle, productive Schreibaktionen.

**Nächster Schritt:** Integration als optionales Goose-Tool oder Tool-MCP, wenn Bedarf konkret wird.
