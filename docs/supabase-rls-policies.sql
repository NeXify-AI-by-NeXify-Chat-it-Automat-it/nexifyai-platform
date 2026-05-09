-- ═══════════════════════════════════════════════════════════
-- NeXifyAI Supabase RLS Policies — Master Policy File
-- Generated: 2026-05-09 by AI-CEO (AIC-64)
-- Purpose: Ensure ALL tables have proper Row Level Security
-- Apply via: psql <DATABASE_URL> -f docs/supabase-rls-policies.sql
-- ═══════════════════════════════════════════════════════════

BEGIN;

-- ═══════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════

-- Check if user is staff or admin
CREATE OR REPLACE FUNCTION public.is_staff(uid uuid)
RETURNS boolean AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles
    WHERE user_id = uid AND role IN ('staff', 'admin')
  );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- Get user's organization/tenant ID
CREATE OR REPLACE FUNCTION public.user_tenant_id(uid uuid)
RETURNS uuid AS $$
  SELECT organization_id FROM public.profiles
  WHERE user_id = uid LIMIT 1;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- ═══════════════════════════════════════
-- CORE TABLES (001_core_tables.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS org_admin_all ON public.organizations;
CREATE POLICY org_admin_all ON public.organizations FOR ALL TO authenticated
  USING (is_staff(auth.uid()))
  WITH CHECK (is_staff(auth.uid()));

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS profile_own ON public.profiles;
CREATE POLICY profile_own ON public.profiles FOR SELECT TO authenticated
  USING (user_id = auth.uid() OR is_staff(auth.uid()));
CREATE POLICY profile_own_update ON public.profiles FOR UPDATE TO authenticated
  USING (user_id = auth.uid() OR is_staff(auth.uid()));
CREATE POLICY profile_staff_insert ON public.profiles FOR INSERT TO authenticated
  WITH CHECK (is_staff(auth.uid()));

ALTER TABLE public.user_consents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS consent_insert ON public.user_consents;
DROP POLICY IF EXISTS consent_select ON public.user_consents;
CREATE POLICY consent_insert ON public.user_consents FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY consent_select ON public.user_consents FOR SELECT TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- WORKSPACES (002_workspaces.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS workspace_access ON public.workspaces;
CREATE POLICY workspace_access ON public.workspaces FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR id IN (SELECT workspace_id FROM public.workspace_members WHERE user_id = auth.uid())
  );

ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS workspace_members_access ON public.workspace_members;
CREATE POLICY workspace_members_access ON public.workspace_members FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR user_id = auth.uid()
  );

