# Git Push vom Hermes-Container zu GitHub

## Status (08.05.2026)

**✅ SSH-Key registriert.** Push funktioniert direkt vom Container.

### Voraussetzung: Git-User konfigurieren
```bash
git config --global user.name "Pascal Courbois"
git config --global user.email "u6288408171@gmail.com"
```

### Commit und Push
```bash
cd /opt/nexifyai-platform
git add -A
git commit -m "MESSAGE"
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_nexifyai -o StrictHostKeyChecking=no" git push origin main
```

### Wichtig: GitHub/Vercel Identity Mismatch
- **GitHub Org:** `nexifyai-dev`
- **Commit-Autor:** `Pascal Courbois <u6288408171@gmail.com>`
- **Vercel:** Separat verbunden, blockt Deployments von unverified Commits
- **Prüfung:** `git log --format='%an <%ae>' -3` zeigt aktuellen Commit-Autor
- **Fix bei Wechsel:** Immer `git config user.name` + `user.email` setzen vor Commit
```
~/.ssh/id_ed25519_nexifyai
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMQS7CU0K8Fe1tBh3rR2RwE0+dKL3043YKBNPTxZ6quM nexifyai@container
```

Der Key muss manuell auf GitHub registriert werden:
1. https://github.com/settings/keys
2. "New SSH Key" → Titel: "nexifyai-container-20260508"
3. Obigen Public Key einfügen → "Add SSH Key"

Danach funktioniert `git push` vom Container.

## Aktueller Workflow (bis Container-Key aktiv)

**Vom Container auf VPS kopieren und von dort pushen:**

```bash
# 1. Dateien auf VPS kopieren
scp -i /opt/data/ssh_keys/hermes_vps_key DATEIEN root@72.62.152.47:/opt/nexifyai-platform/

# 2. Auf VPS commiten + pushen
ssh -i /opt/data/ssh_keys/hermes_vps_key root@72.62.152.47 \
  "cd /opt/nexifyai-platform && git add -A && git commit -m 'MESSAGE' && git push origin main"
```

## GitHub PAT Alternative

Wenn ein GitHub Personal Access Token mit `repo`-Scope verfügbar ist:
```bash
git remote set-url origin https://TOKEN@github.com/nexifyai-dev/nexifyai-platform.git
git push origin main
```

## Repo
- **URL:** git@github.com:nexifyai-dev/nexifyai-platform.git
- **VPS Pfad:** /opt/nexifyai-platform
- **VPS SSH-Key:** git_nexifyai_key (authentifiziert als nexifyai-dev)
