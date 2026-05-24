# NeXifyAI Auth-Flow Dokumentation

**Stand:** 2026-05-22
**Status:** Active

## Übersicht

NeXifyAI verwendet eine mehrschichtige Auth-Strategie mit dienstspezifischen Methoden:

```
┌──────────────────────────────────────────────┐
│              EXTERNAL REQUESTS                │
│  (Cloudflare Tunnel → 127.0.0.1 Services)     │
└────────────┬─────────────────────────────────┘
             │
    ┌────────┼────────┬──────────────┐
    ▼        ▼        ▼              ▼
┌───────┐ ┌──────┐ ┌──────┐  ┌──────────┐
│9Router│ │Brain │ │Traef │  │Admin-Pro │
│ JWT   │ │ JWT  │ │Basic │  │ localhost│
└───────┘ └──────┘ └──────┘  └──────────┘
```

## 1. 9Router — JWT Auth

### Login-Flow

```
POST /api/auth/login
Content-Type: application/json

{"password": "<INITIAL_PASSWORD>"}

Response 200:
{"token": "eyJhbGciOiJIUzI1NiIs...", "expires": "2026-05-23T16:42:00Z"}
```

### Authentifizierte Requests

```
GET /api/providers
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response 200:
{"providers": [...]}
```

### Token-Konfiguration

| Parameter | Wert |
|-----------|------|
| Algorithmus | HS256 |
| Secret-Quelle | `JWT_SECRET` in `/root/.secrets/credentials.env` |
| Gültigkeit | 24 Stunden |
| Rotation | Alle 90 Tage |

### Secret-Rotation (9Router JWT)

```bash
# 1. Neuen Secret generieren
openssl rand -hex 32

# 2. In /root/.secrets/credentials.env aktualisieren
JWT_SECRET=<neuer-secret>

# 3. 9Router neu starten
docker restart 9router-5afd-niner-router-1

# 4. Verifizieren
curl -X POST http://localhost:20128/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password":"<INITIAL_PASSWORD>"}'
```

## 2. Brain API — JWT + API-Key

### Status

| Endpoint | Auth | Status |
|----------|------|--------|
| `/health` | Kein | ✅ live |
| `/system/status` | JWT | 🔜 TODO |
| `/api/v2/*` | JWT | ✅ live |

### Request-Beispiel

```
GET http://localhost:8420/system/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## 3. Traefik Dashboard — Basic-Auth

### Konfiguration

**File:** `traefik/dynamic/20-dashboard.yml`

```yaml
http:
  middlewares:
    dashboard-auth:
      basicAuth:
        users:
          - "admin:$2y$10$hashedPassword"
    dashboard-ips:
      ipWhiteList:
        sourceRange:
          - "127.0.0.1/32"
          - "100.64.0.0/10"  # Tailscale
  routers:
    dashboard:
      rule: "Host(`traefik.nexifyai.cloud`)"
      middlewares:
        - dashboard-auth
        - dashboard-ips
```

### Passwort-Hash generieren

```bash
htpasswd -nbB admin "<password>"
```

## 4. Supabase — GoTrue + RLS

### Auth-Architektur

```
┌──────────────────────┐
│    Supabase Client    │
│  (Admin / App)        │
└────────┬─────────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
┌──────┐ ┌──────┐ ┌──────┐
│ Anon │ │Servic│ │Admin │
│ Key  │ │Role  │ │Key   │
└──┬───┘ └──┬───┘ └──┬───┘
   ▼       ▼       ▼
┌──────────────────────┐
│   Row-Level-Security  │
│   (RLS-Policies)      │
└──────────────────────┘
```

### Keys

| Key-Typ | Verwendung | Zugriff |
|---------|-----------|--------|
| `anon` (VITE_SUPABASE_ANON_KEY) | Client-seitig (Frontend) | Nur via RLS-Policies |
| `service_role` (SUPABASE_SERVICE_ROLE_KEY) | Backend (Admin-API) | Bypass RLS, Vollzugriff |
| `JWT_SECRET` | Token-Signierung | GoTrue intern |

### RLS-Policy-Beispiel

```sql
CREATE POLICY "Users can read own data"
  ON profiles
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can read all"
  ON profiles
  FOR SELECT
  USING (is_staff());
```

### Secret-Rotation (Supabase)

```bash
# 1. Neuen JWT-Secret in Supabase Dashboard setzen
# Settings → Auth → JWT Secret

# 2. Neue API-Keys generieren
# Settings → API → Generate New Keys

# 3. /root/.secrets/credentials.env aktualisieren
SUPABASE_ANON_KEY=<neuer-key>
SUPABASE_SERVICE_ROLE_KEY=<neuer-key>
```

## 5. Host-Level Secrets

### Struktur

```
/root/.secrets/
  credentials.env        (chmod 600)
  credentials.env.gpg    (GPG-encrypted backup)
```

### Variablen

```bash
# /root/.secrets/credentials.env
JWT_SECRET=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
VITE_AI_API_KEY=...
INITIAL_PASSWORD=...
API_KEY_SECRET=...
MACHINE_ID_SALT=...
OPENROUTER_API_KEY=...
DEEPSEEK_API_KEY=...
ANTHROPIC_API_KEY=...
VERCEL_AI_GATEWAY_KEY=...
NSCALE_API_KEY=...
```

### Sichere Verwendung

```bash
# NIE direkt im Code
source /root/.secrets/credentials.env

# NIE in Git
# /root/.secrets/ ist in .gitignore

# Backup
/root/backups/credentials-backup-$(date +%Y%m%d).env.gpg
```

## 6. Incident-Response — Secret-Leak

1. **Leak identifizieren** — Welcher Secret wurde exponiert?
2. **Rotieren** — neuen Secret generieren, alle Instanzen aktualisieren
3. **Revoken** — alten Token ungültig machen
4. **Audit-Log prüfen** — Hat jemand den Token missbraucht?
5. **Root-Cause-Analyse** — Wie kam der Secret ins Repo?
6. **RCA dokumentieren** → `/root/sicher-repo/docs/incidents/`
