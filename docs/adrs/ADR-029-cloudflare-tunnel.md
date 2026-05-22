# ADR-029: Cloudflare Tunnel — Externer Zugriff

**Status:** accepted
**Datum:** 2026-05-22
**Autor:** Infra-Swarm
**Stakeholder:** DevOps, Security

## Kontext

Cloudflare Tunnel ist der einzige Internet-Exposure-Point. Alle externen Requests gehen durch Tunnel → lokale Services.

## Entscheidung

**Tunnel-Architektur:**

| Hostname | Ziel | Beschreibung |
|----------|------|-------------|
| webhook.nexifyai.cloud | :8011 | GitHub Webhook |
| brain.nexifyai.cloud | :8420 | Brain API (direkt) |
| traefik.nexifyai.cloud | :8080 | Traefik Dashboard |
| nexifyai.cloud | :8081 | Landing Page |
| *.nexifyai.cloud | :80 | Traefik Catch-All |

**Regeln:**
1. Remote Config hat Vorrang vor lokaler config.yml
2. brain.nexifyai.cloud geht direkt zu :8420 (umgeht Traefik)
3. nexifyai.cloud direkt zu :8081
4. 127.0.0.1 verwenden (nicht localhost) wegen IPv4/IPv6

**Rollback:**
`systemctl stop cloudflared` → nur interne Erreichbarkeit.
