-- Phase 1: Migration 007 — notifications, audit_logs, automation_runs, webhook_events
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    read BOOLEAN DEFAULT false,
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES auth.users(id),
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    details JSONB DEFAULT '{}',
    ip_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.automation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    automation_name TEXT NOT NULL,
    trigger_event TEXT,
    status TEXT DEFAULT 'running' CHECK (status IN ('running','completed','failed')),
    input JSONB,
    output JSONB,
    error TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT DEFAULT 'received' CHECK (status IN ('received','processed','failed')),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhook_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY notif_own ON public.notifications FOR ALL TO authenticated USING (user_id = auth.uid());
CREATE POLICY audit_staff ON public.audit_logs FOR SELECT TO authenticated USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
CREATE POLICY auto_append ON public.automation_runs FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY webhook_append ON public.webhook_events FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY webhook_staff_read ON public.webhook_events FOR SELECT TO authenticated USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));

CREATE INDEX IF NOT EXISTS idx_audit_actor ON public.audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON public.audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_source ON public.webhook_events(source, event_type);
