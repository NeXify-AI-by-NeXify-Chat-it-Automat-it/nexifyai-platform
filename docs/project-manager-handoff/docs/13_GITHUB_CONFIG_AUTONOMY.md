# 13 — GitHub-Konfiguration für volle Agenten-Autonomie

> **Stand: 2026-05-26T06:51 UTC**
> Policies #11, #12 sind gemerged. Dieses Dokument enthält das vollständige GitHub-Konfigurations-Audit,
> den Soll-Zustand und den schrittweisen Reparaturplan für alle Bereiche.

---

## Teil A: Ist-Stand (Audit 2026-05-26)

### A1 Repository-Settings

| Einstellung | Ist | Soll | Bemerkung |
| --- | --- | --- | --- |
| mergeCommitAllowed | ✅ true | true | ✅ |
| squashMergeAllowed | ✅ true | true | ✅ |
| rebaseMergeAllowed | ✅ true | true | ✅ |
| deleteBranchOnMerge | ❌ **false** | true | PRs hinterlassen tote Branches |
| autoMergeAllowed | ❌ **nicht abfragbar (API 403)** | true | unbekannt |
| hasIssuesEnabled | ✅ true | true | ✅ |
| hasProjectsEnabled | ✅ true | true | ✅ |
| hasWikiEnabled | ❌ false | false | Wiki nicht benötigt (Docs im Repo) |
| isSecurityPolicyEnabled | ✅ true | true | ✅ |
| visibility | PUBLIC | PUBLIC | ✅ |
| defaultBranch | main | main | ✅ |
| viewerPermission | ✅ ADMIN | ADMIN | ✅ |

**Fehlende Konfiguration (UI nötig):**
- `Allow auto-merge` → true
- `Automatically delete head branches` → true
- `Always suggest updating pull request branches` → true

### A2 Ruleset "NeXify AI Plattform" (ID: 16636366)

| Eigenschaft | Ist | Bewertung |
| --- | --- | --- |
| enforcement | active | ✅ |
| target | branch | ✅ |
| Ziel-Branches | `~ALL` | ❌ Kein `docs/`-Ausschluss |
| Ausgeschlossen | `[]` (leer) | ❌ `docs/**` fehlt |
| bypass_mode | `always` für OrgAdmin, RepositoryRole (Write+), Integrations | ✅ Goose kann bypassen |

**Aktive Regeln:**

| Regel | Typ | Bewertung |
| --- | --- | --- |
| ❌ deletion | Branch-Löschung verboten | Verhindert `git push --delete`. Bypass: ✅ always |
| ❌ required_linear_history | Keine Merge-Commits | Verursacht Push-Warnungen. Bypass: ✅ always |
| ❌ pull_request | PR für ALLE Branches nötig | Erzwingt PR-Zwang auf docs/-Branches. Bypass: ✅ always |
| ✅ code_scanning | CodeQL bei `errors` + `high_or_higher` | Sinnvoll, aber hohe Schwelle |
| ✅ code_quality | severity: all | Sinnvoll |

**Empfohlene Änderung:**
- `conditions.ref_name.exclude` → `["refs/heads/docs/**"]`
- Oder: `include` auf `["refs/heads/main"]` beschränken

### A3 Branch Protection (main)

| API-Status | Bedeutung |
| --- | --- |
| ❌ 403 | Token hat keine `administration: read` für Branch-Protection-API |
| Bypass | Ruleset `~ALL` mit `pull_request` deckt main ab |

**Aktuell:** Kein separates Branch-Protection-Ruleset für main. Der Schutz kommt vollständig aus dem Ruleset "NeXify AI Plattform". Das Ruleset zwingt PRs für ALLE Branches, inkl. docs/.

### A4 Actions

