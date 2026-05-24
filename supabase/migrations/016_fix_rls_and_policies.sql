-- Migration 016: Fix RLS Policies — Oracle graduated access + customer_events tenant fix
-- NeXifyAI DOS v4.8 — Security Consolidation
--
-- This migration fixes two issues:
--   1. The overly permissive DO block in 013 that applies `FOR ALL TO authenticated USING (true)`
--      on all oracle_% tables. Replaced with graduated access using is_staff() helpers.
--   2. The customer_events RLS policy in 011 that references `c.tenant_id` which doesn't exist
--      on the conversations table. Fixed to use workspace → organization join.
--
-- NOTE: Policies already properly defined in supabase-rls-policies.sql for some tables;
--       this migration covers ALL oracle tables comprehensively.

BEGIN;

-- ═══════════════════════════════════════════════════════
-- PART 1: Fix Oracle Enterprise RLS (replace permissive DO block)
-- ═══════════════════════════════════════════════════════
-- The DO block in 013 created: CREATE POLICY <tbl>_all ON <tbl> FOR ALL TO authenticated USING (true)
-- We drop ALL those permissive policies and create graduated ones.

-- Drop all permissive "_all" policies created by the DO block in 013
DO $$
DECLARE
    tbl TEXT;
    pol TEXT;
BEGIN
    FOR tbl IN
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public' AND tablename LIKE 'oracle_%'
    LOOP
        -- Drop the permissive policy if it exists
        FOR pol IN
            SELECT policyname FROM pg_policies
            WHERE schemaname = 'public' AND tablename = tbl
              AND policyname = tbl || '_all'
        LOOP
            EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', pol, tbl);
        END LOOP;
    END LOOP;
END $$;

-- ── GROUP 1: Knowledge tables — Staff write, authenticated read ──

-- oracle_documents
DROP POLICY IF EXISTS oracle_documents_all ON public.oracle_documents;
CREATE POLICY oracle_documents_read ON public.oracle_documents FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_documents_insert ON public.oracle_documents FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_documents_update ON public.oracle_documents FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY oracle_documents_delete ON public.oracle_documents FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- oracle_chunks
DROP POLICY IF EXISTS oracle_chunks_all ON public.oracle_chunks;
CREATE POLICY oracle_chunks_read ON public.oracle_chunks FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_chunks_write ON public.oracle_chunks FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_embeddings
DROP POLICY IF EXISTS oracle_embeddings_all ON public.oracle_embeddings;
CREATE POLICY oracle_embeddings_read ON public.oracle_embeddings FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_embeddings_write ON public.oracle_embeddings FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_knowledge_sources
DROP POLICY IF EXISTS oracle_knowledge_sources_all ON public.oracle_knowledge_sources;
CREATE POLICY oracle_knowledge_sources_read ON public.oracle_knowledge_sources FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_knowledge_sources_write ON public.oracle_knowledge_sources FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- ── GROUP 2: ADRs & Policies — Staff write, authenticated read (handled in rls-policies too) ──

-- oracle_adrs
DROP POLICY IF EXISTS oracle_adrs_all ON public.oracle_adrs;
DROP POLICY IF EXISTS oracle_adrs_read ON public.oracle_adrs;
DROP POLICY IF EXISTS oracle_adrs_write ON public.oracle_adrs;
DROP POLICY IF EXISTS oracle_adrs_update ON public.oracle_adrs;
DROP POLICY IF EXISTS oracle_adrs_delete ON public.oracle_adrs;
CREATE POLICY oracle_adrs_read ON public.oracle_adrs FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_adrs_insert ON public.oracle_adrs FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_adrs_update ON public.oracle_adrs FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY oracle_adrs_delete ON public.oracle_adrs FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- oracle_policies
DROP POLICY IF EXISTS oracle_policies_all ON public.oracle_policies;
DROP POLICY IF EXISTS oracle_policies_read ON public.oracle_policies;
DROP POLICY IF EXISTS oracle_policies_write ON public.oracle_policies;
DROP POLICY IF EXISTS oracle_policies_update ON public.oracle_policies;
CREATE POLICY oracle_policies_read ON public.oracle_policies FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_policies_insert ON public.oracle_policies FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_policies_update ON public.oracle_policies FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY oracle_policies_delete ON public.oracle_policies FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- ── GROUP 3: Operational tables — Staff all, authenticated read ──

-- oracle_events
DROP POLICY IF EXISTS oracle_events_all ON public.oracle_events;
CREATE POLICY oracle_events_read ON public.oracle_events FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_events_write ON public.oracle_events FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_tasks
DROP POLICY IF EXISTS oracle_tasks_all ON public.oracle_tasks;
CREATE POLICY oracle_tasks_read ON public.oracle_tasks FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_tasks_write ON public.oracle_tasks FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_sessions
DROP POLICY IF EXISTS oracle_sessions_all ON public.oracle_sessions;
CREATE POLICY oracle_sessions_read ON public.oracle_sessions FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_sessions_write ON public.oracle_sessions FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_runtime
DROP POLICY IF EXISTS oracle_runtime_all ON public.oracle_runtime;
CREATE POLICY oracle_runtime_read ON public.oracle_runtime FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_runtime_write ON public.oracle_runtime FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_retrieval
DROP POLICY IF EXISTS oracle_retrieval_all ON public.oracle_retrieval;
CREATE POLICY oracle_retrieval_read ON public.oracle_retrieval FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_retrieval_write ON public.oracle_retrieval FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_dependencies
DROP POLICY IF EXISTS oracle_dependencies_all ON public.oracle_dependencies;
CREATE POLICY oracle_dependencies_read ON public.oracle_dependencies FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_dependencies_write ON public.oracle_dependencies FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- oracle_recovery
DROP POLICY IF EXISTS oracle_recovery_all ON public.oracle_recovery;
CREATE POLICY oracle_recovery_read ON public.oracle_recovery FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_recovery_write ON public.oracle_recovery FOR ALL TO authenticated USING (is_staff(auth.uid()));

