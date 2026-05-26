# 14 — GitHub App Automation (NeXify AI GitHub Automation)

> **Stand: 2026-05-26**
> Ersetzt PAT-basierte GitHub-Autonomie durch eine dedizierte GitHub App
> für Goose, Projektleiter und Automationen.

---

## 1. Warum GitHub App statt PAT

| Kriterium | PAT (Fine-Grained) | GitHub App |
| --- | --- | --- |
| **Identität** | An User `nexifyai-dev` gebunden | Eigene App-Identität |
| **Token-Typ** | Langzeit-PAT, manuelle Rotation | Installation Token, automatisch rotiert (1h) |
| **Auth-Konflikt** | `GH_TOKEN` kann `hosts.yml` überschreiben | Kein Konflikt — Token pro Aufruf |
| **Audit** | Nur "User X hat Aktion ausgeführt" | "App Y hat Aktion ausgeführt" — klar trennbar |
| **Rechteverwaltung** | Im User-Settings versteckt | In Org-Einstellungen, zentral |
| **Mehrere Umgebungen** | Ein Token pro User — Verwechslungsgefahr | App pro Umgebung (dev/staging/prod) |
| **Sicherheit** | Bei Leak: voller Zugriff bis Rotation | Bei Leak: Token in < 1h abgelaufen |
| **Org-Installation** | Nur Repos, die User sieht | Auf ganze Organisation installierbar |
| **Kundenrepo-Trennung** | Nicht klar auditierbar | App-Instanzen trennbar |
| **Rotation** | Manuell im GitHub UI | Automatisch pro API-Call |
| **Bypass Ruleset** | Nur wenn User Bypass hat | App kann explizit in Bypass-Liste |

**Entscheidung:** Die Organisation `NeXify-AI-by-NeXify-Chat-it-Automat-it` bekommt eine eigene GitHub App. PATs werden nur noch als dokumentierter Notfall-Fallback verwendet.

---

## 2. App-Definition

| Feld | Wert |
| --- | --- |
| **App-Name** | `NeXify AI GitHub Automation` |
| **Organisation** | `NeXify-AI-by-NeXify-Chat-it-Automat-it` |
| **Homepage URL** | `https://github.com/NeXify-AI-by-NeXify-Chat-it-Automat-it/nexifyai-platform` |
| **User Authorization** | nicht benötigt (App-only, keine User-Impersonation) |
| **Webhook** | deaktiviert (keine Event-Verarbeitung nötig) |
| **Installationsumfang** | Zuerst nur `nexifyai-platform`, später klassifizierte Kunden-Repos |

---

## 3. Repository Permissions

### Write-Permissions (aktiv genutzt)

| Permission | Begründung |
| --- | --- |
| **Contents: Read and write** | Push auf Feature/Docs/Policy-Branches |
| **Pull requests: Read and write** | PR erstellen, editieren, mergen, Labels setzen |
| **Issues: Read and write** | Issues erstellen, Labels setzen, schließen |

### Read-Permissions (Monitoring & Audit)

| Permission | Begründung |
| --- | --- |
| **Metadata: Read** | Repo-Infos, Visibility, Default Branch |
| **Checks: Read** | CI/CD-Status abrufen, Merge-Gates prüfen |
| **Actions: Read** | Workflow-Runs einsehen |
| **Commit statuses: Read** | Commit-Status abrufen |

### Security-Read-Permissions (GHAS)

| Permission | Begründung |
| --- | --- |
| **Dependabot alerts: Read** | Alerts klassifizieren und priorisieren |
| **Code scanning alerts: Read** | CodeQL/Trivy-Findings auswerten |
| **Secret scanning alerts: Read** | Echte Secrets erkennen und rotieren |

### Administration: Read (nur bei Bedarf)

| Permission | Begründung | Aktiv? |
| --- | --- | --- |
| **Administration: Read** | Repo-Settings, Branch-Protection lesen | Bei Audit |
| **Administration: Write** | Rulesets, Repo-Settings, Security-Konfiguration ändern | **Nur im P0-Admin-Modus** |

> **Regel:** Administration: Write wird **nicht** standardmäßig aktiviert. Wenn ein Agent / Goose Repo-Settings, Rulesets oder Security-Konfiguration ändern muss, wird ein separater **Admin-Modus-PR** erstellt, dokumentiert und nach expliziter Freigabe ausgeführt.