| Workflow | Status | Letzte Runs |
| --- | --- | --- |
| CI | ✅ active | ✅ success |
| CodeQL | ✅ active | ⚠️ 5 failed (test-Branches), ✅ sonst |
| Enterprise Status Badges | ✅ active | ✅ success |
| OpenAPI Lint — Spectral | ✅ active | ✅ success |
| Tests — pytest + jest | ✅ active | ✅ success |
| Vercel Deploy - Post-Deploy Convergence (E6) | ✅ active | ✅ success |
| Security — Secrets (Gitleaks) | ✅ active | ? |
| Security — Dependencies | ✅ active | ? |
| Security — Container (Trivy) | ✅ active | ? |
| SBOM Generation (CycloneDX/SPDX) | ✅ active | ? |
| Uptime Check | ✅ active | ✅ success |
| Dependabot Updates | ✅ active | ✅ |
| Dependency Graph | ✅ active | ✅ |
| Cline PR Code Review [LEGACY - DISABLED] | active (disabled) | ❌ Nicht entfernt |
| Cline Issue Assistant [LEGACY - DISABLED] | active (disabled) | ❌ Nicht entfernt |

**Failed CodeQL Runs (5 Stück):**
Alle aufgelösten Test-Branchen, keine produktiven Branches betroffen:
1. `docs/autonomy-token-test` → failure
2. `docs/autonomy-final-test` → failure
3. `docs/autonomy-pr-permission-check` → failure
4. `tmp/permission-test` → failure
5. PR #30 Security — CodeQL Analysis → failure (behoben durch #30)

### A5 Security

| Bereich | API-Zugriff | Status |
| --- | --- | --- |
| Dependabot Alerts | ❌ 403 | Token hat `dependabot_alerts: read` nicht |
| Code Scanning Alerts | ❌ 403 | Token hat `code_scanning_alerts: read` nicht |
| Secret Scanning Alerts | ❌ 403 | Token hat `secret_scanning_alerts: read` nicht |
| Vulnerability Alerts | ❌ 403 | Token hat `vulnerability_alerts: read` nicht |

**Erkenntnis:** Der Fine-Grained PAT von `nexifyai-dev` hat **keine Security-Read-Permissions**. Ohne diese können Security-Findings weder gelesen noch klassifiziert noch behoben werden.

### A6 Pull Request Templates

| Template | Status |
| --- | --- |
| `.github/PULL_REQUEST_TEMPLATE.md` | ❌ **Nicht vorhanden** (404) |

Kein PR-Template vorhanden. PR-Bodies sind in den letzten 30 PRs oft leer oder minimal.

### A7 Issues & Labels

**Labels (14 vorhanden):**

| Label | Farbe | Typ | Bewertung |
| --- | --- | --- | --- |
| bug | #d73a4a | Standard | ✅ |
| documentation | #0075ca | Standard | ✅ |
| duplicate | #cfd3d7 | Standard | ✅ |
| enhancement | #a2eeef | Standard | ✅ |
| good first issue | #7057ff | Standard | ✅ |
| help wanted | #008672 | Standard | ✅ |
| invalid | #e4e669 | Standard | ✅ |
| question | #d876e3 | Standard | ✅ |
| wontfix | #ffffff | Standard | ✅ |
| auto-generated | #ededed | Custom | ✅ |
| test | #ededed | Custom | ⚠️ unspezifisch |
| enterprise-runtime | #0d1117 | Custom | ⚠️ unspezifisch |
| dependencies | #0366d6 | Custom | ✅ für Dependabot |
| javascript | #168700 | Custom | ✅ |

**Fehlende Labels:**
- `security` / `security-review-needed`
- `blocked` / `blocker`
- `priority-high` / `priority-critical`
- `agent-task`
- `docs-only`
- `customer-repo`
- `governance`
- `needs-classification`

**Issues:**
- 7 Issues insgesamt, alle CLOSED
- Issue #25 wurde automatisch für PR #25 erstellt
- Keine offenen Issues

### A8 Tokens & Permissions

| Token | Ist | Soll |
| --- | --- | --- |
| Fine-Grained PAT `nexifyai-dev` | `ADMIN` (Repo) | ✅ |
| Pull requests | ❌ **Read** (kein Write) | **Read and write** |
| Contents | ✅ Read and write | ✅ Read and write |
| Metadata | ✅ Read | ✅ Read |
| Actions | ❌ unbekannt | Read |
| Checks | ❌ unbekannt | Read |
| Dependabot alerts | ❌ fehlt | Read |
| Code scanning alerts | ❌ fehlt | Read |
| Secret scanning alerts | ❌ fehlt | Read |
| Administration | ❌ fehlt | Read |
| Commit statuses | ❌ unbekannt | Read |

