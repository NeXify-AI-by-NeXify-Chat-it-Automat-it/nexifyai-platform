-- Phase 1: Migration 002 — workspaces, workspace_members
-- Tenant-Isolation: workspace → organization → member
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(organization_id, slug)
);

CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner','admin','member','viewer')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(workspace_id, profile_id)
);

ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY ws_org_access ON public.workspaces FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles p WHERE p.user_id = auth.uid() AND p.organization_id = workspaces.organization_id));

CREATE POLICY wsm_self ON public.workspace_members FOR SELECT TO authenticated
    USING (profile_id IN (SELECT id FROM public.profiles WHERE user_id = auth.uid()));
