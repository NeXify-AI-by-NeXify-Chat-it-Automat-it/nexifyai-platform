# NeXifyAI Projektleiter Masterplan

## Ziel

Der interne NeXify Project Manager ersetzt Pascal operativ in der laufenden Steuerung. Er priorisiert, plant, beauftragt Goose, prüft Goose-Ergebnisse und erzeugt Folgeaufträge bis zur finalen Fertigstellung.

## Aktuelle Priorität

Nicht zuerst gebaut werden: neues Super-Portal, vollständige Agenten-Produktionsstraße, Huginn, Temporal, Tool-MCP und Experten-Agenten als Endausbau.

Zuerst umzusetzen:

1. Agenturseite verkaufsfähig machen.
2. KI-Berater, Angebotsgenerator, Kontaktformular, Mailversand und Leadprozess reparieren.
3. Bestehende Kundenprojekte einzeln nach Pflichtenheften fertigstellen und live bringen.
4. GitHub, CI/CD, Security Alerts, Secrets, Deployments und Runtime-Zustände stabilisieren.
5. Shadow-, Legacy- und halbfertige Artefakte erfassen, migrieren, quarantänisieren oder entfernen.

## Rollen

Project Manager Control Plane: Steuerungs-, Policy-, Queue- und Evidence-Schicht.

Goose: ausführender Worker. Goose plant und setzt nur innerhalb des genehmigten Auftrags um.

Brain: Pflicht-Kontextsystem. Ohne Brain darf keine Arbeit beginnen.

GitHub: Source of Truth. Lokale Repos, Container und Docker-Stacks sind nur Runtime-Indikatoren, nicht automatisch Wahrheit.

## Fertig heißt

Eine Aufgabe gilt nur als fertig, wenn Branch, Commit, PR, Tests/CI, Security-Prüfung, Brain-Update und bei Runtime-Themen ein Laufzeitnachweis vorliegen.
