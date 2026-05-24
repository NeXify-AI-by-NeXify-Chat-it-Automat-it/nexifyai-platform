-- ═══════════════════════════════════════════════════════════
-- Migration 015: Secrets Vault + Cost Tracking
-- NeXifyAI — Zentrales Credential-Management in Supabase
-- ═══════════════════════════════════════════════════════════

BEGIN;

-- ──────────────────────────────────────────────
-- 1. SERVICE-KATEGORIEN (für Kostenabrechnung)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.service_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_billable BOOLEAN DEFAULT true,
    markup_percent NUMERIC(5,2) DEFAULT 20.00,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ──────────────────────────────────────────────
-- 2. SERVICES (konkrete Dienste/Anbieter)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES public.service_categories(id),
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    description TEXT,
    base_url TEXT,
    is_active BOOLEAN DEFAULT true,
    billing_cycle TEXT DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'quarterly', 'yearly', 'per_request')),
    base_cost_monthly NUMERIC(10,2) DEFAULT 0,
    markup_percent NUMERIC(5,2) DEFAULT 20.00,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(name, provider)
);

-- ──────────────────────────────────────────────
-- 3. SECRETS VAULT (verschlüsselte Credentials)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.secrets_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID REFERENCES public.services(id),
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL,          -- verschlüsselt via PGCE crypto
    key_type TEXT DEFAULT 'api_key' CHECK (key_type IN ('api_key', 'password', 'token', 'jwt_secret', 'certificate', 'ssh_key', 'other')),
    environment TEXT DEFAULT 'production' CHECK (environment IN ('production', 'staging', 'development', 'all')),
    rotation_period_days INTEGER DEFAULT 90,
    rotated_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(service_id, key_name, environment)
);

-- ──────────────────────────────────────────────
-- 4. KUNDENPROJEKTE (Customer Projects)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.customer_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    is_internal BOOLEAN DEFAULT false,
    billing_rate NUMERIC(10,2) DEFAULT 0,     -- €/h oder €/Monat
    billing_type TEXT DEFAULT 'monthly' CHECK (billing_type IN ('hourly', 'monthly', 'project', 'revenue_share')),
    markup_percent NUMERIC(5,2) DEFAULT 20.00,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ──────────────────────────────────────────────
-- 5. PROJEKT-SERVICE-ZUORDNUNG (mit Kosten)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.project_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.customer_projects(id) ON DELETE CASCADE,
    service_id UUID REFERENCES public.services(id),
    is_active BOOLEAN DEFAULT true,
    usage_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(project_id, service_id)
);

-- ──────────────────────────────────────────────
-- 6. KOSTEN-TRACKING (monatliche Abrechnung)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.cost_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.customer_projects(id) ON DELETE CASCADE,
    service_id UUID REFERENCES public.services(id),
    billing_month DATE NOT NULL,
    cost_net NUMERIC(12,4) NOT NULL,         -- Nettokosten (was wir zahlen)
    cost_markup NUMERIC(12,4) NOT NULL,      -- Aufschlag (20%)
    cost_gross NUMERIC(12,4) NOT NULL,       -- Brutto (was Kunde zahlt)
    usage_unit TEXT,                          -- tokens, requests, gb, hours
    usage_amount NUMERIC(12,2),
    notes TEXT,
    recorded_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(project_id, service_id, billing_month)
);

-- ──────────────────────────────────────────────
-- 7. PROJECT SECRETS (kunden-spezifische Keys)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.project_secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.customer_projects(id) ON DELETE CASCADE,
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL,
    key_type TEXT DEFAULT 'api_key',
    environment TEXT DEFAULT 'production',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(project_id, key_name, environment)
);

-- ──────────────────────────────────────────────
-- 8. DOKUMENTATIONS-INDEX (MASTER TOC)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.doc_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_path TEXT NOT NULL UNIQUE,            -- relativer Pfad in docs/
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,                    -- system, governance, legal, infrastructure, architecture, operations, adrs, policies, systems
    tags TEXT[] DEFAULT '{}',
    is_synced_to_brain BOOLEAN DEFAULT false,
    last_synced_at TIMESTAMPTZ,
    checksum TEXT,                            -- SHA256 des Inhalts
    version INTEGER DEFAULT 1,
    file_size_bytes INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ──────────────────────────────────────────────
-- RLS POLICIES
-- ──────────────────────────────────────────────

-- Secrets: nur admin/staff
ALTER TABLE public.secrets_vault ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_secrets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cost_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.services ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.service_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_services ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doc_index ENABLE ROW LEVEL SECURITY;

-- Secrets: nur Staff mit is_admin Berechtigung
CREATE POLICY secrets_staff_only ON public.secrets_vault FOR ALL TO authenticated
    USING (is_staff(auth.uid()) AND EXISTS (
        SELECT 1 FROM public.profiles WHERE user_id = auth.uid() AND role = 'admin'
    ));

-- Projekt-Secrets: Projekt-Member + Staff
CREATE POLICY project_secrets_access ON public.project_secrets FOR ALL TO authenticated
    USING (is_staff(auth.uid()) OR project_id IN (
        SELECT id FROM public.customer_projects WHERE id = project_id
    ));

-- Kosten: Staff + Projekt-Member (read-only für member)
CREATE POLICY cost_tracking_staff_all ON public.cost_tracking FOR ALL TO authenticated
    USING (is_staff(auth.uid()));
CREATE POLICY cost_tracking_project_read ON public.cost_tracking FOR SELECT TO authenticated
    USING (project_id IN (
        SELECT id FROM public.customer_projects WHERE is_internal = false
    ));

-- Doc-Index: öffentlich lesbar
CREATE POLICY doc_index_select ON public.doc_index FOR SELECT TO anon, authenticated
    USING (true);
CREATE POLICY doc_index_staff_all ON public.doc_index FOR ALL TO authenticated
    USING (is_staff(auth.uid()));

-- Helper: Umsatzberechnung mit 20% Aufschlag
CREATE OR REPLACE FUNCTION calculate_markup(
    p_cost_net NUMERIC,
    p_markup_percent NUMERIC DEFAULT 20.00
) RETURNS NUMERIC AS $$
BEGIN
    RETURN ROUND(p_cost_net * (1 + p_markup_percent / 100), 4);
END;
$$ LANGUAGE plpgsql STABLE;

-- Billing Report View
CREATE OR REPLACE VIEW public.customer_billing_report AS
SELECT
    cp.id AS project_id,
    cp.name AS project_name,
    cp.customer_name,
    ct.billing_month,
    SUM(ct.cost_net) AS total_cost_net,
    SUM(ct.cost_markup) AS total_markup,
    SUM(ct.cost_gross) AS total_gross,
    COUNT(DISTINCT ct.service_id) AS services_used
FROM public.customer_projects cp
JOIN public.cost_tracking ct ON ct.project_id = cp.id
GROUP BY cp.id, cp.name, cp.customer_name, ct.billing_month
ORDER BY ct.billing_month DESC, cp.name;

END;
