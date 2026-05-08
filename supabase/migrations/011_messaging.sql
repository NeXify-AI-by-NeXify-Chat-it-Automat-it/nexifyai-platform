-- Phase 2: Migration 011 — messaging extensions + auto_assignment rules
-- Erweitert messages für CRM-Kontext, fügt assignment rules hinzu

-- 1. Messages erweitern
ALTER TABLE public.messages ADD COLUMN IF NOT EXISTS message_type TEXT DEFAULT 'text' CHECK (message_type IN ('text','file','system','reaction'));
ALTER TABLE public.messages ADD COLUMN IF NOT EXISTS attachment_url TEXT;
ALTER TABLE public.messages ADD COLUMN IF NOT EXISTS attachment_name TEXT;
ALTER TABLE public.messages ADD COLUMN IF NOT EXISTS reaction_to UUID REFERENCES public.messages(id);

-- 2. Auto-Assignment Rules
CREATE TABLE IF NOT EXISTS public.assignment_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    conditions JSONB NOT NULL DEFAULT '{}',  -- z.B. {"lead_score": {"min": 70}, "source": "website"}
    assign_to UUID REFERENCES auth.users(id),
    priority INT DEFAULT 0,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Customer Timeline (Aktivitäts-Feed)
CREATE TABLE IF NOT EXISTS public.customer_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,  -- message, status_change, assignment, tag_added, note
    description TEXT,
    actor_id UUID REFERENCES auth.users(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS
ALTER TABLE public.assignment_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY ar_staff ON public.assignment_rules FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id = auth.uid() AND role IN ('staff','admin')));

-- Fix: Alte fehlerhafte Policy droppen, neue mit tenant_id erstellen
DROP POLICY IF EXISTS ce_workspace ON public.customer_events;

CREATE POLICY ce_workspace ON public.customer_events FOR ALL TO authenticated
    USING (EXISTS (
        SELECT 1 FROM public.conversations c 
        JOIN public.profiles p ON p.organization_id = c.tenant_id
        WHERE c.id = customer_events.conversation_id AND p.user_id = auth.uid()
    ));

-- Indexe
CREATE INDEX IF NOT EXISTS idx_msg_type ON public.messages(message_type);
CREATE INDEX IF NOT EXISTS idx_ce_conv ON public.customer_events(conversation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ar_workspace ON public.assignment_rules(workspace_id, enabled);
