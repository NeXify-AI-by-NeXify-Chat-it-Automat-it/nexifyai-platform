# Abnahme und Evidence Gate

## Ziel

Jede Aufgabe wird erst abgenommen, wenn Ergebnis und Nachweise vollständig sind.

## Mindestnachweise

- Ziel erfüllt
- Scope eingehalten
- keine verbotenen Aktionen
- geänderte Dateien dokumentiert
- Tests oder begründete Ausnahme
- CI-Status
- Security-Prüfung
- Brain-Update
- offene Risiken
- Rollback-Hinweis, falls Runtime betroffen ist

## Ablehnungskriterien

- keine Task-ID
- kein Brain-Kontext
- kein Branch oder Commit bei Änderungen
- keine Security-Prüfung
- unklare Runtime-Annahmen
- unfertige Artefakte ohne Status
- vertrauliche Werte im Output
- Kundenprojektänderung ohne Kundenprojektauftrag

## Ergebnisstatus

- accepted
- needs_fix
- blocked
- rejected

Der Project Manager darf Goose-Ergebnisse nur akzeptieren, wenn alle Pflichtnachweise vorliegen.
