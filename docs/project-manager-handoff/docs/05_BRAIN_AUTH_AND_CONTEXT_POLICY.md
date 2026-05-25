# Brain Auth and Context Policy

## Pflicht

Ohne Brain-Verbindung darf keine Arbeit beginnen.

## Vor jedem Task laden

Pflichtkategorien:

- nexifyai-business-first-priority
- nexifyai-customer-project-delivery
- nexifyai-dos-governance
- nexifyai-runtime-reality
- ai-governance-learning
- prevention-rules
- resource-catalog
- github-security-governance
- nexifyai-clean-reuse-governance

## Nach jedem Task speichern

- task history
- lessons learned, falls relevant
- prevention rule, falls Wiederholungsrisiko
- resource catalog update, falls vorhandene Ressource erkannt
- decision memory, falls Architekturentscheidung getroffen wurde

## Geheimnisse

Keine Secrets im Brain speichern. Nur Namen, Status und redaktierte Pfade dokumentieren.

## Auth

Brain-Zugangsdaten liegen ausschließlich in geschützten Environment-Dateien außerhalb des Repos. Werte werden nie in Logs, Issues, PRs oder Chat-Ausgaben geschrieben.

## Abbruch

Wenn Brain nicht erreichbar ist, darf nur ein Blocker-Report erstellt werden. Keine Implementierung.