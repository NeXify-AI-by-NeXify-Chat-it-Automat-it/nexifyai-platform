# Goose Prompt: Agenturseite Fix nach Audit

AUFGABE: Agenturseite gezielt reparieren nach abgeschlossenem Read-only Audit.

MODUS: Implementierung nur auf Branch. Keine produktiven Services direkt ändern. Keine vertraulichen Werte ausgeben.

## Voraussetzungen

- Business Reality Audit liegt vor.
- P0/P1-Liste liegt vor.
- Brain wurde geladen.
- Zielrepo und Branch sind eindeutig.

## Ziel

Die Agenturseite wird verkaufsfähig und funktionsfähig. Priorität haben Kontaktstrecke, Angebotsstrecke, Branding, Leadprozess und Deployment-Fähigkeit.

## Vorgehen

1. Branch erstellen.
2. Relevante Dateien lesen.
3. Minimalen Fixplan erstellen.
4. Nur freigegebene P0/P1-Fixes umsetzen.
5. Tests, Build und Security-Check ausführen.
6. PR erstellen.
7. Brain aktualisieren.

## Report

Berichte Branch, Commit, PR, Tests, CI, Security, offene Blocker und nächsten sicheren Schritt.