**Empfehlung:** Für Produktion: GitHub App statt PAT. PAT ist an User gebunden und riskant bei Mitarbeiterwechsel.

### A9 PR-Historie

| Aspekt | Wert |
| --- | --- |
| PRs insgesamt | 30 (davon 2 von Dependabot) |
| Offene PRs | 0 |
| Gemerged | 30 |
| PRs mit Body | ⚠️ variabel, oft leer |
| PRs mit Tests/Evidence | ⚠️ dokumentiert, aber nicht standardisiert |
| Author | meist `nexifyai-dev`, teils `app/dependabot` |
| Merge-Commits | ja (Merge-Commit-Methode) |
| Letzter PR | #30 `Fix/remove scanner results secrets` |

### A10 Test-Branches

| Branch | Status |
| --- | --- |
| `docs/github-config-autonomy` | 🟢 **bleibt** — enthält Policy #13 |
| `docs/autonomy-permission-check` | 🗑️ gelöscht |
| `docs/autonomy-pr-permission-check` | 🗑️ gelöscht |
| `docs/autonomy-final-test` | 🗑️ gelöscht |
| `docs/autonomy-token-test` | 🗑️ gelöscht |
| `docs/autonomy-rest-test` | 🗑️ gelöscht |
| `tmp/permission-test` | 🗑️ gelöscht (nicht remote) |
| `chore/merge-security-policies-from-stale` | ⚠️ remote vorhanden (CodeQL lief darauf) |

---

## Teil B: Soll-Konfiguration

### B1 Repository Settings (GitHub UI)

```
Repositories → nexifyai-platform → Settings → General → Pull Requests:
☑ Allow merge commits
☑ Allow squash merging
☐ Default: PR title (besser als Commit-Titel)
☑ Allow rebase merging
☑ Always suggest updating pull request branches
☑ Allow auto-merge
☑ Automatically delete head branches
```

### B2 Ruleset (empfohlen: REST API via gh)

**Option A (empfohlen): docs/ ausnehmen**

```
PATCH /repos/.../rulesets/16636366
Bedingungen:
  include: ["~ALL"]
  exclude: ["refs/heads/docs/**"]
```

**Option B (strenger, aber sauber): nur main schützen**

```
Bedingungen:
  include: ["refs/heads/main"]
  exclude: []
```

**Regeln im Ruleset behalten:**
- ✅ `deletion` (Bypass für Admins)
- ✅ `required_linear_history` (Bypass für Admins)
- ✅ `code_scanning` (CodeQL)
- ✅ `code_quality`
- ❌ `pull_request` → **entfernen oder auf main beschränken** (PR-Zwang über Branch-Protection regeln)

### B3 Actions-Konfiguration

| Einstellung | Soll |
| --- | --- |
| Actions enabled | ✅ |
| Allow workflows to create/approve PRs | ✅ |
| Allow GitHub Actions to create/approve PRs | ✅ |
| Fork PR workflows | `Require approval for all external contributors` |
| Workflow permissions | `Read repository contents` (default) |
| GITHUB_TOKEN permissions | `Read and write` (wo nötig) |

**Legacy-Workflows entfernen:**
- `Cline PR Code Review [LEGACY - DISABLED]`
- `Cline Issue Assistant [LEGACY - DISABLED]`

### B4 Security

**Token-Permissions ergänzen (GitHub UI → Settings → Developer settings → Fine-grained tokens → nexifyai-dev):**
- `Dependabot alerts: Read`
- `Code scanning alerts: Read`
- `Secret scanning alerts: Read`
- `Vulnerability alerts: Read`

**Dependabot:**
- Dependabot security updates: ✅ aktiv
- Dependabot version updates: ✅ aktiv
- Alerts-Priorität: Critical/High → automatischer PR nach Policy #12 Gates

**CodeQL:**
- ✅ Aktiv (im Ruleset erzwungen)
- Config: `language: javascript, python, typescript`
- Scan-Branches: `main`, `docs/**` ausschließen

### B5 Pull Request Template

