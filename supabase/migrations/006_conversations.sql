-- Phase 1: Migration 006 — conversations, messages, tasks
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id),
    subject TEXT,
    status TEXT DEFAULT 'open' CHECK (status IN ('open','closed','archived')),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES auth.users(id),
    role TEXT DEFAULT 'user' CHECK (role IN ('user','assistant','system','agent')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id),
    assignee_id UUID REFERENCES auth.users(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'waiting' CHECK (status IN ('waiting','in_progress','done','failed')),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low','medium','high','critical')),
    source TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    meta JSONB DEFAULT '{}',
    due_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY conv_own ON public.conversations FOR SELECT TO authenticated
    USING (created_by = auth.uid() OR EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
CREATE POLICY msg_conv ON public.messages FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM public.conversations c WHERE c.id=messages.conversation_id AND c.created_by=auth.uid()) OR EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
CREATE POLICY task_assignee ON public.tasks FOR ALL TO authenticated
    USING (assignee_id = auth.uid() OR EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
