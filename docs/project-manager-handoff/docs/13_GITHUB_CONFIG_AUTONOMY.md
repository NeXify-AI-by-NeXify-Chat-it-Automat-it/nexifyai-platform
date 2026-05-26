# 13 - GitHub-Konfiguration für volle Agenten-Autonomie

> **Stand: 2026-05-26**
> Policies #11 (Repo Truth) und #12 (Autonomous Delivery) sind gemerged.
> Diese Policy dokumentiert die **technische GitHub-Konfiguration**, die für autonome Agenten-Arbeit nötig ist.

## 1. Token-Konfiguration (Fine-Grained PAT)

### Aktueller Status

| Aspekt | Wert |
| --- | --- |
| Account | `nexifyai-dev` |
| Token-Typ | Fine-Grained Personal Access Token |
| viewerPermission | `ADMIN` (Repo-Ebene) |
| PR-Erstellung | ❌ blockiert |
| Fehler | `Resource not accessible by personal access token (createPullRequest)` |
| Push | ✅ bypassed |
| Lesen (pr list, repo view) | ✅ funktioniert |

### Erforderliche Berechtigungen

Im GitHub UI unter `Settings → Developer settings → Personal access tokens → Fine-grained tokens` muss der Token `nexifyai-dev` folgende Repository-Permissions haben:

| Permission | Erforderlich | Aktuell |
| --- | --- | --- |
| **Contents** | Read and write | ✅ |
| **Pull requests** | **Read and write** | ❌ Read (oder nicht gesetzt) |
| **Metadata** | Read | ✅ |
| **Issues** | Read and write | ? |
| **Checks** | Read | ? |
| **Actions** | Read | ? |
| **Commit statuses** | Read | ? |

> **Kritisch:** Die Permission `Pull requests: Read and write` muss explizit gesetzt sein.
> Repo-Admin allein reicht nicht — der Fine-Grained PAT muss die Permission selbst haben.

### Korrekturschritt (GitHub UI)

```
1. GitHub → Settings (Profil oben rechts)
2. Developer settings (linke Navigation, ganz unten)
3. Personal access tokens → Fine-grained tokens
4. Token "nexifyai-dev" auswählen
5. Unter "Repository permissions" → "Pull requests":
   - Von "Read" auf "Read and write" ändern
6. "Save" klicken
7. Token neu ausrollen: gh auth login --with-token < token.txt
```

## 2. Ruleset-Konfiguration

### Aktuelles Ruleset "NeXify AI Plattform" (ID: 16636366)

| Eigenschaft | Wert |
| --- | --- |
| Enforcement | active |
| Anwendung | `~ALL` (alle Branches) |
| Ausschlüsse | keine |
| Regeln | deletion, code_scanning, required_linear_history, pull_request, code_quality |
| Bypass möglich | ✅ (aktueller User kann bypassen) |

### Problem

Das Ruleset erzwingt **Pull Requests für ALLE Branches**, inklusive `docs/*`-Branches.
Docs-only-Änderungen bräuchten eigentlich keinen PR-Zwang.

### Option A: docs/*-Branches ausnehmen (empfohlen)

Im GitHub UI unter `Repositories → nexifyai-platform → Settings → Rules → Rulesets → NeXify AI Plattform`:

```
Bedingungen:
  Ziel-Branches: ~ALL
  Ausgeschlossene Branches: refs/heads/docs/**
```

Dadurch können `docs/*`-Branches direkt gepusht werden ohne PR-Zwang.

### Option B: Ruleset nur auf main beschränken

```
Bedingungen:
  Ziel-Branches: refs/heads/main
  Ausgeschlossene Branches: (leer)
```

Dann gilt der PR-Zwang nur für `main`. Alle Feature-/Docs-Branches sind frei.

### Option C: Beibehalten + Agent nutzt Bypass

Der Agent hat `current_user_can_bypass: "always"`. Theoretisch kann er das Ruleset umgehen.
Der Fehler `createPullRequest` ist ein Token-Problem, kein Ruleset-Problem.

## 3. Repo-Einstellungen

### Aktuell

| Einstellung | Wert | Soll |
| --- | --- | --- |
| allow_merge_commit | null (false) | true |
| allow_squash_merge | null (false) | true |
| allow_rebase_merge | null (false) | true |
| allow_auto_merge | null (false) | true |
| delete_branch_on_merge | null (false) | true |
| allow_update_branch | null (false) | true |

### Korrektur (GitHub UI)

```
Repositories → nexifyai-platform → Settings → General → Pull Requests:
☑ Allow merge commits
☑ Allow squash merging
☐ Default commit message (oder PR title)
☑ Allow rebase merging
☑ Always suggest updating pull request branches
☑ Allow auto-merge
☑ Automatically delete head branches
```

## 4. Erwarteter Workflow nach Korrektur

```
Agent → Branch erstellen
      → Änderungen committen
      → Branch pushen (bypass oder ohne PR-Zwang bei docs/)
      → gh pr create (funktioniert nach Token-Fix)
      → gh pr edit --body "..." (funktioniert nach Token-Fix)
      → CI-Checks abwarten
      → Gates prüfen (Policy #12)
      → gh pr merge (bei Docs-only nach Gates)
      → Brain updaten
      → Status melden
```

## 5. Fehlerdiagnose-Tabelle

| Fehler | Ursache | Lösung |
| --- | --- | --- |
| `Resource not accessible ... (createPullRequest)` | Token hat keine `Pull requests: write` | Token-Permission korrigieren |
| `Bypassed rule violations ... merge commits` | Ruleset `required_linear_history` | Push von Branches mit Merge-Commit — Bypass funktioniert |
| `Cannot delete this branch` | Ruleset `deletion` | Bypass funktioniert |
| `Resource not accessible ... (update repo)` | Token hat keine `Contents: write` (oder kein `Administration`) | Für Repo-Settings braucht es Token mit Admin-Rechten |
| `Resource not accessible ... (update ruleset)` | Token hat keine Ruleset-Admin-Rechte | Ruleset im GitHub UI ändern (nicht per API) |

## 6. Token-Test-Befehle

Nach Token-Korrektur diese Befehle ausführen:

```bash
# Token-Auth prüfen
gh auth status

# PR erstellen (Test)
cd /opt/nexify/repos/nexifyai-platform
git checkout -B docs/autonomy-verify
echo "verify $(date)" > docs/autonomy-verify.md
git add docs/autonomy-verify.md
git commit -m "docs: verify autonomy"
git push -u origin docs/autonomy-verify
gh pr create --base main --head docs/autonomy-verify --title "docs: verify" --body "Verify autonomy."

# PR-Body editieren
gh pr edit <number> --body "Verified: PR create + body update funktioniert."

# Aufräumen
gh pr close <number>
git push origin --delete docs/autonomy-verify
```
