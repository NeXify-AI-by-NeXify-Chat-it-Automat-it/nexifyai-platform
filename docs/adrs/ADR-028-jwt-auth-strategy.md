# ADR-028: JWT-Auth-Strategie

**Status:** accepted
**Datum:** 2026-05-22
**Autor:** Security-Swarm
**Stakeholder:** Security, Backend, AI-Team

## Kontext

3 Services benötigen Auth: OpenRouter (direct), Brain API, Traefik Dashboard. Kein Single-Sign-On bisher.

## Entscheidung

**Service-spezifische Auth-Strategie:**

| Service | Auth-Methode | Secret-Quelle |
|---------|-------------|---------------|
| OpenRouter (direct) | JWT (HS256) | JWT_SECRET in /root/.secrets/credentials.env |
| Brain API | JWT + API-Key | Gleicher JWT_POOL + API_KEY_SECRET |
| Traefik Dashboard | Basic-Auth | bcrypt-Hash in Traefik-Config |
| Supabase | GoTrue (RLS) | Built-in User Management |
| Admin-API-Proxy | Kein (localhost-only) | — |

## JWT-Flow (OpenRouter (direct))

```
Client → POST /api/auth/login {password} → {token}
Client → GET /api/providers (Authorization: Bearer {token}) → Providers
```

Token: HS256, 24h Gültigkeit, JWT_SECRET aus host env.

## Secret-Rotation

JWT_SECRET rotieren: Setzen auf neuen Wert → alle Tokens ungültig. Rotation alle 90 Tage.
