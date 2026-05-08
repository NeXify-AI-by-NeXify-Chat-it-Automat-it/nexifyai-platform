# NeXifyAI Supabase Quickstarts — Index

## Offizielle Quickstarts (geprüft)

| Quickstart | Status | Migration | Notiz |
|-----------|--------|-----------|-------|
| User Management Starter | ✅ Abgedeckt | 001 | profiles + organizations |
| Todo List | ✅ Abgedeckt | 006 | tasks + RLS |
| Slack Clone | ✅ Geprüft | 006 | conversations/messages RLS abgeglichen |
| Stripe Subscriptions | ❌ Entfernt | — | Ersetzt durch Revolut Business |
| NextAuth Schema | ❌ Nicht benötigt | — | Supabase GoTrue reicht |
| OpenAI Vector Search | ⏸️ Vorgemerkt | — | Qdrant primär, Supabase-Fallback für Volltext |
| LangChain | ⏸️ Evaluiert | — | Siehe /docs/system/llm-frameworks.md |
| Colors | ✅ Erstellt | 008 | In tenant_branding referenzierbar |

## Eigene Quickstarts

| Quickstart | Datei | Zweck |
|-----------|-------|-------|
| Event-Tracking-Baseline | event-tracking-baseline.sql | DOS v2.0 Kap. 11 — analytics_events |
| Audit-Log-Baseline | audit-log-baseline.sql | DOS v2.0 Kap. 14 — audit_logs |
| Feature-Flag-Baseline | feature-flag-baseline.sql | Saubere Rollouts — feature_flags |
| RLS-Template | rls-template.sql | is_staff(), user_tenant_id() — Muster für neue Tabellen |
| Timestamp-Automation | timestamp-automation.sql | set_timestamp() Trigger |
| Revolut Business | nexifyai-revolut-business.sql | Ersetzt Stripe — revolut_orders, webhook_events, configs |
