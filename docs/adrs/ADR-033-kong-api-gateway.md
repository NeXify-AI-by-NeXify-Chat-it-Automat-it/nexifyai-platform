# ADR-033: Kong Gateway API-Management & Service-Routing
status: approved | date: 2026-05-29 | owner: goose

## Kontext
Das NeXify AI System hat mehrere interne Services (Brain API :8420, Oracle :8001, etc.),
die über ein einheitliches Gateway nach außen geroutet werden müssen.

## Entscheidung
**Kong Gateway 3.9** als zentraler API-Management-Layer auf Port 8000 (Proxy) und 8001 (Admin).

### Routenplan
| Route | Target | Methode | Auth |
|-------|--------|---------|------|
| /brain/* | Brain API (:8420) | GET,POST,PUT,DELETE | API-Key |
| /oracle/* | Oracle Engine (:8001) | GET,POST | X-Internal |
| /api/* | Backend (:8001) | GET,POST,PUT,DELETE | JWT |
| /health | Brain API (:8420/health) | GET | Public |

### Plugins (geplant)
- rate-limiting (100/min pro Consumer)
- key-auth (für externe API-Consumer)
- cors (für Frontend-Zugriff)
- prometheus (Metriken)

## Konsequenzen
- **Positiv:** Einheitlicher Entry-Point für alle externen Consumer
- **Positiv:** Security-Schicht vor internen Services
- **Risiko:** Kong als Single-Point-of-Failure
- **Mitigation:** Docker-Restart-Policy + Health-Override via Brain API

## Verweise
- ADR-026: Traefik Security
- Runtime Topology (docs/runtime-topology.md)