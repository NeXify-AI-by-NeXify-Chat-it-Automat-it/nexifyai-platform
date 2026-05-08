-- Phase 1: Migration 004 — documents, document_requests, comments
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id),
    application_id UUID REFERENCES public.applications(id),
    title TEXT NOT NULL,
    content TEXT,
    visibility TEXT DEFAULT 'internal' CHECK (visibility IN ('internal','public','restricted')),
    file_path TEXT,
    file_type TEXT,
    file_size BIGINT,
    metadata JSONB DEFAULT '{}',
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.document_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES public.workspaces(id),
    from_email TEXT NOT NULL,
    from_name TEXT,
    document_ids UUID[] DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending','approved','denied','fulfilled')),
    message TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES public.profiles(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY doc_internal ON public.documents FOR SELECT TO authenticated
    USING (visibility='public' OR created_by=auth.uid() OR EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
