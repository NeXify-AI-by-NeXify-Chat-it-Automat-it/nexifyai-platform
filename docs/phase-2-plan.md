# Phase 2 — CRM Core (Planung → Umsetzung)

## Status: 🔄 In Umsetzung

| Meilenstein | Status | Migration | 
|-------------|--------|-----------|
| lead_ingest extensions | 🔄 | 010 |
| duplicate detection | 📋 | 010 |
| kanban system | 📋 | 010 |
| auto_assignment | 📋 | folgt |
| basic messaging layer | ✅ | 006 (vorhanden) |
| task engine | ✅ | 006+010 (vorhanden) |

## Dependency Map

```
Phase 2 CRM Core
  ├── conversations (006) → lead_score, assigned_to, kanban_column
  ├── tasks (006) → kanban_order, blocked_by, conversation_id
  ├── profiles (001) → auto_assignment lookup
  ├── workspaces (002) → kanban_columns workspace scope
  └── NEU: lead_duplicates, kanban_columns
```

## Nächste Schritte (autonom)
1. Migration 010 auf Supabase ausführen
2. Migration 011: messaging extensions (reactions, attachments)
3. Migration 012: auto_assignment rules table
4. Autopilot-Tasks für Testing generieren

## Leitfassung-Konformität
- lead_ingest ✅ conversations + lead_score
- duplicate flow ✅ lead_duplicates mit similarity
- auto_assignment ✅ conversations.assigned_to
- staff kanban ✅ kanban_columns + tasks.kanban_order
- applicant dashboard 📋 Frontend (Phase 5)
- task engine ✅ tasks (erweitert)
- basic messaging ✅ messages (vorhanden)
