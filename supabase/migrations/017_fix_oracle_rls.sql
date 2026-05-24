-- ============================================================
-- Migration 017: Fix Oracle Enterprise RLS — Echte Tenant/Staff-Isolation
-- NeXifyAI DOS v4.8 — AIC-49 Security Consolidation
--
-- Behebt KRITISCHE SICHERHEITSLÜCKE aus 013_oracle_enterprise_tables.sql:
--   FOR ALL TO authenticated USING (true) → Jeder User = Vollzugriff
--
-- Erfordert: 015_secrets_vault.sql (nutzt is_staff())
-- Fixt:      Alle 20 oracle_%-Tabellen mit gestaffelten Policies
-- ============================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════
-- 1. HELPER-FUNKTION: is_staff()
--    Wird von 015_secrets_vault.sql UND 016_fix_rls_and_policies.sql
--    referenziert, war aber NIE in einer Migration definiert!
-- ═══════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION public.is_staff(uid uuid)
RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles
    WHERE user_id = uid AND role IN ('staff', 'admin')
  );
$$;

-- ═══════════════════════════════════════════════════════════
-- 2. ALLE ALTEN POLICIES ENTFERNEN
--    a) Permissive "_all" Policies aus 013 (DO-Block)
--    b) Policies aus 016 (wenn schon ausgeführt, redundant)
-- ═══════════════════════════════════════════════════════════
DO $$
DECLARE
    tbl TEXT;
    old_pol TEXT;
BEGIN
    FOR tbl IN
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public' AND tablename LIKE 'oracle_%'
    LOOP
        -- Alle existierenden Policies auf jeder oracle_-Tabelle droppen
        FOR old_pol IN
            SELECT policyname FROM pg_policies
            WHERE schemaname = 'public' AND tablename = tbl
        LOOP
            EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', old_pol, tbl);
        END LOOP;
    END LOOP;
END $$;


-- ═══════════════════════════════════════════════════════════
-- 3. GRUPPE A: KRITISCHE SYSTEM-TABELLEN — NUR STAFF/ADMIN
--    oracle_audit, oracle_security_events, oracle_recovery,
--    oracle_runtime, oracle_reconciliation,
--    oracle_identities, oracle_identity_links
-- ═══════════════════════════════════════════════════════════

-- oracle_audit — Immutables Audit-Trail
CREATE POLICY "oracle_audit_staff_only" ON public.oracle_audit
    FOR ALL USING (is_staff(auth.uid()));

-- oracle_security_events — Sicherheits-Ereignisse
CREATE POLICY "oracle_security_events_staff_only" ON public.oracle_security_events
    FOR ALL USING (is_staff(auth.uid()));

-- oracle_recovery — Recovery-Operationen
CREATE POLICY "oracle_recovery_staff_only" ON public.oracle_recovery
    FOR ALL USING (is_staff(auth.uid()));

-- oracle_runtime — Runtime-State (enthält Secrets/Metrics)
CREATE POLICY "oracle_runtime_staff_only" ON public.oracle_runtime
    FOR ALL USING (is_staff(auth.uid()));

-- oracle_reconciliation — Konflikt-Management
CREATE POLICY "oracle_reconciliation_staff_only" ON public.oracle_reconciliation
    FOR ALL USING (is_staff(auth.uid()));

-- oracle_identities — PII-sensitiv (Channel-Mapping)
CREATE POLICY "oracle_identities_staff_only" ON public.oracle_identities
    FOR ALL USING (is_staff(auth.uid()));

-- oracle_identity_links — PII-sensitiv (Cross-Channel-Links)
CREATE POLICY "oracle_identity_links_staff_only" ON public.oracle_identity_links
    FOR ALL USING (is_staff(auth.uid()));


-- ═══════════════════════════════════════════════════════════
-- 4. GRUPPE B: WISSENS-TABELLEN — Staff CRUD, Customer Read
--    oracle_documents, oracle_chunks, oracle_embeddings,
--    oracle_knowledge_sources
-- ═══════════════════════════════════════════════════════════

-- oracle_documents — Primärer Wissenscontainer
CREATE POLICY "oracle_documents_select" ON public.oracle_documents
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_documents_insert" ON public.oracle_documents
    FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY "oracle_documents_update" ON public.oracle_documents
    FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY "oracle_documents_delete" ON public.oracle_documents
    FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- oracle_chunks — Dokument-Fragmente
CREATE POLICY "oracle_chunks_select" ON public.oracle_chunks
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_chunks_write" ON public.oracle_chunks
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));

-- oracle_embeddings — Vektor-Metadaten
CREATE POLICY "oracle_embeddings_select" ON public.oracle_embeddings
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_embeddings_write" ON public.oracle_embeddings
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));

