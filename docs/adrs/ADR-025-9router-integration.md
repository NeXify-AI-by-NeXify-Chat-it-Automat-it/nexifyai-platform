# ADR-025: 9Router AI Provider Gateway

**Status:** accepted
**Datum:** 2026-05-22
**Autor:** AI-Swarm
**Stakeholder:** AI Team, DevOps, Security

## Kontext

NeXifyAI benötigt einen zentralen API-Gateway für LLM-Provider (DeepSeek, OpenRouter, Anthropic, OpenAI, Vercel AI, Nscale). 9Router läuft als Docker-Container auf Port 20128.

## Entscheidung

**9Router als primärer AI-Router** — Lokal gehostet, Multi-Provider, JWT-gesichert.

## Architektur

```
┌───── Client ─────┐
│  Admin-Portal     │
│  Brain Service   │
│  CLI Tools       │
└────────┬─────────┘
         │ HTTPS
         ▼
┌─── Cloudflare Tunnel ────┐
│  ai-router.nexifyai.cloud│
└────────┬─────────────────┘
         │ localhost:20128
         ▼
┌─────── 9Router ─────────┐
│  /v1/chat/completions    │
│  /v1/models              │
│  /api/providers          │
│  /api/health             │
└────────┬─────────────────┘
    ┌────┼────┐
    ▼    ▼    ▼
 DeepSeek OpenRouter VercelAI
```

## Providers

| Provider | Status | Model Count |
|----------|--------|-------------|
| DeepSeek (ds/) | ✅ live | 10 |
| OpenRouter (openrouter/) | ✅ live | 35+ |
| OpenAI (openai/) | ✅ live | 8 |
| Anthropic (anthropic/) | ✅ live | 5 |
| Vercel AI Gateway | ✅ live | 73 |
| Nscale | ✅ live | 6 |
| LlamaLocal | ⚠️ eval | - |

## Auth

JWT-Auth via `Authorization: Bearer <token>`. Login: `POST /api/auth/login`.
