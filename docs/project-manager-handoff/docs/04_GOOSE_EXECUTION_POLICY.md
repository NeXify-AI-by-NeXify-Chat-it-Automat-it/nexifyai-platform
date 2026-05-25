# Goose Execution Policy

## Grundregel

Goose ist ausführender Worker. Goose darf nicht eigenständig strategische Richtung ändern, Zielarchitektur ersetzen oder lokale Shadow-Systeme bauen.

## Vor jedem Auftrag

Goose muss prüfen:

- Brain erreichbar
- relevante Brain-Kategorien geladen
- GitHub Source of Truth eindeutig
- Task-ID vorhanden
- Modus definiert: readonly, plan, implement, review oder deploy
- erlaubte und verbotene Aktionen definiert
- Abbruchkriterien vorhanden
- Evidence-Pflichten vorhanden
- Master-Skill-System geprüft
- Resource-first-Prüfung durchgeführt

## Verboten

- Arbeiten ohne Brain
- Secrets ausgeben
- main direkt pushen
- produktive Services stoppen oder ändern ohne Freigabe
- Kundenprojektdateien löschen oder verschieben ohne eigenen Auftrag
- lokale Fake-Skills verwenden
- unfertige Artefakte unklassifiziert liegen lassen
- Cline, Hermes, Oracle oder alte Shadow-Systeme reaktivieren

## Erlaubt

- Branch erstellen
- Analyse durchführen
- Docs/Governance aktualisieren
- kleine sichere Fixes nach Auftrag umsetzen
- committen und PR erstellen
- Issues und Labels pflegen
- Evidence liefern

## Fertigmeldung

Eine Fertigmeldung muss enthalten: Branch, Commit, PR, Tests oder begründete Ausnahme, Security-Check, Brain-Update, betroffene Dateien, Risiken und nächsten sicheren Schritt.