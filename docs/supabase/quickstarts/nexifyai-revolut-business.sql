-- Quickstart: NeXifyAI Revolut Business Integration v1.0
-- Ersetzt: Stripe (entfernt)
-- Ziel: native Payment-Logik mit Ledger-Hintergrund gemäß Leitfassung
-- Ref: https://developer.revolut.com/docs/merchant/merchant-api

-- 1. Tabelle für Revolut-Orders (statt Stripe Payment Intents)
create table if not exists revolut_orders (
  id uuid primary key default gen_random_uuid(),
  internal_order_id uuid not null references invoices(id),
  revolut_order_id text unique,
  revolut_order_token text,          -- Einmal-Token für Client-SDK
  amount numeric not null,
  currency text not null default 'EUR',
  status text not null default 'PENDING' check (status in ('PENDING','AUTHORISED','COMPLETED','FAILED','CANCELLED')),
  description text,
  customer_email text,
  metadata jsonb default '{}',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 2. Webhook-Events von Revolut
create table if not exists revolut_webhook_events (
  id uuid primary key default gen_random_uuid(),
  event_type text not null,          -- ORDER_COMPLETED, ORDER_AUTHORISED, ORDER_FAILED
  payload jsonb,
  processed boolean default false,
  received_at timestamptz default now(),
  processed_at timestamptz
);

-- 3. Revolut Merchant Config (pro Organization)
create table if not exists revolut_configs (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid references organizations(id) unique,
  revolut_merchant_id text,
  api_key_encrypted text,            -- Verschlüsselt, nie plaintext
  webhook_secret text,               -- Für HMAC-Validierung
  enabled boolean default false,
  sandbox boolean default true,
  default_currency text default 'EUR',
  settlement_iban text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- RLS
alter table revolut_orders enable row level security;
alter table revolut_webhook_events enable row level security;
alter table revolut_configs enable row level security;

create policy "Staff full access" on revolut_orders
  for all using (is_staff(auth.uid()));
create policy "Staff full access" on revolut_webhook_events
  for all using (is_staff(auth.uid()));
create policy "Staff full access" on revolut_configs
  for all using (is_staff(auth.uid()));

-- Index
create index if not exists idx_revolut_orders_internal on revolut_orders(internal_order_id);
create index if not exists idx_revolut_webhook_type on revolut_webhook_events(event_type);
