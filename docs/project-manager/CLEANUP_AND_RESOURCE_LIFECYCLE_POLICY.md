# Cleanup and Resource Lifecycle Policy

**Version:** 1.0  
**Stand:** 2026-05-25  
**Status:** active_managed  
**Owner:** Project Manager

---

## Grundsatz

Keine durch Goose, ChatGPT oder Project Manager erzeugte Ressource darf halb gebaut oder unklassifiziert liegen bleiben.

## Ziel

- Vollständige Transparenz über alle Artefakte
- Klare Statuszuweisung für jede Ressource
- Keine technischen Schulden durch vergessene Experimente
- Nachvollziehbare Entscheidungen

## Status-Definitionen

| Status | Bedeutung | Maximale Dauer |
|--------|-----------|----------------|
| `active_managed` | Aktiv genutzt, dokumentiert, gemonitort | Unbegrenzt |
| `planned` | Geplant, noch nicht implementiert | 90 Tage |
| `migrated` | Migriert, alte Version deprecated | 30 Tage |
| `quarantined` | Isoliert, nicht aktiv, nicht gelöscht | 180 Tage |
| `removed_with_evidence` | Gelöscht, Evidence archiviert | Permanent |
| `blocked` | Kann nicht fortgesetzt werden | 30 Tage |

## Pflicht-Regeln

### 1. Sofortige Klassifizierung

Jede neue Ressource muss innerhalb von 24 Stunden klassifiziert werden:
- Status festlegen
- Owner zuweisen
- Manifest erstellen oder aktualisieren
- Resource Catalog aktualisieren

### 2. Temporäre Dateien

Erlaubte Naming-Patterns:
- `TEMP_*` (max 24h)
- `TEST_*` (max 7d)
- `DEBUG_*` (max 1h)
- `WIP_*` (max 7d)

Nach Ablauf:
- Klassifizieren (active, remove, quarantine)
- Nicht liegen lassen

### 3. Unfertige Implementierungen

Verboten:
- Code ohne Status
- Features ohne Tests
- Docs ohne Review
- Branches ohne PR (>7d)

Pflicht:
- Feature Branch mit WIP Label
- Issue mit Fortschritt
- PR Draft mit Plan
- Review-Termin

### 4. Deprecated Ressourcen

Verboten:
- Stille Deprecation
- Keine Notice
- Keine Migration

Pflicht:
- Deprecation Notice
- Migration Guide
- Timeline (min 30d)
- Monitoring

### 5. Orphaned Ressourcen

Definition:
- Kein Owner
- Keine Dokumentation
- Keine Usage

Pflicht:
- Sofort quarantine
- Investigation (7d)
- Entscheidung: adopt or remove

## Lifecycle-Workflow

```
planned (max 90d)
   ↓
active_managed ←→ migrated (max 30d)
   ↓
quarantined (max 180d)
   ↓
removed_with_evidence

blocked (max 30d, von jedem Status)
   ↓
(active_managed oder removed_with_evidence)
```

## Decision Log

Jede Status-Änderung muss dokumentiert werden:

```markdown
## [YYYY-MM-DD] [Resource] [Old Status] → [New Status]

**Grund**: Warum wurde geändert
**Evidence**: Links, Commits, Screenshots
**Owner**: Wer hat entschieden
**Review**: Wann wird überprüft
```

## Enforcement

### Automatisch

- **Pre-Commit Hooks**: Verhindern unklassifizierte Dateien
- **CI Checks**: Prüfen Manifest Konsistenz
- **Monitoring**: Alert bei Status-Verletzung

### Manuell

- **Weekly Review**: Alle `planned` und `blocked` prüfen
- **Monthly Audit**: Vollständiges Resource Inventory
- **Quarterly Cleanup**: Quarantined und obsolete entfernen

## Compliance Check (Weekly)

- [ ] Alle neuen Ressourcen klassifiziert
- [ ] Alle `planned` < 90d
- [ ] Alle `blocked` < 30d
- [ ] Alle `quarantined` < 180d
- [ ] Resource Catalog aktuell
- [ ] Manifests konsistent
- [ ] Keine Orphans
- [ ] Keine TEMP_* > 24h

## Consequences

### Bei Verstoß

1. **Erster Verstoß** → Warning + sofortige Klassifizierung
2. **Zweiter Verstoß** → Automatische Quarantäne
3. **Dritter Verstoß** → Owner-Sperre + Review

### Bei Compliance

- ✅ Resource Catalog aktuell
- ✅ Keine technischen Schulden
- ✅ Klare Ownership
- ✅ Vorhersehbare Maintenance

## Integration

### Project Manager

- Prüft Status bei jedem Task
- Updated Resource Catalog
- Erstellt Issues für Violations
- Eskaliert bei `blocked` > 30d

### Goose

- Klassifiziert neue Ressourcen sofort
- Updated Manifests
- Respektiert Status in Tasks
- Meldet Orphans

### CI/CD

- Pre-Commit: Manifest Check
- PR Check: Resource Catalog Update
- Post-Merge: Status Validation

## Examples

### Good: Planned Feature

```
Status: planned
Owner: @team
Created: 2026-05-25
Timeline: Q3 2026
Issue: #123
Approval: [Link]
```

### Bad: Orphaned File

```
❌ file.py (no manifest, no owner, no docs)
```

### Fix

```
1. Quarantine
2. Investigate (7d)
3. Decide: adopt or remove
4. Document in Resource Catalog
```

## Escalation

Bei Fragen oder Konflikten:

1. **Project Manager** → Erste Instanz
2. **Team Lead** → Zweite Instanz
3. **Stakeholder** → Finale Entscheidung

## Related Documents

- [Resource Lifecycle Policy (Detailed)](../project-manager-handoff/docs/20_RESOURCE_LIFECYCLE_POLICY.md)
- [Existing Artifacts Decision Log](./EXISTING_ARTIFACTS_DECISION_LOG.md)
- [Resource Catalog](../agency/learning/resource-catalog.json)

## Version History

- **v1.0** (2026-05-25) - Initial Policy, extracted from PR #17 handoff
