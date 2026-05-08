-- Phase 2: Migration 010 — lead_ingest extensions
-- Erweitert conversations, tasks, profiles für CRM Core
-- Abhängigkeiten: Migration 001 (profiles), 002 (workspaces), 006 (conversations, tasks)

-- 1. Conversations erweitern für Lead-Management
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS lead_score INT DEFAULT 0;
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS lead_source TEXT;
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS assigned_to UUID REFERENCES auth.users(id);
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS kanban_column TEXT DEFAULT 'inbox';
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS next_followup_at TIMESTAMPTZ;
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';

-- 2. Tasks für Kanban erweitern
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS kanban_order INT;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS blocked_by UUID[] DEFAULT '{}';
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS estimated_hours NUMERIC(4,1);
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS actual_hours NUMERIC(4,1);
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS conversation_id UUID REFERENCES public.conversations(id);

-- 3. Lead Duplicates Tabelle
CREATE TABLE IF NOT EXISTS public.lead_duplicates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_a UUID REFERENCES public.conversations(id),
    lead_b UUID REFERENCES public.conversations(id),
    similarity FLOAT CHECK (similarity BETWEEN 0 AND 1),
    merged_into UUID REFERENCES public.conversations(id),
    status TEXT DEFAULT 'open' CHECK (status IN ('open','merged','dismissed')),
    detected_at TIMESTAMPTZ DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

-- 4. Kanban Columns
CREATE TABLE IF NOT EXISTS public.kanban_columns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#6b7280',
    sort_order INT DEFAULT 0,
    wip_limit INT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS für neue Tabellen
ALTER TABLE public.lead_duplicates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kanban_columns ENABLE ROW LEVEL SECURITY;

-- Staff/Admin: Vollzugriff auf alle neuen Strukturen
CREATE POLICY ld_staff ON public.lead_duplicates FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id = auth.uid() AND role IN ('staff','admin')));

CREATE POLICY kc_workspace ON public.kanban_columns FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.workspace_members wm JOIN public.profiles p ON p.id = wm.profile_id WHERE p.user_id = auth.uid() AND wm.workspace_id = kanban_columns.workspace_id));

-- Indexe für Performance
CREATE INDEX IF NOT EXISTS idx_conv_assigned ON public.conversations(assigned_to);
CREATE INDEX IF NOT EXISTS idx_conv_kanban ON public.conversations(kanban_column);
CREATE INDEX IF NOT EXISTS idx_conv_score ON public.conversations(lead_score DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_kanban ON public.tasks(kanban_order);
CREATE INDEX IF NOT EXISTS idx_ld_status ON public.lead_duplicates(status);
