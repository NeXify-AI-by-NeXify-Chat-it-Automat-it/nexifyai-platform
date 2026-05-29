# ADR-030: Local Redis Cache Strategy

## Status
ACCEPTED · 2026-05-29

## Context
Das System betreibt mehrere Rate-Limiter, Event-Busse und Caching-Layer.
Bisher wurde `production-redis:6379` (Docker-Container) erwartet, aber nie deployed.
Oracle Engine lief im Fallback In-Memory Modus ohne Persistenz.

## Decision
Nutze den bestehenden **lokalen Redis** auf `127.0.0.1:6379`.
Kein Passwort (localhost-only, firewall-geschützt).
Kein Docker-Container — native Installation spart Ressourcen.

## Consequences
- ✅ Rate-Limiter persistent (kein In-Memory Fallback mehr)
- ✅ Geringer Memory-Footprint (~1MB)
- ✅ Kein zusätzlicher Docker-Container
- ⚠️ Kein HA/Replication — single-node (ausreichend für aktuelles Scale)
- ⚠️ Redis muss beim Boot starten (`systemctl enable redis-server`)
