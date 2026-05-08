# Phase 2 — Schema-Review gegen Leitfassung Abschnitt 5

## Prüfmatrix: CRM Core Anforderungen

| Leitfassung | Tabelle | Status | Abweichung |
|-------------|---------|--------|------------|
| lead_ingest | conversations | ✅ | lead_score, lead_source, assigned_to |
| duplicate flow | lead_duplicates | ✅ | similarity, merged_into |
| auto_assignment | assignment_rules + Trigger | ✅ | conditions-based |
| staff kanban | kanban_columns + conversations.kanban_column | ✅ | workspace-scoped |
| applicant dashboard | conversations + tasks | ✅ | Filterbar nach assigned_to, kanban_column |
| task engine | tasks (erweitert) | ✅ | kanban_order, blocked_by, conversation_id |
| basic messaging | messages + attachments | ✅ | message_type, attachment_url, reactions |

## Fehlende Komponenten (nicht in Phase 2, für Phase 3+)

| Feature | Phase | Notiz |
|---------|-------|-------|
| lead scoring AI | 3 | ML-basierte Bewertung |
| email integration | 3 | IMAP → conversation |
| customer portal | 5 | Frontend |
| reporting | 5 | Analytics-Dashboard |

## Fazit
**Leitfassung Abschnitt 5 zu 100% abgedeckt.** Keine Schema-Lücken.
Phase 2 Tabellen 010-012 decken alle CRM-Core-Anforderungen.
