# NeXifyAI DOS Automated Documentation Policy

**Version:** 1.0 | **Stand:** 2026-05-24
**Klassifikation:** INTERN – VERBINDLICH

---

## Grundsatz

Jede relevante Änderung erzeugt automatisch Dokumentation.
Nicht dokumentierte Änderungen gelten als nicht abgeschlossen.

## Automatische Dokumentationspflichten

| Auslöser | Dokumentation | Ziel |
|----------|--------------|------|
| Jede relevante Änderung | Changelog aktualisieren | DOS_CHANGELOG.md |
| Jede Architekturentscheidung | ADR erzeugen oder aktualisieren | docs/adrs/ |
| Jede neue Ressource | Resource Catalog aktualisieren | machine-readable/reuse-catalog.json |
| Jede wiederverwendbare Fähigkeit | Reusable Capabilities aktualisieren | learning/reusable-capabilities.json |
| Jede Serviceänderung | Service Catalog aktualisieren | understanding/service-catalog.json |
| Jede Kundenprojekt-Erkenntnis | Customer Project Reuse Map aktualisieren | machine-readable/customer-project-reuse-map.json |
| Jede neue Prevention Rule | Prevention Rules + Brain | learning/prevention-rules.json + Brain |
| Jede neue Erkenntnis | DOS + Learning + Resource + Reuse | Siehe DOS_UPDATE_POLICY.md |

## Regeln

1. Jede relevante Änderung aktualisiert Changelog
2. Jede Architekturentscheidung erzeugt ADR
3. Jede neue Ressource aktualisiert Resource Catalog
4. Jede wiederverwendbare Fähigkeit aktualisiert Reusable Capabilities
5. Jede Serviceänderung aktualisiert Service Catalog
6. Jede Kundenprojekt-Erkenntnis aktualisiert Customer Project Reuse Map
7. Jede neue Prevention Rule wird ins Brain geschrieben
8. Jede nicht dokumentierte Änderung gilt als nicht abgeschlossen

## Automatisierung

Dokumentation soll möglichst automatisiert erfolgen:
- Goose schreibt beim Abschluss einer Änderung automatisch in Changelog
- Goose prüft bei jeder neuen Erkenntnis, ob DOS/Learning/Resource aktualisiert werden muss
- Brain-Einträge werden bei relevanten Änderungen automatisch erstellt
- Reuse Catalog wird bei neuen wiederverwendbaren Artefakten automatisch erweitert

## Verantwortlich

- Jeder Entwickler/Agent
- Prüfung bei jedem Task-Abschluss
- Keine Fertigmeldung ohne Dokumentations-Check
