-- Quickstart: Event-Tracking-Baseline (DOS v2.0 Kap. 11)
-- Nutzt Supabase-Postgres statt MongoDB analog zu analytics_routes.py

create table if not exists analytics_events (
  id uuid primary key default gen_random_uuid(),
  event_name text not null,
  payload jsonb,
  user_id uuid references auth.users,
  session_id text,
  ip_address text,  -- anonymisiert (letztes Oktett genullt)
  user_agent text,
  timestamp timestamptz default now(),
  created_at timestamptz default now()
);

alter table analytics_events enable row level security;

-- Portal: sieht nur eigene Events
create policy "User sees own events" on analytics_events
  for select using (auth.uid() = user_id);

-- Staff/Admin: sieht alle Events
create policy "Staff sees all events" on analytics_events
  for select using (exists (select 1 from profiles where user_id = auth.uid() and role in ('staff','admin')));

-- Anon: kann Events schreiben (für client-seitiges Tracking)
create policy "Anon can insert events" on analytics_events
  for insert to anon with check (true);

-- Index für Health-Score Queries
create index if not exists idx_analytics_ts on analytics_events(timestamp desc);
create index if not exists idx_analytics_event on analytics_events(event_name, timestamp desc);
