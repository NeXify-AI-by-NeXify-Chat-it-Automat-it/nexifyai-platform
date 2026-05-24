# NeXifyAI DOS Resource First

## Prüfreihenfolge vor jeder neuen Lösung
1. Gibt es eine Brain-Funktion?
2. Gibt es ein Goose-Tool?
3. Gibt es eine Master-Repo-Komponente (Skill/Agent/Hook/MCP)?
4. Gibt es bestehende Infrastruktur (9Router, Traefik, Cloudflare, Supabase, Vercel, GitHub Actions)?
5. Gibt es Code im nexifyai-platform Repo?
6. Gibt es ein bestehendes Pattern?
7. Gibt es Dokumentation oder ADRs?
8. Kann eine vorhandene Ressource kombiniert oder erweitert werden?
9. Gibt es einen Eintrag im Reuse Catalog?
10. Brauchen wir wirklich etwas Neues?

## Entscheidung
Wenn vorhandene Ressourcen nutzbar sind: verwenden, verbinden, feinabstimmen.
Nicht: neubauen, duplizieren, lokal nachmodellieren, Shadow-System erzeugen.

## Zentrale Regel: Einmal zentral, nicht mehrfach

Interne Lösungen werden grundsätzlich **einmal zentral** gebaut und gepflegt.

### Beispiele für zentrale Lösungen
- ein zentrales Kundenportal
- ein zentrales Adminportal
- ein zentrales Auth-/Rollenmodell
- ein zentrales Billing-/Usage-System
- ein zentrales API-Key-System
- ein zentrales Top-up-System
- ein zentrales Docs-System
- ein zentrales Designsystem
- ein zentrales Event-/Tracking-System
- ein zentrales Angebotsgenerator-Pattern
- ein zentrales KI-Berater-Pattern
- ein zentrales Leadanalyse-Pattern
- ein zentrales Monitoring-/Runbook-System

### Neue Lösung nur erlaubt, wenn
1. Zentrale Lösung nicht existiert
2. Bestehende Lösung technisch/rechtlich nicht nutzbar ist
3. Erweiterung schlechter wäre als Neubau
4. ADR begründet wurde
5. Resource-first-Prüfung dokumentiert wurde

## Pflicht: Reuse Catalog vor jeder neuen Lösung prüfen
Vor jeder neuen Implementierung muss der Reuse Catalog (docs/agency/machine-readable/reuse-catalog.json) geprüft werden.
Fund aus Reuse Catalog = vorhandene Lösung nutzen, nicht neu bauen.

## Erweiterung
Erweitere DOS bei:
- neue Systemressource
- neues externes System
- neuer Service
- neuer Workflow
- neues Portal/Interface
- neue Architekturentscheidung
- neues Tool/Skill/MCP
- neues Kundenprojekt-Artefakt (generalisiert)
- neue Erkenntnis, die DOS betrifft

## Kategorien
- Core: Brain, Qdrant, 9Router, Traefik, Cloudflare, Redis, Supabase, Vercel, GitHub
- Skills: claude-code-templates, Bridge, Registry
- Tools: Goose-Tools, MCPs, GitHub Actions
- System: Portale, Services, APIs, Workflows