Datei: `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## Ziel

_Welches Problem löst dieser PR? Welche Policy/Decision wird umgesetzt?_

## Scope

- [ ] Dokumentation only
- [ ] Code / Runtime
- [ ] CI / Workflow
- [ ] Security / Dependencies
- [ ] Kundenrepo-Änderung

## Evidence

_Welche Tests, Builds, Lints oder Checks wurden durchgeführt und bestanden?_

## Risiken

- [ ] Keine Runtime-Änderung
- [ ] Keine Secrets
- [ ] Keine Breaking Changes
- [ ] Rückbau möglich

## Offene Punkte

_Welche Fragen, bekannten Einschränkungen oder Folgearbeiten gibt es?_
```

### B6 Labels

**Zu ergänzen:**

| Label | Farbe | Beschreibung |
| --- | --- | --- |
| `security` | #b60205 | Sicherheitsrelevantes Issue/PR |
| `blocked` | #e99695 | Wird durch externen Faktor blockiert |
| `priority-high` | #fbca04 | Hohe Priorität |
| `priority-critical` | #b60205 | Kritische Priorität |
| `agent-task` | #c5def5 | Vom Agenten auszuführende Aufgabe |
| `docs-only` | #0075ca | Nur Dokumentation betroffen |
| `customer-repo` | #5319e7 | Kundenrepo-Bezug |
| `governance` | #0e8a16 | Governance/Policy-Änderung |
| `needs-classification` | #d4c5f9 | Repo-Zweck unklar |
| `needs-evidence` | #fef2c0 | Fehlende Tests/Belege |

### B7 Issue Templates

Dateien unter `.github/ISSUE_TEMPLATE/`:

| Template | Dateiname | Zweck |
| --- | --- | --- |
| Bug Report | `bug_report.md` | Fehlermeldung |
| Feature Request | `feature_request.md` | Neue Funktion |
| Task / Policy | `task.md` | Agenten-Aufgabe, Policy-Änderung |
| Security | `security.md` | Sicherheitsfund |

### B8 Token/App-Konfiguration

**Kurzfristig (PAT):**
```
Fine-Grained PAT nexifyai-dev:
Repository permissions:
  ✅ Contents: Read and write
  ❌ Pull requests: Read and write (aktuelle nur Read)
  ❌ Issues: Read and write
  ❌ Actions: Read
  ❌ Checks: Read
  ❌ Dependabot alerts: Read
  ❌ Code scanning alerts: Read
  ❌ Secret scanning alerts: Read
  ❌ Administration: Read
  ❌ Commit statuses: Read
```

**Mittelfristig (GitHub App — empfohlen):**
```
GitHub App "NeXify AI Agent":
  Repository permissions:
    Contents: Read and write
    Pull requests: Read and write
    Issues: Read and write
    Metadata: Read
    Actions: Read
    Checks: Read
    Dependabot alerts: Read
    Code scanning alerts: Read
    Secret scanning alerts: Read
    Commit statuses: Read
  Installation: NeXify-AI-by-NeXify-Chat-it-Automat-it (alle Repos)
  Vorteil: Nicht an User gebunden, Rotation automatisch, fein granulare Permissions
```

---

## Teil C: Reparaturplan

### Phase 1: Token-Permission (P0 — 1 Minute UI)

```text
GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
→ nexifyai-dev → Repository permissions:
  - Pull requests: Read and write (!!WICHTIG!!)
  - Issues: Read and write
  - Actions: Read
  - Checks: Read
  - Dependabot alerts: Read
  - Code scanning alerts: Read
  - Secret scanning alerts: Read
  - Administration: Read
  - Commit statuses: Read
→ Save
```

### Phase 2: Repo-Settings (P1 — 2 Minuten UI)

```text
GitHub → nexifyai-platform → Settings → General → Pull Requests:
☑ Allow auto-merge
☑ Automatically delete head branches
☑ Always suggest updating pull request branches
```

### Phase 3: Ruleset korrigieren (P1 — API)

```bash
gh api -X PATCH repos/NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform/rulesets/16636366 \
  --input - <<'EOF'
{
  "conditions": {
    "ref_name": {
      "include": ["~ALL"],
      "exclude": ["refs/heads/docs/**"]
    }
  }
}
EOF
```

### Phase 4: PR-Template erstellen (P2 — Goose Commit)

