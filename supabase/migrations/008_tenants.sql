-- Phase 1: Migration 008 — White-Label: tenants, tenant_configs, tenant_members, tenant_branding, tenant_integrations
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    domain TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active','suspended','archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.tenant_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, key)
);

CREATE TABLE IF NOT EXISTS public.tenant_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner','admin','member')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, profile_id)
);

CREATE TABLE IF NOT EXISTS public.tenant_branding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID UNIQUE REFERENCES public.tenants(id) ON DELETE CASCADE,
    logo_url TEXT,
    favicon_url TEXT,
    primary_color TEXT,
    accent_color TEXT,
    font_heading TEXT,
    font_body TEXT,
    custom_css TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.tenant_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    type TEXT NOT NULL,
    credentials JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, provider, type)
);

ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_branding ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_integrations ENABLE ROW LEVEL SECURITY;

CREATE POLICY tnt_staff ON public.tenants FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
CREATE POLICY tntcfg_staff ON public.tenant_configs FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
