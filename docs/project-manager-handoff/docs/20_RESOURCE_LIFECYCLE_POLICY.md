# Resource Lifecycle Policy

## Ziel

Keine Ressource darf halb gebaut oder unklassifiziert bleiben. Jede Ressource muss einen klaren Status haben.

## Status Definitionen

### `active_managed`
- **Bedeutung**: Ressource ist aktiv und wird gemanagt
- **Anforderungen**:
  - Dokumentation vorhanden
  - Monitoring aktiv
  - Owner zugewiesen
  - Regelmäßige Reviews
- **Beispiele**:
  - Production Services
  - Aktive Dokumentation
  - Genutzte Automationen

### `planned`
- **Bedeutung**: Ressource ist geplant, aber noch nicht implementiert
- **Anforderungen**:
  - Plan dokumentiert
  - Timeline definiert
  - Dependencies klar
  - Approval vorhanden
- **Maximale Dauer**: 90 Tage
- **Danach**: Implementieren oder `blocked`

### `migrated`
- **Bedeutung**: Ressource wurde migriert, alte Version deprecated
- **Anforderungen**:
  - Migration dokumentiert
  - Alte Version archiviert
  - Neue Version `active_managed`
  - Redirect/Notice vorhanden
- **Beispiele**:
  - Alte API → Neue API
  - Altes Repo → Neues Repo
  - Alte Doku → Neue Doku

### `quarantined`
- **Bedeutung**: Ressource ist isoliert, nicht aktiv, nicht gelöscht
- **Anforderungen**:
  - Grund dokumentiert
  - Manifest vorhanden
  - Keine aktiven Dependencies
  - Review geplant
- **Beispiele**:
  - Unfertige Experimente
  - Deprecated aber noch benötigt
  - Security Issues (pending fix)

### `removed_with_evidence`
- **Bedeutung**: Ressource wurde gelöscht, Evidence archiviert
- **Anforderungen**:
  - Löschgrund dokumentiert
  - Evidence gespeichert (Git, Logs, Screenshots)
  - Dependencies geprüft
  - Stakeholder informiert
- **Beispiele**:
  - Temporäre Test-Dateien
  - Obsolete Dokumentation
  - Fehlgeschlagene Experimente

### `blocked`
- **Bedeutung**: Ressource kann nicht fortgesetzt werden
- **Anforderungen**:
  - Blocker dokumentiert
  - Issue erstellt
  - Owner zugewiesen
  - Nächster Schritt definiert
- **Maximale Dauer**: 30 Tage
- **Danach**: Lösen oder `removed_with_evidence`

## Lebenszyklus

```
planned
   ↓
active_managed ←→ migrated
   ↓
quarantined
   ↓
removed_with_evidence

blocked (kann von jedem Status)
   ↓
(active_managed oder removed_with_evidence)
```

## Regeln

### 1. Keine halbfertigen Ressourcen

**Verboten**:
- Dateien ohne Dokumentation
- Services ohne Monitoring
- Automationen ohne Tests
- Branches ohne PR

**Pflicht**:
- Sofort klassifizieren
- Status im Manifest dokumentieren
- Owner zuweisen
- Review planen

### 2. Temporäre Dateien

**Erlaubt für**:
- Tests (max 24h)
- Experiments (max 7d)
- Debug (max 1h)

**Pflicht**:
- Naming: `TEMP_*`, `TEST_*`, `DEBUG_*`
- Auto-Cleanup konfiguriert
- Review nach Ablauf

### 3. Unfertige Implementierungen

**Verboten**:
- Code ohne Status
- Features ohne Tests
- Docs ohne Review

**Pflicht**:
- Feature Branch mit WIP Label
- Issue mit Fortschritt
- PR Draft mit Plan

### 4. Deprecated Ressourcen

**Verboten**:
- Stille Deprecation
- Keine Notice
- Keine Migration

**Pflicht**:
- Deprecation Notice
- Migration Guide
- Timeline (min 30d)
- Monitoring

### 5. Orphaned Ressourcen

**Definition**:
- Kein Owner
- Keine Dokumentation
- Keine Usage

**Pflicht**:
- Sofort quarantine
- Investigation (7d)
- Entscheidung: adopt or remove

## Decision Log

Jede Status-Änderung muss dokumentiert werden:

```markdown
## [Date] [Resource] [Old Status] → [New Status]

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

## Tools

### Resource Catalog

**Location**: `docs/project-manager/RESOURCE_CATALOG.md`

**Struktur**:
```markdown
| Resource | Status | Owner | Last Review | Notes |
|----------|--------|-------|-------------|-------|
| ...      | ...    | ...   | ...         | ...   |
```

### Manifest

**Location**: Pro Resource (z.B. `MANIFEST.md` im Verzeichnis)

**Inhalt**:
```markdown
# [Resource Name]

**Status**: active_managed | planned | migrated | quarantined | removed_with_evidence | blocked
**Owner**: [Name/Team]
**Created**: [Date]
**Last Review**: [Date]
**Next Review**: [Date]

## Purpose
Warum existiert diese Ressource

## Dependencies
Was hängt davon ab

## Evidence
Links, Commits, Tests

## Decision Log
- [Date] [Change] [Reason]
```

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
Created: 2024-01-15
Timeline: Q1 2024
Issue: #123
Approval: [Link]
```

### Bad: Orphaned File

```
❌ file.py (no manifest, no owner, no docs)
```

### Fix:

```
1. Quarantine
2. Investigate (7d)
3. Decide: adopt or remove
4. Document in Resource Catalog
```

## Questions

**Q**: Was wenn ich unsicher bin?  
**A**: Immer `planned` oder `blocked`, nie unklassifiziert

**Q**: Was wenn Owner fehlt?  
**A**: Sofort `blocked` + Issue erstellen

**Q**: Was wenn Deadline verpasst?  
**A**: Status reviewen, extend oder remove

**Q**: Was wenn Dependencies unklar?  
**A**: Investigation Task erstellen, nicht ignorieren

## Compliance Check

Weekly Checklist:

- [ ] Alle neuen Ressourcen klassifiziert
- [ ] Alle `planned` < 90d
- [ ] Alle `blocked` < 30d
- [ ] Resource Catalog aktuell
- [ ] Manifests konsistent
- [ ] Keine Orphans
- [ ] Keine TEMP_* > 24h

## Escalation

Bei Fragen oder Konflikten:

1. **Project Manager** → Erste Instanz
2. **Team Lead** → Zweite Instanz
3. **Stakeholder** → Finale Entscheidung

## Version

- **v1.0** - 2024-01-15 - Initial Policy
- **Owner**: Project Manager
- **Review**: Quarterly