```bash
# Branch: docs/pr-template
# Datei: .github/PULL_REQUEST_TEMPLATE.md
# Commit → Push → PR (nach Token-Fix)
```

### Phase 5: Labels ergänzen (P2 — Goose API)

```bash
gh label create security --color b60205 --description "Sicherheitsrelevantes Issue/PR"
gh label create blocked --color e99695 --description "Wird blockiert"
# ... alle weiteren Labels
```

### Phase 6: Legacy-Workflows entfernen (P2 — Goose Commit)

```bash
# Branch: chore/remove-legacy-workflows
# Dateien löschen: .github/workflows/cline-*.yml
# Commit → Push → PR
```

### Phase 7: Issue-Templates erstellen (P2 — Goose Commit)

```bash
# Branch: docs/issue-templates
# Dateien: .github/ISSUE_TEMPLATE/*.md
# Commit → Push → PR
```

### Phase 8: GitHub App erstellen (P3 — GitHub UI)

Nur bei Bedarf für Produktionsbetrieb. PAT reicht für Entwicklung.

---

## Teil D: Bekannte Blocker

| Blocker | Bereich | Lösung | Status |
| --- | --- | --- | --- |
| `createPullRequest: FORBIDDEN` | Token | Pull requests: Read and write setzen | ⏳ Phase 1 |
| Security Alerts 403 | Token | Security-Read-Permissions setzen | ⏳ Phase 1 |
| Actions Permissions 403 | Token | Actions: Read setzen | ⏳ Phase 1 |
| `deleteBranchOnMerge: false` | Repo-Settings | UI-Korrektur | ⏳ Phase 2 |
| Kein PR-Template | Dokumentation | Goose Commit | ⏳ Phase 4 |
| Fehlende Labels | Organisation | Goose API | ⏳ Phase 5 |
| Legacy-Workflows | Repository | Goose Commit | ⏳ Phase 6 |
| Keine Issue-Templates | Dokumentation | Goose Commit | ⏳ Phase 7 |

---

## Teil E: Autonomie-Test

Nach Abschluss aller Phasen:

```bash
cd /opt/nexify/repos/nexifyai-platform
git fetch origin --prune
git checkout main && git reset --hard origin/main
git checkout -B docs/autonomy-verify-final
echo "verify $(date -u)" > docs/autonomy-verify-final.md
git add docs/autonomy-verify-final.md
git commit -m "docs: verify full autonomy"
git push -u origin docs/autonomy-verify-final
gh pr create --base main --head docs/autonomy-verify-final \
  --title "docs: verify full autonomy" \
  --body "## Ziel\nVerify full GitHub autonomy after token + ruleset + settings fix.\n\n## Evidence\n- PR create: ✅\n- PR body: ✅\n- Branch: docs/autonomy-verify-final"
gh pr edit <number> --body "## Ziel\nVerified.\n\n## Ergebnis\nToken-Fix + Ruleset-Fix + Settings-Fix erfolgreich."
gh pr merge <number> --auto --squash
```

---

## Teil F: Anhang — Datenquellen

| Datenpunkt | Quelle | Zugriff |
| --- | --- | --- |
| Repo-Settings | `gh repo view --json ...` | ✅ |
| Ruleset | `gh api repos/.../rulesets/16636366` | ✅ |
| PR-Historie | `gh pr list --state all` | ✅ |
| Issues | `gh issue list` | ✅ |
| Labels | `gh label list` | ✅ |
| Actions/Workflows | `gh workflow list` | ✅ |
| Action Runs | `gh run list` | ✅ |
| Dependabot Alerts | `gh api .../dependabot/alerts` | ❌ 403 |
| Code Scanning Alerts | `gh api .../code-scanning/alerts` | ❌ 403 |
| Secret Scanning Alerts | `gh api .../secret-scanning/alerts` | ❌ 403 |
| Branch Protection | `gh api .../branches/main/protection` | ❌ 403 |
| Actions Permissions | `gh api .../actions/permissions` | ❌ 403 |
| Deploy Keys | `gh api .../keys` | ❌ 403 |
| PR Template | `gh api .../contents/.github/PULL_REQUEST_TEMPLATE.md` | ❌ 404 |
