# ADR-026: Traefik Reverse-Proxy Security

**Status:** accepted
**Datum:** 2026-05-22
**Autor:** Security-Swarm
**Stakeholder:** DevOps, Security

## Kontext

Traefik läuft als zentraler Reverse-Proxy (Port 80/443) mit Dashboard auf Port 8080. Dashboard ist aktuell ungeschützt erreichbar.

## Entscheidung

**Traefik-Härtung:**
1. Dashboard mit Basic-Auth schützen (dynamic config)
2. IP-Allowlist für Dashboard (nur localhost + Tailscale-IPs)
3. TLS via Cloudflare Tunnel — kein direkter TLS-Termination an Traefik
4. Rate-Limiting für externe Routen
5. Header-Security (CSP, HSTS, X-Frame-Options)

## Dynamic Config (20-dashboard.yml)

```yaml
http:
  middlewares:
    dashboard-auth:
      basicAuth:
        users:
          - "admin:$2y$10$..."
    dashboard-ips:
      ipWhiteList:
        sourceRange:
          - "127.0.0.1/32"
          - "::1"
```

## Consequence

Dashboard nur noch mit gültigen Credentials erreichbar. Keine Info-Leaks mehr.
