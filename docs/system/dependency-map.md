# NeXifyAI — System Dependency Map
# Version: 1.0 | Stand: 2026-05-08 02:00 CEST
# Prinzip B: Vor jeder Aktivierung wird die Abhängigkeitskette validiert.

## Cron-Job Abhängigkeiten

### brain-sync (30 Min)
```
brain-sync.py
  ├── Qdrant (Port 6333) .................. ⚠️ Container-isoliert
  ├── Honcho (Brain Plugin) ............... ✅ via brain.db
  ├── Open Notebook (Port 32772) .......... ✅ erreichbar
  ├── DOS-v2.0.md .......................... ✅ /docs/DOS-v2.0.md
  └── brain.db .............................. ✅ /opt/data/brain/brain.db
Status: ⚠️ PARTIAL — Qdrant-Isolation bekannt, Fallback via SQLite aktiv
```

### event-tracking-check (04:00)
```
event-tracking-check.py
  ├── taxonomy.ts .......................... ✅ 18 Events definiert
  ├── Backend: POST /api/analytics/track ... ❌ EXISTIERT NICHT ← FLASCHENHALS
  ├── Supabase: analytics_events Tabelle ... ❌ Noch nicht erstellt
  └── lib/track.ts (Frontend) .............. ✅ Code existiert, nicht aktiviert
Status: ❌ BLOCKIERT — Wird durch P3-1 (Analytics-Route) entsperrt
```

### dos-compliance-check (06:00)
```
dos-compliance-check.py
  ├── DOS-v2.0.md .......................... ✅
  ├── Alle Pflichtverzeichnisse ............ ✅ docs/, packages/, etc.
  ├── OpenAPI-Spec .......................... ✅ ops/policies/openapi.json
  ├── CVE-Scanner (Trivy) .................. ✅ security-scan.yml
  └── Testabdeckung ......................... ✅ test.yml + 7 Tests
Status: ✅ BEREIT
```

### luecken-scan (08:00)
```
luecken-scan.py
  ├── Brain-Daten aktuell? ................. ✅ brain-sync läuft
  ├── Repo-Zugriff .......................... ✅
  └── DOS-v2.0.md als Referenz ............. ✅
Status: ✅ BEREIT
```

### health-score (stündlich)
```
health-score.py
  ├── Uptime (/proc/uptime) ................ ✅ Server-Kernel (shared)
  ├── Error-Rate (Backend-Logs) ............ ⚠️ Braucht Sentry/Error-Logging
  ├── Security (CVE-Scan) .................. ⚠️ Scan existiert, noch kein Ergebnis
  ├── Deploy-Frequency (Git) ............... ✅ Git-Log
  ├── MTTR (Incident-Log) .................. ⚠️ Noch keine Incidents
  ├── Conversion (Analytics) ............... ❌ Analytics-Route fehlt ← FLASCHENHALS
  └── Latenz (Health-Endpoint) ............. ✅ /api/health erreichbar
Status: ⚠️ DEGRADED — Conversion und Error-Rate blockieren >75%
```

## Kern-Abhängigkeitskette (Flaschenhals-Analyse)

```
POST /api/analytics/track (FEHLT)
  │
  ├──▶ lib/track.ts (kann nicht feuern)
  │      │
  │      └──▶ initTracking() in App.js (kein Effekt)
  │             │
  │             └──▶ Event-Datenstrom (0 Events/Stunde)
  │                    │
  │                    ├──▶ event-tracking-check.py (0 gefundene Events)
  │                    └──▶ health-score Conversion-Komponente (0%)
  │
  └──▶ shared/index.js track() (läuft ins Leere)
         │
         └──▶ Admin.js Analytics (keine Daten)
```

## Lösungspfad (Phase 3)

1. **Analytics-Route bauen** → Entsperrt lib/track.ts + event-tracking-check + health-score
2. **Supabase events-Tabelle** → Datenpersistenz für Analytics
3. **initTracking() aktivieren** → Datenstrom beginnt
4. **Health-Score neu berechnen** → Conversion + Error-Rate liefern echte Werte
