# NeXifyAI Platform Operating Model

## Zentrale Architekturentscheidung
NeXifyAI ist EIN zentrales Plattform-System. Nicht mehrere getrennte Projekte.

Die zentrale Plattform ist nexifyai-platform. Darin leben: Agenturseite, Kundenportal, Adminportal, AI-Gateway, Billing, Usage, API-Key-System, Guthabenlogik, Modellverwaltung, Docs-System, AI-Provider-Abstraktion, DeepSeek-kompatible API, Nscale-kompatible API, Token-Metering, Pricing, Support, Auth, Rollen, Kundenrouting, Infrastruktur-Dashboard, KI-Projektabrechnung.

## Provider-Regel
NeXifyAI hostet keine eigenen LLMs lokal. NeXifyAI ist AI-Platform / AI-Service-Layer. Provider: DeepSeek intern, Nscale intern. Kunde sieht nur NeXify API, Modelle, Preise, Rechnungen, Support, Docs. Kunde sieht niemals Provider-Keys.

## 9Router-Regel
9Router ist kritische Core-Infrastruktur. Routing-Layer für LLM-/Embedding-/Provider-Zugriffe. Niemals beschädigen, unkontrolliert refaktorieren, löschen, blockieren oder destabilisieren.

## Guthaben-Regel
Vor jeder AI-Ausführung: Tenant prüfen, API-Key prüfen, Guthaben prüfen, Kosten kalkulieren, Usage loggen, Providerkosten kalkulieren, Marge kalkulieren, Limits prüfen. Kein Guthaben = keine KI-Leistung.

## Einmal zentral, nicht mehrfach

Interne Lösungen werden grundsätzlich einmal zentral gebaut und gepflegt.

**Zentral zu bauen:**
- Kundenportal (ein zentrales)
- Adminportal (ein zentrales)
- Auth-/Rollenmodell (ein zentrales)
- Billing-/Usage-System (ein zentrales)
- API-Key-System (ein zentrales)
- Top-up-System (ein zentrales)
- Docs-System (ein zentrales)
- Designsystem (ein zentrales)
- Event-/Tracking-System (ein zentrales)
- Angebotsgenerator-Pattern (ein zentrales)
- KI-Berater-Pattern (ein zentrales)
- Leadanalyse-Pattern (ein zentrales)
- Monitoring-/Runbook-System (ein zentrales)

**Neue Lösung nur erlaubt, wenn:**
- zentrale Lösung nicht existiert
- bestehende Lösung technisch/rechtlich nicht nutzbar ist
- Erweiterung schlechter wäre als Neubau
- ADR begründet wurde
- Resource-first-Prüfung dokumentiert wurde

## Kundenportal-Regel
Kundenportal ist zentrale Runtime-Oberfläche: Usage, API Keys, Top-up, Billing, Rechnungen, Docs, Pricing, Support, KI-Nutzung, Guthabenlogik, Limits, Tenantsteuerung.