---

## 4. Installation

### Schritt 1: GitHub App erstellen

```
GitHub → Organisation NeXify-AI-by-NeXify-Chat-it-Automat-it → Settings
→ Developer settings → GitHub Apps → New GitHub App

App name:             NeXify AI GitHub Automation
Homepage URL:         https://github.com/.../nexifyai-platform
Description:          Automation App für Goose, Projektleiter und CI/CD

Repository permissions:
  Actions:              Read
  Administration:       Read (Write nur bei Bedarf)
  Checks:               Read
  Commit statuses:      Read
  Contents:             Read and write
  Dependabot alerts:    Read
  Code scanning alerts: Read
  Secret scanning alerts: Read
  Issues:               Read and write
  Metadata:             Read
  Pull requests:        Read and write

Webhook:               Active (false) — kein Haken
Subscribe to events:   (none)

Where can this app be installed:
☑ Only on this organization
```

### Schritt 2: Private Key generieren & speichern

Nach App-Erstellung:

```
GitHub App Settings → Generate a private key
→ Lädt `ne-xify-ai-github-automation.2026-05-26.private-key.pem` herunter
```

**Speicherort auf dem VDS:**

```
/opt/nexify/secrets/github-app/private-key.pem
```

**Zugriffsschutz:**

```bash
chmod 600 /opt/nexify/secrets/github-app/private-key.pem
chown root:root /opt/nexify/secrets/github-app/private-key.pem
```

**Niemals:**
- Private Key ins Repo committen
- Private Key in Logs ausgeben
- Private Key in Env-Variablen (nur via Datei-Referenz)

### Schritt 3: App ID & Installation ID speichern

```
/opt/nexify/secrets/github-app/app-id         (enthält nur die App-ID-Zahl)
/opt/nexify/secrets/github-app/installation-id (enthält nur die Installations-ID-Zahl)
```

Oder in einer EnvironmentFile:

```
/opt/nexify/secrets/github-app/env
→ GITHUB_APP_ID=123456
→ GITHUB_APP_INSTALLATION_ID=987654
```

### Schritt 4: App auf Organisation installieren

```
GitHub App Settings → Install App → Install
→ Only select repositories → nexifyai-platform
→ Install
```

Die Installation erzeugt eine `installation_id`. Diese Nummer notieren und in `env` speichern.

---

## 5. Token-Helper-Script

```bash
#!/bin/bash
# /opt/nexify/github-app-token/get-installation-token.sh
# Gibt einen kurzlebigen GitHub Installation Token aus (STDOUT)
# Keine Secrets im Output außer dem Token selbst

set -euo pipefail

APP_ID="$(cat /opt/nexify/secrets/github-app/app-id)"
INSTALLATION_ID="$(cat /opt/nexify/secrets/github-app/installation-id)"
PRIVATE_KEY_PATH="/opt/nexify/secrets/github-app/private-key.pem"

# JWT erzeugen (Ablauf: 5 Minuten)
NOW=$(date +%s)
JWT_HEADER=$(echo -n '{"alg":"RS256","typ":"JWT"}' | base64 -w0 | tr '+/' '-_' | tr -d '=')
JWT_PAYLOAD=$(echo -n "{\"iat\":$((NOW - 60)),\"exp\":$((NOW + 300)),\"iss\":\"${APP_ID}\"}" | base64 -w0 | tr '+/' '-_' | tr -d '=')

# Signatur erzeugen
JWT_SIGNATURE=$(echo -n "${JWT_HEADER}.${JWT_PAYLOAD}" \
  | openssl dgst -sha256 -sign "${PRIVATE_KEY_PATH}" \
  | base64 -w0 | tr '+/' '-_' | tr -d '=')

JWT="${JWT_HEADER}.${JWT_PAYLOAD}.${JWT_SIGNATURE}"

# Installation Token abrufen
TOKEN=$(curl -s -X POST \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "${TOKEN}"
```

**Zugriffsschutz:**

```bash
chmod 700 /opt/nexify/github-app-token/
chmod 500 /opt/nexify/github-app-token/get-installation-token.sh
chown root:root /opt/nexify/github-app-token/
```

### Abhängigkeiten prüfen

```bash
# Auf dem VDS installieren falls fehlend:
which openssl           # OpenSSL für JWT-Signatur
which curl              # HTTP-Client
which python3           # JSON-Parsing
```