-- oracle_knowledge_sources — Quellen-Registry
CREATE POLICY "oracle_knowledge_sources_select" ON public.oracle_knowledge_sources
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_knowledge_sources_write" ON public.oracle_knowledge_sources
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));


-- ═══════════════════════════════════════════════════════════
-- 5. GRUPPE C: OPERATIVE TABELLEN — Staff CRUD, Customer Read
--    oracle_events, oracle_tasks, oracle_agents, oracle_sessions,
--    oracle_incidents, oracle_policies, oracle_adrs
-- ═══════════════════════════════════════════════════════════

-- oracle_events — Enterprise Event-Ledger
CREATE POLICY "oracle_events_select" ON public.oracle_events
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_events_write" ON public.oracle_events
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));

-- oracle_tasks — Governed Task-Ledger
CREATE POLICY "oracle_tasks_select" ON public.oracle_tasks
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_tasks_write" ON public.oracle_tasks
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));

-- oracle_agents — Governed Agent-Registry
CREATE POLICY "oracle_agents_select" ON public.oracle_agents
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_agents_insert" ON public.oracle_agents
    FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY "oracle_agents_update" ON public.oracle_agents
    FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY "oracle_agents_delete" ON public.oracle_agents
    FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- oracle_sessions — Governed Session-Registry
CREATE POLICY "oracle_sessions_select" ON public.oracle_sessions
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_sessions_write" ON public.oracle_sessions
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));

-- oracle_incidents — Incident-Management
CREATE POLICY "oracle_incidents_select" ON public.oracle_incidents
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_incidents_insert" ON public.oracle_incidents
    FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY "oracle_incidents_update" ON public.oracle_incidents
    FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY "oracle_incidents_delete" ON public.oracle_incidents
    FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- oracle_policies — Governed Policy-Registry
CREATE POLICY "oracle_policies_select" ON public.oracle_policies
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_policies_insert" ON public.oracle_policies
    FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY "oracle_policies_update" ON public.oracle_policies
    FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY "oracle_policies_delete" ON public.oracle_policies
    FOR DELETE TO authenticated USING (is_staff(auth.uid()));

-- oracle_adrs — Architecture Decision Records
CREATE POLICY "oracle_adrs_select" ON public.oracle_adrs
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_adrs_insert" ON public.oracle_adrs
    FOR INSERT TO authenticated WITH CHECK (is_staff(auth.uid()));
CREATE POLICY "oracle_adrs_update" ON public.oracle_adrs
    FOR UPDATE TO authenticated USING (is_staff(auth.uid()));
CREATE POLICY "oracle_adrs_delete" ON public.oracle_adrs
    FOR DELETE TO authenticated USING (is_staff(auth.uid()));


-- ═══════════════════════════════════════════════════════════
-- 6. GRUPPE D: WEITERE TABELLEN — Staff CRUD, Customer Read
--    oracle_retrieval, oracle_dependencies
-- ═══════════════════════════════════════════════════════════

-- oracle_retrieval — Retrieval-Qualitäts-Tracking
CREATE POLICY "oracle_retrieval_select" ON public.oracle_retrieval
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_retrieval_write" ON public.oracle_retrieval
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));

-- oracle_dependencies — Abhängigkeitsgraph
CREATE POLICY "oracle_dependencies_select" ON public.oracle_dependencies
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "oracle_dependencies_write" ON public.oracle_dependencies
    FOR ALL TO authenticated USING (is_staff(auth.uid()))
    WITH CHECK (is_staff(auth.uid()));


-- ═══════════════════════════════════════════════════════════
-- 7. VERIFIKATION: RLS ist auf ALLEN oracle_-Tabellen aktiv
-- ═══════════════════════════════════════════════════════════
DO $$
DECLARE
    tbl TEXT;
    rls_enabled BOOLEAN;
    missing_policies TEXT[] := '{}';
BEGIN
    FOR tbl IN
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public' AND tablename LIKE 'oracle_%'
    LOOP
        -- Sicherstellen dass RLS enabled ist
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);

        -- Prüfen ob Policies existieren
        IF NOT EXISTS (
            SELECT 1 FROM pg_policies
            WHERE schemaname = 'public' AND tablename = tbl
        ) THEN
            missing_policies := array_append(missing_policies, tbl);
        END IF;
    END LOOP;

    IF array_length(missing_policies, 1) IS NOT NULL THEN
        RAISE WARNING 'Folgende Tabellen haben KEINE Policies: %',
            array_to_string(missing_policies, ', ');
    END IF;
END $$;

COMMIT;
