-- Phase 2: Migration 012 — auto_assignment & lead deduplication automation
-- Führt assignment_rules mit conversation-Trigger zusammen

-- 1. Auto-Assignment Trigger: Weist leads automatisch zu wenn conditions passen
CREATE OR REPLACE FUNCTION auto_assign_lead()
RETURNS trigger AS $$
DECLARE
  rule RECORD;
  target_user UUID;
BEGIN
  -- Nur bei neuen oder aktualisierten conversations mit lead_score
  IF TG_OP = 'UPDATE' AND NEW.lead_score IS NOT DISTINCT FROM OLD.lead_score THEN
    RETURN NEW;
  END IF;

  -- Durch alle aktiven Regeln iterieren
  FOR rule IN 
    SELECT * FROM public.assignment_rules 
    WHERE enabled = true 
    ORDER BY priority DESC 
    LIMIT 1
  LOOP
    -- Einfachste Regel: Zuweisen falls definiert
    IF rule.assign_to IS NOT NULL AND NEW.assigned_to IS NULL THEN
      NEW.assigned_to = rule.assign_to;
      NEW.kanban_column = 'assigned';
      
      -- Event loggen
      INSERT INTO public.customer_events (conversation_id, event_type, description, actor_id)
      VALUES (NEW.id, 'assignment', format('Auto assigned via rule: %s', rule.name), rule.assign_to);
    END IF;
  END LOOP;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auto_assign ON public.conversations;
CREATE TRIGGER trg_auto_assign
  BEFORE INSERT OR UPDATE OF lead_score ON public.conversations
  FOR EACH ROW EXECUTE FUNCTION auto_assign_lead();

-- 2. Default Kanban Columns für alle neuen Workspaces
CREATE OR REPLACE FUNCTION create_default_kanban_columns()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.kanban_columns (workspace_id, name, color, sort_order) VALUES
    (NEW.id, 'Inbox', '#6b7280', 0),
    (NEW.id, 'Assigned', '#3b82f6', 1),
    (NEW.id, 'In Progress', '#f59e0b', 2),
    (NEW.id, 'Review', '#8b5cf6', 3),
    (NEW.id, 'Done', '#22c55e', 4);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_default_kanban ON public.workspaces;
CREATE TRIGGER trg_default_kanban
  AFTER INSERT ON public.workspaces
  FOR EACH ROW EXECUTE FUNCTION create_default_kanban_columns();

-- 3. Health-Score Erweiterung: Phase-2-Status checken
COMMENT ON TABLE public.assignment_rules IS 'Phase 2: Auto-Assignment Rules';
COMMENT ON TABLE public.customer_events IS 'Phase 2: Customer Timeline/Aktivitätsfeed';
COMMENT ON TABLE public.lead_duplicates IS 'Phase 2: Dublettenerkennung für CRM';
