-- Supabase RLS Policies — NeXifyAI (self-hosted)
-- Generiert: 09.05.2026 | NXA-AUDIT-09052026
-- 
-- 14 Tabellen ohne RLS. Hier die minimalen Policies:
-- Nur service_role (Backend) und authenticated (Admin) haben Zugriff.

-- 1. oracle_ready_queue
ALTER TABLE public.oracle_ready_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.oracle_ready_queue
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "admin_read_only" ON public.oracle_ready_queue
  FOR SELECT USING (auth.role() = 'authenticated');

-- 2. knowledge_base
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.knowledge_base
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "admin_read_only" ON public.knowledge_base
  FOR SELECT USING (auth.role() = 'authenticated');

-- 3. memory_entries
ALTER TABLE public.memory_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.memory_entries
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "admin_read_only" ON public.memory_entries
  FOR SELECT USING (auth.role() = 'authenticated');

-- 4. ai_agents
ALTER TABLE public.ai_agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.ai_agents
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 5. audit_logs
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.audit_logs
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 6. oracle_tasks
ALTER TABLE public.oracle_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.oracle_tasks
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 7. oracle_autonomous_status
ALTER TABLE public.oracle_autonomous_status ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.oracle_autonomous_status
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 8. oracle_full_context
ALTER TABLE public.oracle_full_context ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.oracle_full_context
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 9. email_events
ALTER TABLE public.email_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.email_events
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 10. error_events
ALTER TABLE public.error_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.error_events
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 11. support_tickets
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.support_tickets
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 12. memories
ALTER TABLE public.memories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.memories
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 13. oracle_agents
ALTER TABLE public.oracle_agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.oracle_agents
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 14. brain_notes
ALTER TABLE public.brain_notes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON public.brain_notes
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "admin_read_only" ON public.brain_notes
  FOR SELECT USING (auth.role() = 'authenticated');
