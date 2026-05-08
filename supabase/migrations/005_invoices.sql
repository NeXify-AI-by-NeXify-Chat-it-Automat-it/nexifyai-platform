-- Phase 1: Migration 005 — invoices, transactions (nur Staff)
CREATE TABLE IF NOT EXISTS public.invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id),
    number TEXT NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft','sent','paid','overdue','cancelled')),
    total NUMERIC(12,2) NOT NULL DEFAULT 0,
    currency TEXT DEFAULT 'EUR',
    due_date DATE,
    paid_at TIMESTAMPTZ,
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES public.invoices(id),
    type TEXT DEFAULT 'payment' CHECK (type IN ('payment','refund','charge','credit')),
    amount NUMERIC(12,2) NOT NULL,
    currency TEXT DEFAULT 'EUR',
    provider TEXT,
    provider_tx_id TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending','completed','failed','reversed')),
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY inv_staff ON public.invoices FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
CREATE POLICY tx_staff ON public.transactions FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE user_id=auth.uid() AND role IN ('staff','admin')));
