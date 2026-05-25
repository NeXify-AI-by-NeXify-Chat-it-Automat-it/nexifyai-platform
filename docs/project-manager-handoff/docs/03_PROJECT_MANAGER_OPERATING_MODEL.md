# Project Manager Operating Model

## Zweck

Die interne NeXify Project Manager Control Plane übernimmt die operative Steuerung. Sie erzeugt Aufgaben, beauftragt Goose, prüft Ergebnisse, dokumentiert Evidence und erzeugt Folgeaufträge.

## Verantwortlichkeiten

Project Manager Control Plane:
- nimmt manuelle, GitHub-, Vercel-, Supabase- und spätere Webhook-Ereignisse entgegen
- erzeugt Task-IDs
- lädt Brain-Kontext
- prüft Policy Gates
- priorisiert P0 bis P3
- triggert Goose kontrolliert
- bewertet Goose-Ergebnisse
- erzeugt Folgeaufträge
- schreibt Brain-, DOS-, Learning- und GitHub-Updates

Goose:
- führt nur validierte Aufgaben aus
- arbeitet auf Branches
- liefert Evidence
- meldet Blocker statt zu improvisieren

## Ablauf

1. Event oder Auftrag kommt an.
2. Project Manager lädt Brain-Kontext.
3. Task wird klassifiziert.
4. Policy Gate entscheidet, ob Ausführung erlaubt ist.
5. Goose erhält einen präzisen Auftrag.
6. Goose liefert Ergebnis mit Evidence.
7. Project Manager validiert.
8. Nächster Auftrag entsteht oder Task wird abgeschlossen.

## Grundsatz

Der Project Manager ersetzt Pascal in der operativen Taktung, aber nicht die Governance-Regeln. Jede Ausführung bleibt nachvollziehbar und sicher.