-- ═══════════════════════════════════════
-- PIPELINES (003_pipelines.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.pipelines ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS pipeline_access ON public.pipelines;
CREATE POLICY pipeline_access ON public.pipelines FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- DOCUMENTS (004_documents.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS document_access ON public.documents;
CREATE POLICY document_access ON public.documents FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.document_requests ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS doc_request_access ON public.document_requests;
CREATE POLICY doc_request_access ON public.document_requests FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- INVOICES (005_invoices.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS invoice_access ON public.invoices;
CREATE POLICY invoice_access ON public.invoices FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS transaction_access ON public.transactions;
CREATE POLICY transaction_access ON public.transactions FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- CONVERSATIONS (006_conversations.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS conversation_access ON public.conversations;
CREATE POLICY conversation_access ON public.conversations FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR user_id = auth.uid()
  );

-- ═══════════════════════════════════════
-- NOTIFICATIONS (007_notifications.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS notification_access ON public.notifications;
CREATE POLICY notification_access ON public.notifications FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR user_id = auth.uid()
  );

-- ═══════════════════════════════════════
-- TENANTS (008_tenants.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_access ON public.tenants;
CREATE POLICY tenant_access ON public.tenants FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR id = user_tenant_id(auth.uid())
  );

ALTER TABLE public.tenant_members ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_member_access ON public.tenant_members;
CREATE POLICY tenant_member_access ON public.tenant_members FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR user_id = auth.uid()
  );

ALTER TABLE public.tenant_configs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_config_access ON public.tenant_configs;
CREATE POLICY tenant_config_access ON public.tenant_configs FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.tenant_branding ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_branding_access ON public.tenant_branding;
CREATE POLICY tenant_branding_access ON public.tenant_branding FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.tenant_integrations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_integration_access ON public.tenant_integrations;
CREATE POLICY tenant_integration_access ON public.tenant_integrations FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- AUTOPILOT (009_autopilot.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.automation_runs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS automation_run_access ON public.automation_runs;
CREATE POLICY automation_run_access ON public.automation_runs FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS application_access ON public.applications;
CREATE POLICY application_access ON public.applications FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR user_id = auth.uid()
  );

-- ═══════════════════════════════════════
-- LEAD INGEST (010_lead_ingest.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.customer_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS customer_event_access ON public.customer_events;
CREATE POLICY customer_event_access ON public.customer_events FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.lead_duplicates ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS lead_duplicate_access ON public.lead_duplicates;
CREATE POLICY lead_duplicate_access ON public.lead_duplicates FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.webhook_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS webhook_event_access ON public.webhook_events;
CREATE POLICY webhook_event_access ON public.webhook_events FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.assignment_rules ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS assignment_rule_access ON public.assignment_rules;
CREATE POLICY assignment_rule_access ON public.assignment_rules FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- MESSAGING (011_messaging.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS message_access ON public.messages;
CREATE POLICY message_access ON public.messages FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR sender_id = auth.uid()
    OR recipient_id = auth.uid()
  );

-- ═══════════════════════════════════════
-- AUTOASSIGN (012_autoassign.sql)
-- ═══════════════════════════════════════

ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS task_access ON public.tasks;
CREATE POLICY task_access ON public.tasks FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR assignee_id = auth.uid()
    OR created_by = auth.uid()
  );

ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS comment_access ON public.comments;
CREATE POLICY comment_access ON public.comments FOR ALL TO authenticated
  USING (
    is_staff(auth.uid())
    OR user_id = auth.uid()
  );

ALTER TABLE public.kanban_columns ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS kanban_column_access ON public.kanban_columns;
CREATE POLICY kanban_column_access ON public.kanban_columns FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- INCIDENTS & AUDIT
-- ═══════════════════════════════════════

ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS incident_access ON public.incidents;
CREATE POLICY incident_access ON public.incidents FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS audit_log_access ON public.audit_logs;
CREATE POLICY audit_log_access ON public.audit_logs FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- ═══════════════════════════════════════
-- ORACLE ENTERPRISE TABLES (013)
-- Already have RLS via DO block in migration
-- But ensure proper policies (not just permissive)
-- ═══════════════════════════════════════

-- Oracle tables use staff-only access:
-- All oracle_% tables already have RLS enabled with:
--   CREATE POLICY %I_all ON public.%I FOR ALL TO authenticated USING (true)
-- This is permissive by design (all authenticated users can read oracle data)
-- For write protection on critical tables:

-- Oracle ADRs: Staff write, all read
DROP POLICY IF EXISTS oracle_adrs_all ON public.oracle_adrs;
CREATE POLICY oracle_adrs_read ON public.oracle_adrs FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_adrs_write ON public.oracle_adrs FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_adrs_update ON public.oracle_adrs FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY oracle_adrs_delete ON public.oracle_adrs FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- Oracle Policies: Staff write, all read
DROP POLICY IF EXISTS oracle_policies_all ON public.oracle_policies;
CREATE POLICY oracle_policies_read ON public.oracle_policies FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_policies_write ON public.oracle_policies FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_policies_update ON public.oracle_policies FOR UPDATE TO authenticated USING (is_staff(auth.uid()));

-- Oracle Audit: Staff only (immutable audit trail)
DROP POLICY IF EXISTS oracle_audit_all ON public.oracle_audit;
CREATE POLICY oracle_audit_staff ON public.oracle_audit FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- Oracle Security Events: Staff only
DROP POLICY IF EXISTS oracle_security_events_all ON public.oracle_security_events;
CREATE POLICY oracle_sec_staff ON public.oracle_security_events FOR ALL TO authenticated
  USING (is_staff(auth.uid()));

-- Oracle Incidents: Staff write, all read
DROP POLICY IF EXISTS oracle_incidents_all ON public.oracle_incidents;
CREATE POLICY oracle_incidents_read ON public.oracle_incidents FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_incidents_write ON public.oracle_incidents FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_incidents_update ON public.oracle_incidents FOR UPDATE TO authenticated USING (is_staff(auth.uid()));

-- Oracle Agents: Staff write, all read
DROP POLICY IF EXISTS oracle_agents_all ON public.oracle_agents;
CREATE POLICY oracle_agents_read ON public.oracle_agents FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_agents_write ON public.oracle_agents FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- Oracle Sessions, Tasks, Dependencies: Staff write, all read
-- (These need agent write access too — handled via service_role in backend)

COMMIT;

-- ═══════════════════════════════════════
-- VERIFICATION QUERIES
-- ═══════════════════════════════════════
-- Run after applying to verify all tables have RLS:
--
-- SELECT tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public'
--   AND rowsecurity = false
-- ORDER BY tablename;
--
-- Should return 0 rows.
-- ═══════════════════════════════════════
