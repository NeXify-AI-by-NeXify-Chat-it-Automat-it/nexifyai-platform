-- Quickstart: Audit-Log-Baseline (DOS v2.0 Kap. 14 Security)
-- Append-only Tabelle für alle Datenzugriffe und Änderungen

create table if not exists audit_logs (
  id uuid primary key default gen_random_uuid(),
  action text not null,         -- INSERT, UPDATE, DELETE, SELECT
  table_name text,
  record_id uuid,
  old_data jsonb,
  new_data jsonb,
  performed_by uuid references auth.users,
  ip_address text,
  performed_at timestamptz default now()
);

alter table audit_logs enable row level security;

-- Append-only: nur INSERT erlaubt, kein UPDATE/DELETE
create policy "Append only" on audit_logs
  for insert to authenticated with check (true);

-- Staff/Admin: SELECT erlaubt
create policy "Staff can read audit_logs" on audit_logs
  for select using (exists (select 1 from profiles where user_id = auth.uid() and role in ('staff','admin')));

-- Automatischer Trigger für Kern-Tabellen (Beispiel: organizations)
create or replace function audit_organizations()
returns trigger as $$
begin
  insert into audit_logs (action, table_name, record_id, old_data, new_data, performed_by)
  values (TG_OP, 'organizations', coalesce(NEW.id, OLD.id),
          case when TG_OP in ('UPDATE','DELETE') then to_jsonb(OLD) else null end,
          case when TG_OP in ('INSERT','UPDATE') then to_jsonb(NEW) else null end,
          auth.uid());
  return coalesce(NEW, OLD);
end;
$$ language plpgsql security definer;

-- Trigger an organizations binden (Vorbild für andere Kern-Tabellen)
-- drop trigger if exists trg_audit_organizations on organizations;
-- create trigger trg_audit_organizations after insert or update or delete on organizations
--   for each row execute function audit_organizations();
