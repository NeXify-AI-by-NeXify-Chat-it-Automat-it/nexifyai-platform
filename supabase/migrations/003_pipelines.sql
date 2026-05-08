-- Phase 1: Migration 003 — pipelines, applications
CREATE TABLE IF NOT EXISTS public.pipelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft','active','paused','archived')),
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES public.pipelines(id) ON DELETE SET NULL,
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'web' CHECK (type IN ('web','api','mobile','desktop','cli','other')),
    repo_url TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.pipelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY pip_staff ON public.pipelines FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles p JOIN public.workspace_members wm ON p.id=wm.profile_id WHERE p.user_id=auth.uid() AND wm.workspace_id=pipelines.workspace_id AND wm.role IN ('admin','owner')));

CREATE POLICY app_portal_read ON public.applications FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles p JOIN public.workspace_members wm ON p.id=wm.profile_id WHERE p.user_id=auth.uid() AND wm.workspace_id=applications.workspace_id));
