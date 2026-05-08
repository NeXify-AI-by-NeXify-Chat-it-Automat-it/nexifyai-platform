# PR Merge Policy
# DOS v2.0 Chapter 13.2

## Pflicht-Inhalt jedes PR

Jeder Pull Request muss enthalten:
1. **Zielbeschreibung** — Was wird geändert? Warum?
2. **Funnel-Zuordnung** — Welchem Funnel-Schritt dient diese Änderung?
3. **Risikoabschätzung** — Low / Medium / High + Begründung
4. **Migrations-Hinweise** — Breaking Changes, DB-Migrationen, API-Änderungen
5. **UI-Screenshots** — Before/After (bei Frontend-Änderungen)
6. **Tracking-Änderungen** — Neue Events, geänderte Events
7. **Claims-Review** — Neue/geänderte Marketing-Aussagen
8. **Tests** — Neue Tests oder Begründung warum nicht

## Review-Anforderungen

| Projekt-Klasse | Reviewer |
|---|---|
| Standard | 1 Reviewer |
| Enterprise/Compliance | 2 Reviewer (Tech Lead + Security) |
| Produktions-Infrastruktur | 1 Senior Review + Änderungsdokument |
| Security-kritisch | Security Reviewer + Risikobewertung |

## Quality Gates (müssen grün sein)

- Lint: 0 Fehler
- Typecheck: 0 Fehler
- Unit Tests: grün (Coverage ≥ 80%)
- Build: erfolgreich (npm run build Exit 0)
- Dependency Audit: 0 kritische CVEs
- Secret Scan: 0 Findings
- Performance: LCP < 2.5s, CLS < 0.1

## Prinzip F

Kein Push ohne lokalen Build: `npm run build` muss Exit 0 sein.
`git diff --cached` muss vor Push geprüft sein.
