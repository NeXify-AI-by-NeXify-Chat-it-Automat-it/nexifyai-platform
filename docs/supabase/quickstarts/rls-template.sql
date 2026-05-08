-- Quickstart: RLS-Template für neue Multi-Tenant-Tabellen
-- Dieses Template ist bei JEDER neuen Tabelle anzuwenden.

-- Hilfsfunktion: Prüft ob User Staff/Admin ist
create or replace function is_staff(uid uuid)
returns boolean as $$
  select exists (select 1 from profiles where user_id = uid and role in ('staff','admin'));
$$ language sql stable;

-- Hilfsfunktion: Prüft Tenant-Zugehörigkeit
create or replace function user_tenant_id(uid uuid)
returns uuid as $$
  select organization_id from profiles where user_id = uid limit 1;
$$ language sql stable;

-- Muster-RLS für Tenant-isolierte Tabellen:
--
-- alter table new_table enable row level security;
--
-- -- Tenant-Isolation: User sieht nur eigene Tenant-Daten
-- create policy "Tenant isolation" on new_table
--   for all using (tenant_id = user_tenant_id(auth.uid()));
--
-- -- Staff/Admin: Full access über alle Tenants
-- create policy "Staff full access" on new_table
--   for all using (is_staff(auth.uid()));
--
-- -- Anon: Kein Zugriff (Default)
-- -- Falls nötig: create policy "Anon can read" on new_table for select to anon using (public = true);
