-- Phase 1: Supabase-Fundament — Kernobjekte (Leitfassung Abschnitt 6)
-- Migration 001: organizations, profiles, user_consents

-- ═══════════════════════════════════════
-- ORGANIZATIONS
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    vat_id TEXT,
    address TEXT,
    country TEXT DEFAULT 'DE',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ═══════════════════════════════════════
-- PROFILES
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES public.organizations(id),
    role TEXT NOT NULL DEFAULT 'portal' CHECK (role IN ('public', 'portal', 'staff', 'admin')),
    display_name TEXT,
    avatar_url TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, organization_id)
);

-- ═══════════════════════════════════════
-- USER CONSENTS (Cookie-Governance)
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.user_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    consent_type TEXT NOT NULL CHECK (consent_type IN ('essential', 'functional', 'analytics', 'marketing')),
    granted BOOLEAN NOT NULL DEFAULT false,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    ip_hash TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_consents_user ON public.user_consents(user_id);
CREATE INDEX IF NOT EXISTS idx_user_consents_ts ON public.user_consents(timestamp DESC);

-- ═══════════════════════════════════════
-- RLS POLICIES
-- ═══════════════════════════════════════
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_consents ENABLE ROW LEVEL SECURITY;

-- Organizations: Staff/Admin can read, nobody can insert publicly
CREATE POLICY org_admin_all ON public.organizations FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id = auth.uid() AND role IN ('staff', 'admin')));

-- Profiles: User can read own profile; staff/admin can read all
CREATE POLICY profile_own ON public.profiles FOR SELECT TO authenticated
    USING (user_id = auth.uid() OR EXISTS (SELECT 1 FROM public.profiles p WHERE p.user_id = auth.uid() AND p.role IN ('staff', 'admin')));

-- User Consents: Anon can insert; staff can read
CREATE POLICY consent_insert ON public.user_consents FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY consent_select ON public.user_consents FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id = auth.uid() AND role IN ('staff', 'admin')));
