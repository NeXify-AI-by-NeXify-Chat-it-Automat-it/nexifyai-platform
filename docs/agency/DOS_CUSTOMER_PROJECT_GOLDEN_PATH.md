# NeXifyAI DOS Customer Project Golden Path

## Prinzip
Kundenprojekte werden nach denselben Standards gebaut wie interne Systeme.

## Jedes Kundenprojekt erhält
- eigenes Repo
- eigene Deployment-/VDS-/Vercel-Struktur
- eigene Secrets
- eigene Datenbank
- eigene CI/CD
- keine Vermischung mit Core
- definierte Schnittstellen zum zentralen Kundenportal
- KI-Nutzung über Guthabenlogik und NeXify API Keys
- kein Provider-Key beim Kunden

## Kundenprojekt-Wiederverwendung nur als Clean Pattern

Kundenprojekte dürfen nicht im Core leben.
Sie dürfen aber als Erkenntnis-/Pattern-/Blueprint-Quelle dienen.

**Erlaubt:**
- Architekturpattern übernehmen
- UI-/UX-Pattern abstrahieren
- generische Komponenten neu sauber aufbauen
- Workflows nachbauen
- Lessons Learned speichern
- wiederverwendbare Anforderungen ableiten

**Nicht erlaubt:**
- Kundendaten übernehmen
- Secrets übernehmen
- kundenspezifische Texte/Marke ungeprüft übernehmen
- Kundenrepo in Core kopieren
- Kundenprojekt als Core-Modul betreiben
- unklare Lizenz-/Eigentumsverhältnisse ignorieren

## Pfad
1. Discovery: Kunde, Ziel, Leistungsbereich, Anforderungen, Erfolgskriterien, Risiken, Budget, Betrieb
2. Konzept: Zielgruppe, Nutzenversprechen, Seitenstruktur, UX-Flows, Content, Angebot
3. Architektur: Next.js/React/Supabase/Vercel, Datenmodell, Auth, Rollen, API, Hosting, Monitoring, Security
4. Design/Text: CI, UI-Komponenten, Copy, Conversion, Barrierefreiheit, SEO, Rechtliches
5. Umsetzung: eigenes Repo, CI/CD, Env/Secrets, Deployment-Partition, keine Core-Vermischung
6. KI-Integration: zentrale Kundenportal-Anbindung, Guthabenpflicht, Usage Tracking, API-Keys
7. QA/Security: Tests, Build, Security, RLS, Datenschutz, Performance, Accessibility, Evidence
8. Übergabe/Betrieb: Dokumentation, Monitoring, Wartungsplan, Backup/Recovery, Support
9. Reuse-Abgleich: Wiederverwendbare Artefakte/Patterns aus dem Projekt erfassen und in Reuse Catalog eintragen
