# OpenRouter UI Setup Runbook — CLI Token + MITM + Codex

## 1. Dashboard-Auth (erledigt ✅)

| Schritt | Status |
|:--------|:-------|
| `INITIAL_PASSWORD` entfernt | ✅ Docker Env sauber |
| Dashboard Login aktiv | ✅ Passwort persistent |
| **`Require API key`** | ✅ **SQLite gesetzt** (requireApiKey=true) |
| **API-Key in DB** | ✅ **`sk-e0e3a8077bfc75f7-k2i38t-c985b82d`** |
| `API_KEY_SECRET` in Docker Env | ✅ |

## 2. CLI Token

Tunnel zeigt: **"Local only: CLI token required"**

Das OpenRouter CLI Binary (`npm i -g OpenRouter@latest`) hat einen Befehl, der den CLI Token generiert. 
Der Token wird in der SQLite-DB gespeichert und ermöglicht lokale CLI-API-Zugriffe.

**Lösung (exakte Befehle):**

```bash
# Variante A: Dashboard UI (empfohlen, kein Secret-Leak)
# 1. Dashboard öffnen: https://openrouter.ai
# 2. Settings → CLI → "Generate CLI Token" klicken
# 3. Token wird im Dashboard angezeigt → in ~/.OpenRouter/auth/cli-secret speichern

# Variante B: CLI Binary (npm installiert)
cd /opt/nexify/repos/nexifyai-platform
OpenRouter --help  # Verfügbare CLI-Befehle prüfen
OpenRouter token --help  # Token-spezifische Hilfe
# Typisch: OpenRouter token generate > ~/.OpenRouter/auth/cli-secret

# Variante C: Nach der Dashboard-Generierung reicht oft
# docker restart OpenRouter-5afd-openrouter-1
```

Nach CLI-Token: **Dashboard → Tunnel → Activate**

## 3. MITM Proxy

OpenRouter Dashboard → **MITM Server** → **Start**

Erwartete /etc/hosts Einträge:
```
127.0.0.1 api.individual.githubcopilot.com
```

## 4. Codex CLI

Config-Datei: `~/.codex/config.toml` ✅ Bereits geschrieben
Auth-Datei: `~/.codex/auth.json` ✅ Bereits vorhanden

```toml
# ~/.codex/config.toml
model = "deepseek/deepseek-chat-v4"
model_provider = "OpenRouter"

[model_providers.OpenRouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
wire_api = "responses"

[agents.subagent]
model = "deepseek/deepseek-chat-v4"
```

## 5. Modelle konfigurieren (Dashboard UI)

OpenRouter Dashboard → **Model Mappings**:

| IDE-Modell | OpenRouter Ziel |
|------------|-------------|
| GPT-4o | `provider/model-id` (Pascal wählen) |
| GPT-4.1 | `provider/model-id` (Pascal wählen) |
| Claude Haiku 4.5 | `provider/model-id` (Pascal wählen) |

## 6. Finale Healthchecks

```bash
# Ohne Auth → 401/403
curl -i https://openrouter.ai/api/v1/models

# Mit Auth → 200
curl -i -H "Authorization: Bearer sk-e0e3a8077bfc75f7-k2i38t-c985b82d" \
  https://openrouter.ai/api/v1/models

# Dashboard nach Restart
docker restart OpenRouter-5afd-openrouter-1
# → Dashboard Login prüfen

# Health-Timer
systemctl enable --now nexify-OpenRouter-health.timer
```
