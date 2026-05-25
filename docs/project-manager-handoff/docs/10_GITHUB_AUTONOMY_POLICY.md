# 10 - GitHub Autonomy Policy

## Ziel

Project Manager und Goose dürfen GitHub autonom nutzen, aber mit klaren Grenzen und Safety Checks.

## Erlaubte Aktionen

### Branch Management
- ✅ Branches erstellen (feature/, fix/, chore/, refactor/)
- ✅ Branches löschen (nach Merge)
- ✅ Branch Protection Rules respektieren
- ✅ Rebase/Force-Push auf eigenen Branches

### Commits
- ✅ Commits erstellen (conventional commits)
- ✅ Commit Messages nach Schema
- ✅ Signierte Commits (wenn konfiguriert)
- ✅ Squash/Merge Commits

### Pull Requests
- ✅ PRs erstellen (mit Template)
- ✅ PRs updaten (Review Feedback)
- ✅ PRs mergen (wenn Checks grün)
- ✅ PRs schließen (wenn obsolete)

### Issues
- ✅ Issues erstellen (mit Labels)
- ✅ Issues updaten (Status, Assignees)
- ✅ Issues schließen (mit Evidence)
- ✅ Issue Templates nutzen

### Labels
- ✅ Labels erstellen (nach Schema)
- ✅ Labels zuweisen
- ✅ Labels entfernen

### Checks & CI
- ✅ CI/CD Triggers respektieren
- ✅ Check Results lesen
- ✅ Checks re-run (wenn nötig)

## Verbotene Aktionen

### Branch Protection
- ❌ Kein direkter Push auf `main`
- ❌ Kein Force-Push auf `main`
- ❌ Keine Branch Protection Rules umgehen
- ❌ Keine Protected Branches löschen

### Secrets
- ❌ Keine Secrets in Commits
- ❌ Keine Secrets in PR Descriptions
- ❌ Keine Secrets in Issue Comments
- ❌ Keine Secrets in Logs

### Security
- ❌ Keine Security Findings ohne Evidence schließen
- ❌ Keine Vulnerability Reports ignorieren
- ❌ Keine Security Labels entfernen ohne Review

### Auto-Merge
- ❌ Kein Auto-Merge ohne:
  - Alle Checks grün
  - Keine Produktivlogik betroffen
  - Kein Security Risk
  - Review approved (wenn erforderlich)

## Auto-Merge Bedingungen

Auto-Merge ist erlaubt wenn:

1. **Checks**
   - [ ] CI/CD grün
   - [ ] Lint/Format grün
   - [ ] Tests bestanden
   - [ ] Security Scan clean

2. **Scope**
   - [ ] Nur Dokumentation
   - [ ] Nur Config (nicht produktiv)
   - [ ] Nur Dependencies (minor/patch)
   - [ ] Keine Breaking Changes

3. **Review**
   - [ ] Kein Review required ODER
   - [ ] Review approved

4. **Labels**
   - [ ] `auto-merge` Label gesetzt
   - [ ] Kein `do-not-merge` Label
   - [ ] Kein `security-review-needed` Label

## Evidence Pflicht

Jede GitHub-Aktion muss dokumentiert werden:

- Branch erstellt → Link im Task Report
- PR erstellt → PR URL im Task Report
- Issue erstellt → Issue URL im Task Report
- Merge → Commit SHA im Task Report

## Rollback

Bei Problemen:

1. Merge sofort reverten
2. Branch wiederherstellen (wenn gelöscht)
3. Issue erstellen für Investigation
4. Task Report aktualisieren

## Monitoring

Project Manager muss prüfen:

- [ ] Branch Protection Rules aktiv
- [ ] Required Checks konfiguriert
- [ ] Secret Scanning aktiv
- [ ] Dependabot aktiv
- [ ] CodeQL aktiv (wenn konfiguriert)

## Eskalation

Bei Unsicherheit:

1. **Stop** - Keine Aktion
2. **Document** - Issue erstellen
3. **Escalate** - Human Review anfordern
4. **Wait** - Auf Freigabe warten

## Source of Truth

**GitHub ist Source of Truth** für:

- Code
- Documentation
- Issues
- PRs
- Releases
- CI/CD Status

**Nicht Source of Truth:**

- Lokale Dateien
- Chat-Verläufe
- Brain (nur Cache/Context)
- Externe Systeme

## Compliance

Alle GitHub-Aktionen müssen:

- Conventional Commits folgen
- Issue/PR Templates nutzen
- Labels korrekt zuweisen
- Milestones tracken
- Projects aktualisieren

## Audit Trail

Project Manager muss loggen:

- Wer hat was gemacht
- Wann wurde es gemacht
- Warum wurde es gemacht
- Was war das Ergebnis
- Gibt es Follow-ups

## Konsequenzen

Bei Verstoß:

1. **Erster Verstoß** → Warning + Dokumentation
2. **Zweiter Verstoß** → Autonomy Level reduzieren
3. **Dritter Verstoß** → Autonomy suspendieren
4. **Kritischer Verstoß** → Sofort stoppen + Human Review
