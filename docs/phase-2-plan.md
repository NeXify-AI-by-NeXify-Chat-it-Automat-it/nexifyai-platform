# Phase 2 — CRM Core (Planung)

## Stand
- Leitfassung v1.0 Abschnitt 5
- Supabase-Fundament (Phase 1): 22+ Tabellen deployed

## Anforderungen lt. Leitfassung

| Feature | Beschreibung | Supabase-Tabellen |
|---------|-------------|-------------------|
| lead_ingest | Lead-Erfassung via Form/API/Webhook | conversations, messages |
| duplicate flow | Dublettenerkennung und Merge | conversations + profiles |
| auto_assignment | Automatische Zuweisung an Staff | tasks (assignee_id) |
| staff kanban | Kanban-Board für Lead-Bearbeitung | tasks (status workflow) |
| applicant dashboard | Dashboard für Leads/Kunden-Pipeline | conversations + tasks |
| task engine | Aufgaben-Management mit Workflows | tasks (vorhanden, erweitern) |
| basic messaging layer | Chat zwischen Staff und Kunden | messages (vorhanden, prüfen) |

## Schema-Erweiterungen (benötigt)

1. **conversations** → `lead_score` INT, `assigned_to` UUID (staff), `kanban_column` TEXT
2. **tasks** → `kanban_order` INT, `blocked_by` UUID[], `estimated_hours` NUMERIC
3. **Neue Tabelle `lead_duplicates`**: `id, lead_a, lead_b, similarity, merged`
4. **Neue Tabelle `kanban_columns`**: `id, name, order, color, workspace_id`

## RLS-Erweiterungen
- Portal-User: Nur eigene conversations/messages
- Staff: Alle conversations, eigene Tasks
- Admin: Vollzugriff

## Migrationen
- 010: lead_ingest extensions
- 011: kanban system
- 012: duplicate detection

## Nicht in dieser Phase
- Stripe (entfernt, durch Revolut ersetzt in Phase 4)
- Finance Core (Phase 4)
- Enterprise Security (Phase 7)

## Status: 📋 Planung — Implementierung nach Pascal-Freigabe
