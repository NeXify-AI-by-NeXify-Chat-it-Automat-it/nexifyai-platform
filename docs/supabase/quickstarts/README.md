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

## Offizielle Supabase-Quickstarts (Referenzen)

| Quickstart | Schema-Prüfung | Status |
|-----------|---------------|--------|
| **User Management Starter** | profiles: id (uuid), username (text), avatar_url (text), website (text) — Supabase nutzt auth.users mit optionaler public.profiles | 🔄 Abweichung: Unser profiles hat organization_id, role, settings. Erweiterung ist korrekt für Multi-Tenant. |
| **Todo List** | tasks: id, user_id, task (text), is_complete (boolean), inserted_at (timestamptz) | 🔄 Unser tasks ist erweitert (assignee, priority, rice_score, retry_count). Korrekt für Autopilot. |
| **Slack Clone** | conversations + messages mit RLS: user kann nur eigene sehen, participant kann Room sehen | ✅ Unsere Migration 006 entspricht dem Pattern. Unterschied: Wir haben workspace-Zuordnung für Multi-Tenant. |
| **Stripe Subscriptions** | ❌ Ersetzt durch Revolut Business | Entfernt. Siehe nexifyai-revolut-business.sql |
| **NextAuth Schema Setup** | ❌ Nicht benötigt | Supabase GoTrue deckt Auth vollständig ab. NextAuth würde nur Komplexität hinzufügen ohne Mehrwert. |
| **OpenAI Vector Search** | ⏸️ Vorgemerkt | Qdrant bleibt primär. Supabase `pgvector` als Fallback für Blog/Knowledge-Suche dokumentiert. |
| **LangChain** | ⏸️ Evaluiert | Siehe /docs/system/llm-frameworks.md |
| **Colors** | ✅ triviale Lookup-Tabelle | Kann in tenant_branding (Migration 008) integriert werden. |
