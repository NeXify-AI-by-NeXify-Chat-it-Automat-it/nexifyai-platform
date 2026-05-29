# Grafana Dashboards — NeXifyAI Enterprise Brain v3

## UIDs

| Dashboard | UID | Status |
|-----------|-----|--------|
| AI Cost Tracking | `nexifyai-ai-cost-tracking` | ✅ 17 Panels |
| System Health | `nexifyai-system-health` | ✅ 19 Panels |
| Agent & Oracle Loop | `nexifyai-agent-oracle-performance` | ✅ 26 Panels |
| Performance | `nexifyai-performance` | 🆕 12 Panels |

## Import

1. Grafana UI (http://localhost:3000) → Create → Import
2. JSON-Datei hochladen
3. Prometheus-Datasource verknuepfen
4. Importieren

## Datenquellen

| Quelle | URL | Typ |
|--------|-----|-----|
| Prometheus | http://prometheus:9090 | Metrics |
| Loki | http://loki:3100 | Logs |
| Brain API | http://host.docker.internal:8420 | Custom |