---

## 6. gh CLI auf App-Token umstellen

### Option A: GH_TOKEN pro Befehl (empfohlen für erste Phase)

```bash
GH_TOKEN="$(/opt/nexify/github-app-token/get-installation-token.sh)" gh pr create ...
GH_TOKEN="$(/opt/nexify/github-app-token/get-installation-token.sh)" gh label create ...
```

### Option B: Shortcut-Script (für häufige Nutzung)

```bash
#!/bin/bash
# /usr/local/bin/gh-app
GH_TOKEN="$(/opt/nexify/github-app-token/get-installation-token.sh)" /usr/bin/gh "$@"
```

```bash
chmod +x /usr/local/bin/gh-app
# Nutzung:
gh-app pr create --base main --head docs/test --title "Test" --body "Test"
```

### Option C: .bashrc-Alias (für interactive Shell)

```bash
alias gh='GH_TOKEN="$(/opt/nexify/github-app-token/get-installation-token.sh)" gh'
```

> **Nicht empfohlen:** Der Alias erschwert Debugging und verlangsamt jeden `gh`-Aufruf um ~1 Sekunde.

---

## 7. Goose Runtime-Integration

### Environment-Variablen (kein statischer PAT)

```
# Statt: GH_TOKEN=github_pat_...
# Neu: GITHUB_APP_ID=123456
#       GITHUB_APP_INSTALLATION_ID=987654
#       GITHUB_APP_PRIVATE_KEY_PATH=/opt/nexify/secrets/github-app/private-key.pem
```

### Integration in execute_typescript / SDK

Die SDK-Funktionen nutzen den GitHub-Connector (der bereits funktioniert). Die `gh` CLI wird nur für Operationen genutzt, die per SDK nicht abbildbar sind. Dafür reicht das Token-Helper-Script.

---

## 8. Token-Rotation

### Automatisch

GitHub Installation Tokens laufen nach **1 Stunde** ab. Ein neuer Aufruf von `get-installation-token.sh` erzeugt automatisch einen frischen Token.

### Private Key Rotation (selten)

```
1. GitHub App Settings → Generate new private key
2. Neue .pem-Datei nach /opt/nexify/secrets/github-app/private-key.pem
3. chmod 600
4. Alte .pem-Datei sicher löschen (shred)
5. Test: /opt/nexify/github-app-token/get-installation-token.sh
```

### App Secret Rotation (nie nötig)

GitHub Apps haben kein App Secret im herkömmlichen Sinn. Die Authentifizierung erfolgt via Private Key + JWT + Installation Token.

---

## 9. Audit Logs

### GitHub Audit Log

```
GitHub → Organisation Settings → Audit log
Filter: "app:ne-xify-ai-github-automation"
```

Sichtbar:
- Welche Aktionen die App ausgeführt hat
- Welche Repos betroffen waren
- Welche Permissions genutzt wurden
- Zeitstempel, IP, Actor

### VDS Audit

```
/var/log/gh-app-audit.log (optional)
→ Zeile pro Token-Erzeugung
→ Kein Token, keine Secrets
→ Nur: timestamp, app_id, installation_id, exit_code
```

---

## 10. Fallback-Regel

| Szenario | Aktion |
| --- | --- |
| App-Token-Erzeugung schlägt fehl | Fehler dokumentieren, Ursache analysieren |
| Private Key korrupt | Rotieren, App neu authorisieren |
| Installation entfernt | Neu installieren, installation_id updaten |
| App deaktiviert | In Org-Settings reaktivieren |
| Kurzzeitiger API-Fehler | Retry nach 5 Sekunden |
| Kein Fallback auf PAT | **Nur** mit dokumentierter Notfall-Freigabe |

> **Regel:** Ein Fine-Grained PAT wird **nicht** als Fallback vorgehalten. Wenn die GitHub App nicht funktioniert, wird das System gestoppt, bis die App wieder funktioniert. Ein PAT als "quick fix" untergräbt die gesamte App-Architektur.

---

## 11. Testplan

Nach App-Installation:

