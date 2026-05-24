-- ============================================================
-- Migration 018: Fix Orchestrator V3 RLS — Service-Role + Staff-Isolation
-- NeXifyAI DOS v4.8 — AIC-49 Security Consolidation
--
-- Behebt fehlende RLS auf 4 Orchestrator-Tabellen aus
-- 014_orchestrator_v3_tables.sql:
--   - rules_registry
--   - team_registry
--   - task_graph
--   - agent_metrics
--
-- Prinzip:
--   Service-Role + Staff/Admin = Vollzugriff
--   Authentifizierte User = Nur SELECT (eingeschränkter Read-Only)
-- ============================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════
-- 1. RULES REGISTRY — Agenten-Verhaltensregeln
-- ═══════════════════════════════════════════════════════════
ALTER TABLE public.rules_registry ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS rules_registry_all ON public.rules_registry;
DROP POLICY IF EXISTS rules_registry_service ON public.rules_registry;

-- Service-Role + Staff/Admin: Full CRUD
CREATE POLICY "rules_registry_service_admin" ON public.rules_registry
    FOR ALL USING (
        auth.role() = 'service_role'
        OR is_staff(auth.uid())
    );

-- Authentifizierte User: Read-Only
CREATE POLICY "rules_registry_read" ON public.rules_registry
    FOR SELECT TO authenticated USING (true);


-- ═══════════════════════════════════════════════════════════
-- 2. TEAM REGISTRY — Capability-basierte Agenten-Teams
-- ═══════════════════════════════════════════════════════════
ALTER TABLE public.team_registry ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS team_registry_all ON public.team_registry;
DROP POLICY IF EXISTS team_registry_service ON public.team_registry;

-- Service-Role + Staff/Admin: Full CRUD
CREATE POLICY "team_registry_service_admin" ON public.team_registry
    FOR ALL USING (
        auth.role() = 'service_role'
        OR is_staff(auth.uid())
    );

-- Authentifizierte User: Read-Only
CREATE POLICY "team_registry_read" ON public.team_registry
    FOR SELECT TO authenticated USING (true);


-- ═══════════════════════════════════════════════════════════
-- 3. TASK GRAPH — Multi-Step Agenten-Pipelines
-- ═══════════════════════════════════════════════════════════
ALTER TABLE public.task_graph ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS task_graph_all ON public.task_graph;
DROP POLICY IF EXISTS task_graph_service ON public.task_graph;

-- Service-Role + Staff/Admin: Full CRUD
CREATE POLICY "task_graph_service_admin" ON public.task_graph
    FOR ALL USING (
        auth.role() = 'service_role'
        OR is_staff(auth.uid())
    );

-- Authentifizierte User: Read-Only
CREATE POLICY "task_graph_read" ON public.task_graph
    FOR SELECT TO authenticated USING (true);


-- ═══════════════════════════════════════════════════════════
-- 4. AGENT METRICS — Performance-Tracking
-- ═══════════════════════════════════════════════════════════
ALTER TABLE public.agent_metrics ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS agent_metrics_all ON public.agent_metrics;
DROP POLICY IF EXISTS agent_metrics_service ON public.agent_metrics;

-- Service-Role + Staff/Admin: Full CRUD
CREATE POLICY "agent_metrics_service_admin" ON public.agent_metrics
    FOR ALL USING (
        auth.role() = 'service_role'
        OR is_staff(auth.uid())
    );

-- Authentifizierte User: Read-Only
CREATE POLICY "agent_metrics_read" ON public.agent_metrics
    FOR SELECT TO authenticated USING (true);


-- ═══════════════════════════════════════════════════════════
-- 5. VERIFIKATION
-- ═══════════════════════════════════════════════════════════
DO $$
DECLARE
    tbl TEXT;
    orchestrator_tables TEXT[] := ARRAY['rules_registry', 'team_registry', 'task_graph', 'agent_metrics'];
BEGIN
    FOREACH tbl IN ARRAY orchestrator_tables
    LOOP
        -- RLS enabled
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);

        -- Prüfen ob Policies existieren
        IF NOT EXISTS (
            SELECT 1 FROM pg_policies
            WHERE schemaname = 'public' AND tablename = tbl
        ) THEN
            RAISE WARNING 'Orchestrator-Tabelle % hat KEINE Policies!', tbl;
        END IF;
    END LOOP;
END $$;

COMMIT;
