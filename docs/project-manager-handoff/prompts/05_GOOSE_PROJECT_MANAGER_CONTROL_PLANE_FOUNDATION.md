# Goose Prompt: Project Manager Control Plane Foundation

AUFGABE: Interne NeXify Project Manager Control Plane vorbereiten.

MODUS: Erst Analyse, dann sichere Minimalstruktur. Keine Produktivänderung ohne Freigabe.

## Ziel

Eine interne Steuerungsschicht soll Goose kontrolliert beauftragen, Brain-Kontext erzwingen, Aufgaben registrieren, Evidence prüfen und Folgeaufträge erzeugen.

## Vorarbeit

- bestehende Worker- und Zwischenstands-Artefakte inventarisieren
- unfertige Strukturen klassifizieren
- nichts halb gebaut liegen lassen
- manuelle Goose CLI darf nicht beschädigt werden

## Minimalstruktur

- Health-Endpunkt
- Task Registry
- Policy Gate
- Brain Client
- Goose Controller
- Evidence Store
- redaktierte Logs
- Runbook und Failure Handling

## Abnahme

- Read-only Testtask erfolgreich
- Brain-Kontext geladen
- Ergebnis gespeichert
- keine vertraulichen Werte in Logs
- manueller Goose CLI weiter nutzbar
- Branch, Commit und PR erstellt
