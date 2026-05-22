# ADR-020: Repository-Konsolidierung — Single Source of Truth

**Status:** accepted
**Datum:** 2026-05-21
**Autor:** File-Organizer-Agent / AI-CEO (AIC-64)
**Stakeholder:** Alle Entwickler, DevOps, CTO

## Kontext
Die Repository-Analyse hat massive Duplikate identifiziert:
1. **agentur-repo/** ↔ **nexifyai-portal/** → >80% identisch
2. **nexifyai-workstation/** ↔ **workstation-repo/** → Workstation-Code gespiegelt
3. **sicher-repo/** → Weitgehend identisch mit agentur-repo
4. **5+ System-Audit-Ordner** nebeneinander

Dies verursacht Wartungs-Albtraum, Inkonsistenzen und verschwendet Entwicklerzeit.

## Problem
Duplikate führen zu:
- Bug-Fixes in einem Repo, aber nicht im anderen
- Verwirrung welches die aktuelle Version ist
- Verschwendeter Storage und CI/CD-Zeit
- Keine klare Package-Governance

## Optionen
1. **Option A: agentur-repo als Single Source of Truth + Symlinks** (Gewählt)
   - Pro: Einfach, nachvollziehbar, Git-tracking-fähig
   - Contra: Keine echte Trennung

2. **Option B: Vollständige Monorepo-Migration**
   - Pro: Eine einzige Source of Truth
   - Contra: Riesiger initialer Merge-Aufwand

3. **Option C: Git-Submodule**
   - Pro: Klare Trennung
   - Contra: Komplexität im Workflow

## Entscheidung
Option A für Phase 1: **agentur-repo als Single Source of Truth**
- `nexifyai-portal/` → Symlink auf `agentur-repo/` (nach Konsolidierung)
- `sicher-repo/` → Markiert als Legacy, nur kritische Fixes
- `workstation-repo/` → Nach `agentur-repo` migrieren, dann löschen
- System-Audit-Ordner: Nur aktuellsten behalten, Rest archivieren

Phase 2 (nach Sicherheitsfixes): Evaluierung von Option B (echte Monorepo-Struktur)

## Konsequenzen
### Positiv
- 📦 Single Source of Truth für allen Code
- 🔧 Einmalige Fixes statt Duplikate
- 📉 Reduzierte Wartungskomplexität

### Negativ
- ⏱️ Initialer Merge-Aufwand
- ⚠️ Bestehende CI/CD-Pfade müssen aktualisiert werden

### Neutral
- Symlinks sind transparent für Git
- Keine Daten-Verluste durch Löschung (alles in agentur-repo)

## Rollback-Plan
1. Symlinks durch echte Kopien ersetzen
2. Workstation-Code wieder trennen falls nötig
3. System-Audit-Ordner aus Backup wiederherstellen

## Verweise
- [TASK-006: Repository-Duplikate auflösen](/docs/tasks/MASTER_TASKBOARD.md)
- [TASK-007: Workstation-Code konsolidieren](/docs/tasks/MASTER_TASKBOARD.md)
- [TASK-008: System-Audit-Ordner bereinigen](/docs/tasks/MASTER_TASKBOARD.md)
- Monorepo-Struktur: siehe ADR-004
