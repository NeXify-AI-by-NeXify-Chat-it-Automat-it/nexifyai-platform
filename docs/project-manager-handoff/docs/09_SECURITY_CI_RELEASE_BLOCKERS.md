# Security and CI Release Blockers

## Ziel

Security- und CI-Probleme dürfen keine Livegänge blockieren. Sie werden priorisiert und mit Evidence abgearbeitet.

## Priorität

P0:
- offene echte Secret-Funde rotieren und schließen
- Critical CodeQL-Funde analysieren
- fehlgeschlagene Release- oder Deploy-Checks klären

P1:
- High CodeQL-Funde triagieren
- Dependabot-Funde gezielt lösen
- Legacy- und Archiv-Pfade klassifizieren

P2:
- Labels, Rulesets, Branch Protection und PR-Templates stabilisieren
- Docs-only Deployments vermeiden
- Legacy-CI deaktivieren oder auf manuell setzen

## Regeln

- Keine geheimen Werte wiederholen.
- Alerts nur mit Nachweis schließen.
- Archive nicht blind fixen, sondern produktiv, legacy oder false-positive mit Evidence klassifizieren.
- Jede CI-Änderung braucht PR und Checks.
