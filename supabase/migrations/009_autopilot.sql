-- Phase 1: Migration 009 — Autopilot: tasks (erweitert), incidents
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS autopilot BOOLEAN DEFAULT false;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS tag TEXT[] DEFAULT '{}';
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS rice_score FLOAT;

CREATE TABLE IF NOT EXISTS public.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES public.tasks(id),
    error_type TEXT NOT NULL,
    root_cause TEXT,
    fix_strategy TEXT,
    success BOOLEAN DEFAULT false,
    retry_count INT DEFAULT 0,
    log_snippet TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;

CREATE POLICY inc_staff ON public.incidents FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));

CREATE INDEX IF NOT EXISTS idx_incidents_task ON public.incidents(task_id);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON public.incidents(error_type);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_autopilot ON public.tasks(autopilot) WHERE autopilot = true;
