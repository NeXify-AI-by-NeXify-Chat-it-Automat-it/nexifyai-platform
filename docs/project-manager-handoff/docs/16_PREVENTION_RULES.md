# Prevention Rules

## Stop-Regeln

Goose oder die Project Manager Control Plane müssen stoppen, wenn:

- Brain nicht erreichbar ist.
- GitHub Source of Truth unklar ist.
- der Zielmodus nicht definiert ist.
- vertrauliche Werte im Auftrag oder Output sichtbar würden.
- produktive Services betroffen sind und keine Freigabe vorliegt.
- Kundenprojektdateien verändert würden, ohne eigenen Kundenprojektauftrag.
- Runtime-Zustand nur vermutet, aber nicht belegt ist.
- ein Artefakt angelegt wurde und kein Status vergeben wurde.

## Ressourcen-Lebenszyklus

Jede erzeugte Ressource braucht einen Status:

- active_managed
- planned
- migrated
- quarantined
- removed_with_evidence
- blocked

Unklassifizierte Artefakte sind ein Fehler.

## Wiederverwendung

Vor Neubau immer prüfen:

- bestehendes Repo
- Brain
- Resource Catalog
- Kundenprojekt-Pattern
- OSS-Lösung
- Template
- vorhandene Infrastruktur

## Fertigstellung

Keine Aufgabe gilt als fertig ohne Evidence und Brain-Update.
