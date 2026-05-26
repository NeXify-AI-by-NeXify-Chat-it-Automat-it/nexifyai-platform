# 11 - Repo Truth and PR Ownership Policy

## Verbindliche Repo-Wahrheit

Die Kunden-Repositories liegen im GitHub-Organisationsbereich:

`NeXify-AI-by-NeXify-Chat-it-Automat-it`

Dieser Organisationsbereich ist der verbindliche Bereich für Agentur- und Kunden-Repositories.

Das einzige gültige Agentur-Repo ist:

`NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform`

Kunden-Repos sind nicht lokal, nicht geraten und nicht außerhalb dieses Organisationsbereichs zu suchen.

## Kunden-Repo-Klassifizierung

Vor jeder Arbeit an einem Kunden-Repo muss der konkrete Repository Full Name im GitHub-Organisationsbereich geprüft und klassifiziert werden.

Repos mit Namen oder Zweck wie:

- `sicherheitskopie`
- `backup`
- `ursprungsdaten`
- `archive`
- `copy`
- unklarer Zweck

sind nicht automatisch aktive Kunden-Repos.

Sie dürfen nur analysiert und klassifiziert werden, bis Projektleiter-Kontext und Brain die aktive Bearbeitung eindeutig bestätigen.

## Aktuell bekannte Repos im Organisationsbereich

| Repo | Klassifizierung | Bearbeitung |
| --- | --- | --- |
| `nexifyai-platform` | Agentur-Repo, aktive Hauptwahrheit | erlaubt nach Gates |
| `studienkolleg-aachen-sicherheitskopie` | Sicherheitskopie / unklar | keine aktive Bearbeitung ohne Freigabe |
| `opencarbox-2026-sicherheitskopie` | Sicherheitskopie / unklar | keine aktive Bearbeitung ohne Freigabe |
| `affilinet-portal-aachen-final` | Kunden-/Projekt-Repo unklar | erst klassifizieren |
| `ursprungsdaten-emergent` | Ursprungsdaten / unklar | keine aktive Bearbeitung ohne Freigabe |

## PR- und Push-Verantwortung

Ein Agent darf abgeschlossene oder reviewfähige Arbeit nicht lokal liegen lassen und darf den Benutzer nicht zum manuellen Commit, Push oder PR zwingen.

Nach erfüllten Gates muss der Agent selbst:

1. einen passenden Branch führen,
2. Änderungen nachvollziehbar committen,
3. den Branch pushen,
4. einen Pull Request erstellen oder aktualisieren,
5. PR-Beschreibung, Evidence, Tests, Risiken und offene Punkte dokumentieren,
6. Brain und Projektleiter-Kontext aktualisieren,
7. Status mit Branch, Commit, PR und nächster Aktion melden.

## Gates vor Push oder PR

Vor Push oder PR müssen erfüllt sein:

1. Projektleiter-/Handoff-Kontext geprüft,
2. Brain-Kontext abgefragt,
3. gültiges Repo eindeutig klassifiziert,
4. Branch und Remote geprüft,
5. offene PRs geprüft,
6. Diff vollständig geprüft,
7. keine Secrets im Diff,
8. Tests, Build, Lint oder begründete Ersatzprüfung durchgeführt,
9. Live-/Runtime-Auswirkung bewertet,
10. Evidence dokumentiert,
11. keine widersprüchlichen Vorgaben offen.

Wenn ein Gate nicht erfüllt ist, darf nicht gepusht und kein PR erstellt werden. Der Agent muss Blocker, Risiko und nächste sichere Aktion dokumentieren.

## Falsche Commits oder falsche Repos

Wenn ein Commit, Push oder PR in einem falschen Repo oder unter falscher Annahme entstanden ist:

1. keine weiteren Änderungen darauf aufbauen,
2. betroffenen Commit, Branch oder PR identifizieren,
3. Diff und Risiko prüfen,
4. Brain und Projektleiter-Kontext abgleichen,
5. Korrekturplan liefern: behalten, revertieren, schließen oder neu aufsetzen,
6. keine direkte Änderung an geschützten Branches,
7. keine Historie umschreiben ohne explizite Freigabe.

## Benutzer darf GitHub-Rückmeldung nicht ersetzen müssen

Der Benutzer darf nicht gezwungen sein, manuell gegenteilige Aussagen, Commits, Pushes oder PR-Kommentare ins System zu bringen, damit Agenten ihre Arbeit verstehen oder zurückmelden.

Agenten müssen Status, Commit, Push, PR, CI, Review, Brain-Update und offene Risiken proaktiv selbst pflegen.