-- ── GROUP 4: Agent tables — Agents can read via service_role ──

-- oracle_agents
DROP POLICY IF EXISTS oracle_agents_all ON public.oracle_agents;
DROP POLICY IF EXISTS oracle_agents_read ON public.oracle_agents;
DROP POLICY IF EXISTS oracle_agents_write ON public.oracle_agents;
CREATE POLICY oracle_agents_read ON public.oracle_agents FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_agents_insert ON public.oracle_agents FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_agents_update ON public.oracle_agents FOR UPDATE TO authenticated USING (is_staff(auth.uid()) OR auth.uid() IS NOT NULL);
CREATE POLICY oracle_agents_delete ON public.oracle_agents FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- oracle_incidents
DROP POLICY IF EXISTS oracle_incidents_all ON public.oracle_incidents;
DROP POLICY IF EXISTS oracle_incidents_read ON public.oracle_incidents;
DROP POLICY IF EXISTS oracle_incidents_write ON public.oracle_incidents;
DROP POLICY IF EXISTS oracle_incidents_update ON public.oracle_incidents;
CREATE POLICY oracle_incidents_read ON public.oracle_incidents FOR SELECT TO authenticated USING (true);
CREATE POLICY oracle_incidents_insert ON public.oracle_incidents FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY oracle_incidents_update ON public.oracle_incidents FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY oracle_incidents_delete ON public.oracle_incidents FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- ── GROUP 5: Sensitive/Security tables — Staff only ──

-- oracle_audit (immutable audit trail — staff only)
DROP POLICY IF EXISTS oracle_audit_all ON public.oracle_audit;
DROP POLICY IF EXISTS oracle_audit_staff ON public.oracle_audit;
CREATE POLICY oracle_audit_staff ON public.oracle_audit FOR ALL TO authenticated
    USING (is_staff(auth.uid()));

-- oracle_security_events
DROP POLICY IF EXISTS oracle_security_events_all ON public.oracle_security_events;
DROP POLICY IF EXISTS oracle_sec_staff ON public.oracle_security_events;
CREATE POLICY oracle_sec_staff ON public.oracle_security_events FOR ALL TO authenticated
    USING (is_staff(auth.uid()));

-- oracle_reconciliation
DROP POLICY IF EXISTS oracle_reconciliation_all ON public.oracle_reconciliation;
CREATE POLICY oracle_reconciliation_staff ON public.oracle_reconciliation FOR ALL TO authenticated
    USING (is_staff(auth.uid()));

-- oracle_identities (PII-sensitive)
DROP POLICY IF EXISTS oracle_identities_all ON public.oracle_identities;
CREATE POLICY oracle_identities_staff ON public.oracle_identities FOR ALL TO authenticated
    USING (is_staff(auth.uid()));

-- oracle_identity_links (PII-sensitive)
DROP POLICY IF EXISTS oracle_identity_links_all ON public.oracle_identity_links;
CREATE POLICY oracle_identity_links_staff ON public.oracle_identity_links FOR ALL TO authenticated
    USING (is_staff(auth.uid()));


-- ═══════════════════════════════════════════════════════
-- PART 2: Fix customer_events RLS policy (broken tenant_id reference)
-- ═══════════════════════════════════════════════════════
-- The original policy in 011_messaging.sql referenced `c.tenant_id` on the
-- conversations table, but conversations does NOT have a tenant_id column.
-- The correct lookup is: conversations → workspace → organization → profile
--
-- Original broken policy:
--   CREATE POLICY ce_workspace ON public.customer_events FOR ALL TO authenticated
--     USING (EXISTS (
--       SELECT 1 FROM public.conversations c
--       JOIN public.profiles p ON p.organization_id = c.tenant_id
--       WHERE c.id = customer_events.conversation_id AND p.user_id = auth.uid()
--     ));

DROP POLICY IF EXISTS ce_workspace ON public.customer_events;

CREATE POLICY ce_workspace ON public.customer_events FOR ALL TO authenticated
    USING (EXISTS (
        SELECT 1 FROM public.conversations c
        JOIN public.workspaces w ON w.id = c.workspace_id
        JOIN public.profiles p ON p.organization_id = w.organization_id
        WHERE c.id = customer_events.conversation_id
          AND p.user_id = auth.uid()
    ));

-- Also ensure customer_events RLS is enabled (it should be from 011, but idempotent)
ALTER TABLE public.customer_events ENABLE ROW LEVEL SECURITY;

COMMIT;
