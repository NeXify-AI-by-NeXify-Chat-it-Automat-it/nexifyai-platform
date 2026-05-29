# ADR-E1: Health v3 — Topology-Aware Multi-Perspective Health

**Status:** accepted  
**Datum:** 2026-05-08  
**Decider:** NeXifyAI (Hermes Lead Agent)  
**Consulted:** Pascal Courbois (CEO)  
**Depends on:** ADR-005 (Automation Layer), ADR-007 (Observability)  

---

## Kontext

### Evolution der Health-Architektur

| Version | Modell | Problem |
|---------|--------|---------|
| **v1** (implizit) | Binary: `alive=true/false` | Keine Diagnose. "Läuft oder läuft nicht" |
| **v2** (heute) | Component-scored: 10 Komponenten, gewichteter Score | Misst aus EINER Perspektive (Observer=Container). `qdrant":"down"` obwohl Qdrant auf VPS läuft |
| **v3** (E1-Design) | Topology-aware: Multi-Observer, Layer-Diagnose | Erklärt WARUM ein Dienst aus welcher Perspektive nicht erreichbar ist |

### Das Problem

Das heutige VPS-Debug bewies:

```
Canonical Runtime ≠ Observed Runtime
```

Nicht wegen Service-Ausfall. Sondern weil:
- Der Hermes-Container `localhost:6333` nicht erreichen kann (Qdrant auf 127.0.0.1 gebunden)
- Redis KEINEN Host-Port hat (nur innerhalb `honcho_honcho-network`)
- Backend als systemd-Service läuft (nicht Docker → Container kann `localhost:8001` nicht erreichen)

Health v2 meldet diese Dienste als "down", obwohl sie LAUFEN. Das ist eine False-Positive-Diagnose durch Netzwerk-Isolation.

---

## Entscheidung

**Health v3 wird Topology-Aware.** Nicht mehr "Ist Dienst X erreichbar?" sondern "Aus welcher Perspektive ist Dienst X erreichbar, und warum nicht?"

### Architektur

```
                    ┌──────────────────────────┐
                    │     HEALTH v3 ENGINE      │
                    │  topology_probe.py        │
                    └────────────┬─────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
    ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
    │ Observer:     │   │ Observer:     │   │ Observer:     │
    │ HERMES-CONT.  │   │ VPS-HOST      │   │ EXTERNAL      │
    │ (Container)   │   │ (SSH/systemd) │   │ (Internet)    │
    └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   TOPOLOGY LAYER DIAG   │
                    │   service/network/port  │
                    │   dns/firewall/proxy    │
                    └─────────────────────────┘
```

### Output-Struktur (Health v3)

```json
{
  "status": "critical",
  "score": 37,
  "timestamp": "...",
  "observers": {
    "hermes-container": {
      "reachable": ["supabase", "open_notebook", "paperclip"],
      "unreachable": [
        {
          "target": "qdrant",
          "canonical": "host.docker.internal:6333",
          "observed": "connection_refused",
          "layer": "docker-network",
          "diagnosis": "Qdrant läuft auf VPS, aber Port-Bindung ist 127.0.0.1 (host-local only)",
          "recovery": "Qdrant-Port auf 0.0.0.0:6333 ändern ODER qdrant-vjfp-qdrant-1:6333 nutzen",
          "service_actually_running": true
        }
      ]
    },
    "vps-host": {
      "reachable": ["backend", "qdrant", "supabase"],
      "unreachable": [
        {
          "target": "redis",
          "canonical": "localhost:6379",
          "observed": "connection_refused",
          "layer": "port-binding",
          "diagnosis": "Redis hat kein Host-Port-Mapping. Nur innerhalb honcho_honcho-network erreichbar.",
          "recovery": "docker run -p 6379:6379 redis ODER direkt auf honcho-redis-1:6379 zugreifen",
          "service_actually_running": true
        }
      ]
    },
    "external": {
      "reachable": ["backend", "traefik"],
      "unreachable": []
    }
  },
  "topology_summary": {
    "total_services": 8,
    "running_services": 8,
    "false_positive_downs": 3,
    "false_positive_services": ["qdrant", "redis", "backend"],
    "root_cause": "Docker network isolation + port binding policy"
  }
}
```

### Vier Wahrheiten pro Dienst

Jeder Dienst hat jetzt vier explizite Zustände:

| Ebene | Bedeutung | Beispiel |
|-------|-----------|----------|
| **Canonical** | Läuft der Dienst? | `systemctl is-active` / `docker ps` |
| **Observed** | Erreichbar von diesem Observer? | TCP/HTTP-Probe |
| **Projected** | Was meldet Health v2? | `qdrant: down` (False-Positive) |
| **Recoverable** | Wie wird Erreichbarkeit hergestellt? | Port-Mapping ändern, Netzwerk-Brücke |

---

## Konsequenzen

### Positiv
- **Keine False-Positive-Downs mehr** — Health erklärt, WARUM ein Dienst "unreachable" ist, nicht nur DASS
- **Multi-Observer** — Unterschiedliche Perspektiven decken Netzwerk-Isolation auf
- **Layer-Diagnose** — Unterscheidet Service-Ausfall von Netzwerk-Isolation von Port-Bindung von DNS
- **Recovery-Pfade** — Jeder "unreachable"-Status hat konkreten Recovery-Befehl
- **Production Honesty bleibt** — System beschönigt nicht, erklärt aber präzise

### Negativ
- Komplexität steigt (4 Observer × 8 Dienste = 32 Probes)
- SSH-Abhängigkeit für VPS-Host-Perspektive
- Health-Endpoint wird langsamer (mehrere Probes)

### Neutral
- `/api/health/v2` bleibt als einfacher Einstieg erhalten
- `/api/health/v3` wird neuer Endpunkt mit voller Topologie
- v2 und v3 laufen parallel, v2 als Fallback

---

## Implementierungs-Plan

### E1 (JETZT) — Topology Inventory + Probe
- [x] `/docs/runtime-topology.md` — alle Dienste, Endpoints, Netzwerke
- [x] `backend/diagnostics/topology_probe.py` — Multi-Perspective Probe Engine
- [ ] `/api/health/v3` — neuer Endpoint (nach Infra-Fixes)

### E2 (NACH INFRA-FIXES) — Shared Cache
- Redis-basierter Health-Cache (cross-worker, cross-container)
- TTL 15s, invalidierung bei Service-Restart

### E5 (SPÄTER) — Failure Injection
- Health v3 als Basis für Chaos-Experimente
- "Was passiert wenn Qdrant-Port auf 127.0.0.1 gebunden bleibt?"
- Automatische Recovery-Validierung

---

## Referenzen

- `/docs/runtime-topology.md` — Topology Inventory
- `backend/diagnostics/topology_probe.py` — Probe Engine
- `backend/routes/health_v2_routes.py` — Health v2 (bestehend)
- VPS-Debug-Session 08.05.2026 — Discovery: Canonical ≠ Observed
