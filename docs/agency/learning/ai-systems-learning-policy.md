# NeXifyAI Systems Learning Policy

## Geltungsbereich
Diese Policy gilt für alle AI-Lösungen im NeXifyAI-System: Goose manuell, Goose 24/7 Worker, NeXify AI Projektleiter GPT, Brain API, Skill-Bridge, MCP-Systeme, Projektmanager-API, alle AI-gestützten Plattformfunktionen.

## Pflichten
1. Alle AI-Lösungen lernen aus Brain (vorher Kontext abrufen, nachher Erkenntnisse speichern)
2. Alle AI-Lösungen schreiben validierte Erkenntnisse ins Brain
3. Jede relevante Änderung erzeugt Lessons Learned
4. Fehler werden als Prevention Rules gespeichert
5. Vorhandene Ressourcen werden zuerst geprüft (Resource-first)
6. Keine neue Lösung ohne Resource-Reuse-Check
7. Keine lokalen Erfindungen, wenn Systemressourcen existieren
8. Keine Secrets speichern oder ausgeben

## Memory-Typen
- Semantisches Gedächtnis: Fakten, Architektur, Regeln
- Episodisches Gedächtnis: Ereignisse, Incidents, Entscheidungen
- Prozedurales Gedächtnis: Workflows, Recovery, Vorgehensweisen
- Governance Memory: Policies, Compliance, Standards
- Prevention Memory: Fehler-Präventionsregeln, Lessons Learned

## Meta-Regel: Neue Erkenntnisse sind Pflichtabgleich

Neue Erkenntnisse sind keine Chatnotizen.
Jede neue Erkenntnis aus:
- Goose-Ausgaben
- User-Korrekturen
- Audits
- Runtime-Checks
- Security-Funden
- Kundenprojekten
- Repo-Analysen
- Vercel-/GitHub-/CI-Ergebnissen
- Brain-Abfragen
- Deployment-Fehlern
- Architekturentscheidungen
- wiederverwendbaren Artefakten
- bestehenden Kundenprojektlösungen

muss geprüft und übertragen werden in:
1. DOS, falls Regel/Standard/Prozess betroffen ist
2. Lessons Learned, falls Fehler/Erkenntnis entstanden ist
3. Prevention Rules, falls Wiederholungsfehler verhindert werden muss
4. Resource Catalog, falls vorhandene Ressource nutzbar ist
5. Reusable Capabilities, falls etwas wiederverwendet werden kann
6. Service Catalog, falls Service/System betroffen ist
7. ADR, falls Architekturentscheidung betroffen ist
8. Brain, falls agentenübergreifendes Wissen relevant ist

**Neue Erkenntnis ohne Governance-/Learning-/Resource-Abgleich gilt als nicht verarbeitet.**

## Task-Gate (vor jeder Aufgabe)
1. Brain-Kontext abrufen
2. Lessons Learned abrufen
3. Prevention Rules prüfen
4. Resource Catalog prüfen
5. Reuse Catalog prüfen
6. Master-Skill-Registry prüfen
7. DOS-Anwendbarkeit prüfen
8. Entscheidung: vorhandene Ressource nutzen/erweitern/kombinieren ODER neue Lösung planen
9. Entscheidung dokumentieren
10. DOS-/Learning-/Reuse-Update-Pflicht prüfen
