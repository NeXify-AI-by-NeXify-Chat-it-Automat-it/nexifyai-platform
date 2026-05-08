-- Quickstart: Feature-Flag-Baseline für saubere Rollouts

create table if not exists feature_flags (
  id uuid primary key default gen_random_uuid(),
  flag_name text unique not null,
  enabled boolean default false,
  tenant_id uuid references tenants(id) null,  -- null = global
  rollout_percentage int default 0 check (rollout_percentage between 0 and 100),
  description text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table feature_flags enable row level security;

-- Staff/Admin: Vollzugriff
create policy "Staff full access" on feature_flags
  for all using (exists (select 1 from profiles where user_id = auth.uid() and role in ('staff','admin')));

-- Portal: Nur lesend auf enabled flags
create policy "Portal reads enabled flags" on feature_flags
  for select to authenticated using (enabled = true);

-- Helper: Feature-Flag prüfen (für Edge Functions / API Routes)
create or replace function is_feature_enabled(flag text, tid uuid default null)
returns boolean as $$
  select exists (select 1 from feature_flags where flag_name = flag and enabled = true
    and (tenant_id is null or tenant_id = tid));
$$ language sql stable;
