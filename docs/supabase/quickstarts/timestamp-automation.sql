-- Quickstart: Timestamp-Automation für created_at/updated_at
-- Wendbar auf ALLE Tabellen per Trigger

create or replace function set_timestamp()
returns trigger as $$
begin
  if TG_OP = 'INSERT' then
    NEW.created_at = coalesce(NEW.created_at, now());
  end if;
  NEW.updated_at = now();
  return NEW;
end;
$$ language plpgsql;

-- Anwendung auf eine neue Tabelle:
-- create trigger trg_new_table_timestamp
--   before insert or update on new_table
--   for each row execute function set_timestamp();
--
-- Bestehende Tabellen (die bereits created_at/updated_at haben):
-- Nur Trigger anlegen, Spalten existieren bereits
