# 12 - Autonomous Delivery Rules

## Ziel

Diese Policy definiert, wie Project Manager, Goose, Goose AI ACC und weitere AI-Agenten Arbeit vollständig autonom bis zur GitHub-Rückmeldung, PR-Führung und gegebenenfalls Merge-Fähigkeit führen.

Autonomie bedeutet nicht nur lokale Ausführung. Autonomie bedeutet vollständige Rückverfolgbarkeit im Repo.

## Repo-Dokumentation ist verbindlich

Alle verbindlichen Vorgaben, Projektleiter-Entscheidungen, Repo-Wahrheiten, Kundenrepo-Klassifizierungen, PR-/Push-/Merge-Regeln, Runtime-Entscheidungen und Agentenpflichten müssen im Repo dokumentiert werden.

Runtime-Prompts, Brain-Einträge und Chat-Verläufe dürfen Repo-Dokumentation ergänzen, aber nicht ersetzen.

Wenn eine neue verbindliche Regel entsteht, muss der Agent prüfen, ob sie im Repo zu dokumentieren ist. Wenn ja, muss er nach erfüllten Gates einen Dokumentations-PR erstellen oder aktualisieren.

## Autonome GitHub-Rückmeldung

Jeder Agent muss eigene Arbeit selbst über GitHub zurückmelden.

Pflichten:

1. passenden Branch erstellen oder aktualisieren,
2. Änderung committen,
3. Branch pushen,
4. Pull Request erstellen oder bestehenden PR aktualisieren,
5. PR-Body mit Ziel, Kontext, Änderungen, Evidence, Tests, Risiken und offenen Punkten pflegen,
6. CI-/Check-Status verfolgen,
7. Review-Kommentare verarbeiten,
8. Folgecommits pushen,
9. Brain aktualisieren,
10. Abschlussstatus mit Branch, Commit, PR, Checks und nächster Aktion liefern.

Wenn ein Token oder eine GitHub-Berechtigung einen Schritt blockiert, muss der Agent:
- den exakten Fehler dokumentieren,
- benennen, welche Permission fehlt,
- den bereits erledigten Stand sichern,
- die nächste manuelle Minimalaktion angeben,
- nach Rechtekorrektur automatisch fortsetzen.

## Auto-Merge-Grundsatz

Auto-Merge ist erlaubt, wenn alle Merge-Gates erfüllt sind.

Auto-Merge ist nicht erlaubt, wenn ein Gate offen, unklar oder rot ist.

Der Agent darf Merge nicht als erledigt melden, solange der PR nicht tatsächlich gemerged ist.

## Merge-Gates

Vor Merge müssen erfüllt sein:

1. gültiges Repo bestätigt,
2. Branch korrekt,
3. PR existiert,
4. PR-Body vollständig,
5. Diff geprüft,
6. keine Secrets,
7. keine verbotenen Kundenrepo-Änderungen,
8. CI/Checks grün oder bei Dokumentations-only nachvollziehbar nicht erforderlich,
9. Scope dokumentiert,
10. Risiken dokumentiert,
11. Brain aktualisiert,
12. Projektleiter-Kontext berücksichtigt,
13. keine widersprüchlichen Vorgaben offen.

## Dokumentations-only Auto-Merge

Dokumentations-only-PRs dürfen automatisch gemergt werden, wenn:

- nur Dateien unter `docs/` betroffen sind,
- keine Runtime-Dateien geändert werden,
- keine Secrets enthalten sind,
- Repo-Wahrheit und Projektleiter-Kontext eingehalten sind,
- Checks grün sind oder keine relevanten Checks erforderlich sind,
- PR-Body vollständig ist,
- kein `do-not-merge`, `security-review-needed` oder vergleichbarer Blocker existiert.

## Kein Auto-Merge ohne explizite Evidence

Kein automatischer Merge bei:

- Codeänderungen,
- Runtime-Änderungen,
- Domain-/Routing-Änderungen,
- Deployment-Änderungen,
- Security-relevanten Änderungen,
- Kundenrepo-Änderungen,
- Datenbank-/Migration-Änderungen,
- API-/Webhook-Änderungen,
- unklarer Repo-Klassifizierung,
- fehlender Evidence,
- fehlender Berechtigung.

In diesen Fällen darf der Agent nur PR vorbereiten, Evidence sammeln und Review/Merge-Freigabe dokumentieren.

## Kundenrepo-Regel

Kunden-Repos liegen ausschließlich im GitHub-Organisationsbereich:

`NeXify-AI-by-NeXify-Chat-it-Automat-it`

Vor jeder Arbeit an einem Kunden-Repo muss die Repo-Klassifizierung aus `11_REPO_TRUTH_AND_PR_OWNERSHIP.md`, Brain und Projektleiter-Kontext geprüft werden.

Unklassifizierte, Backup-, Sicherheitskopie-, Ursprungsdaten- oder Archiv-Repos dürfen nicht aktiv bearbeitet werden.

## Statuspflicht

Jeder Lauf muss melden:

1. Repo,
2. Branch,
3. Commit,
4. Push-Status,
5. PR-Status,
6. PR-Body-Status,
7. Check-/CI-Status,
8. Merge-Status,
9. Brain-Update,
10. offene Blocker,
11. nächste Aktion.

Keine Arbeit darf im Status `unklar` enden. Wenn etwas blockiert ist, muss der Blocker eindeutig benannt werden.

## Konsequenz bei fehlender Autonomie

Wenn der Benutzer manuell committen, pushen, PR erstellen, PR-Body ergänzen oder mergen musste, muss der Agent danach eine Ursachenanalyse liefern:

1. Welche Berechtigung fehlte?
2. Welche Regel fehlte?
3. Welcher Automationsschritt fehlte?
4. Welche Dokumentation muss ergänzt werden?
5. Welche Runtime-/Token-/GitHub-Konfiguration muss korrigiert werden?

Das Ergebnis muss in Brain und, wenn dauerhaft relevant, im Repo dokumentiert werden.