```bash
# 1. Token-Helper testen
TOKEN=$(/opt/nexify/github-app-token/get-installation-token.sh)
echo "Token erhalten: ${#TOKEN} Zeichen"

# 2. PR erstellen
cd /opt/nexify/repos/nexifyai-platform
git checkout main && git reset --hard origin/main
git checkout -B docs/github-app-test
echo "gh-app-test $(date)" > docs/github-app-test.md
git add docs/github-app-test.md
git commit -m "docs: test github app"
git push -u origin docs/github-app-test

GH_TOKEN="$TOKEN" gh pr create \
  --base main --head docs/github-app-test \
  --title "docs: test github app" \
  --body "Test der GitHub App Automation." \
  --label governance

GH_TOKEN="$TOKEN" gh pr edit docs/github-app-test --body "## Ziel\nTest GitHub App.\n\n## Ergebnis\n✅ PR create, edit, label funktionieren."

GH_TOKEN="$TOKEN" gh pr view --json number,title,state,body,labels

# 3. Label testen
GH_TOKEN="$TOKEN" gh label create gov-app-test --color 0e8a16 --description "Test"

# 4. Aufräumen
GH_TOKEN="$TOKEN" gh label delete gov-app-test --yes
GH_TOKEN="$TOKEN" gh pr close docs/github-app-test
GH_TOKEN="$TOKEN" gh pr delete docs/github-app-test
git push origin --delete docs/github-app-test
```

### Test-Kriterien

| Test | Erwartung |
| --- | --- |
| Token-Erzeugung | Token string (kein Error) |
| `gh pr create` | PR # wird erstellt |
| `gh pr edit` | Body aktualisiert |
| `gh pr view` | Labels sichtbar |
| `gh label create` | Label existiert |
| `gh label delete` | Label entfernt |
| `gh api dependabot/alerts` | Alerts lesbar (ggf. leer) |
| `gh api code-scanning/alerts` | Alerts lesbar (ggf. leer) |
| `gh api secret-scanning/alerts` | Alerts lesbar (ggf. leer) |

---

## 12. Migrationsplan: Vom PAT zur GitHub App

### Phase 1 (heute)

```
- GitHub App erstellen
- Private Key sichern
- Token-Helper bauen
- gh CLI testen → PR create, edit, label, security alerts
- Policy #14 committen und mergen
```

### Phase 2 (nach App-Test)

```
- Goose Runtime auf App-Token umstellen
- GH_TOKEN aus allen Konfigurationen entfernen
- hosts.yml-PAT nicht mehr nutzen
- ~/.config/gh/hosts.yml leeren oder auf App-Token umstellen
- Audit: alle Automationen laufen über App
```

### Phase 3 (stabiler Betrieb)

```
- Kunden-Repos klassifizieren
- App auf Kunden-Repos ausweiten (nach Classification)
- GitHub Connector (SDK) prüfen, ob er App-Token nutzen kann
- PATs in der Organisation identifizieren und rotieren/entfernen
```

---

## 13. Zusammenfassung der Berechtigungen

| Permission | Wert | Grund |
| --- | --- | --- |
| Contents | **Read and write** | Branches pushen, Dateien schreiben |
| Pull requests | **Read and write** | PRs erstellen, editieren, mergen |
| Issues | **Read and write** | Issues und Labels verwalten |
| Metadata | Read | Repo-Infos |
| Checks | Read | CI/CD-Status |
| Actions | Read | Workflow-Runs |
| Commit statuses | Read | Commit-Status |
| Dependabot alerts | Read | Security Monitoring |
| Code scanning alerts | Read | CodeQL/Trivy-Auswertung |
| Secret scanning alerts | Read | Secret-Erkennung |
| Administration | **Read** | Repo-Settings lesen |
| Administration (Write) | **NUR bei dokumentiertem P0-Fall** | Settings/Rulesets ändern |

---

## 14. Abhängigkeiten auf dem VDS

| Paket | Prüfbefehl | Fehlt? |
| --- | --- | --- |
| openssl | `which openssl` | Install: `apt install openssl` |
| curl | `which curl` | Install: `apt install curl` |
| python3 | `which python3` | Install: `apt install python3` |
| gh | `which gh` | Install: `apt install gh` (GitHub CLI) |

**Verzeichnisstruktur nach Setup:**

```
/opt/nexify/
├── github-app-token/
│   └── get-installation-token.sh   (500 root:root)
└── secrets/
    └── github-app/
        ├── private-key.pem          (600 root:root)
        ├── app-id                   (600 root:root)
        └── installation-id          (600 root:root)
```
