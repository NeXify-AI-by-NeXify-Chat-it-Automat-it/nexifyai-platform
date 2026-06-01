# ADR-024: Secrets Vault — pgcrypto-basierte Secret-Verschlüsselung in Supabase

**Status:** accepted
**Datum:** 2026-05-21
**Autor:** Security-Agent / Subagent-ID 20260521_66
**Stakeholder:** Alle Entwickler, DevOps, CTO, Security-Team

## Kontext

Die NeXifyAI-Plattform betreibt eine Multi-Service-Architektur mit zahlreichen externen API-Integrationen (NeXify, OpenRouter, MindsDB, Qdrant, Resend etc.) sowie internen Infrastruktur-Komponenten (Supabase, Redis, Traefik, Loki, Grafana). Jeder dieser Services benötigt Credentials (API-Keys, Passwörter, Tokens, JWT-Secrets), die sicher gespeichert und verwaltet werden müssen.

Die aktuelle Situation (vor dieser Implementierung) war:

1. **Hartcodierte Secrets** im Code (festgestellt durch ADR-018 und Security-Audit)
2. **Klartext-Secrets** in der Datenbank (Migration 015 speichert `key_value` unverschlüsselt)
3. **Keine zentrale Secrets-Verwaltung** — Credentials waren über `.env`-Dateien, Docker-Configs und Code verstreut
4. **Keine Rotation** — Secrets hatten kein Ablaufdatum und wurden nie rotiert
5. **Keine Audit-Trail** — Änderungen an Secrets wurden nicht protokolliert

Der bestehende ADR-018 (Secret-Management) empfiehlt bereits **Umgebungsvariablen + Supabase Vault (pgcrypto)** als primäre Strategie. Diese ADR beschreibt die konkrete Implementierung.

## Problem

Wie können alle Service-Credentials zentral, sicher, auditierbar und rotationsfähig in der Supabase PostgreSQL-Datenbank gespeichert werden, ohne dass Klartext-Secrets in der Datenbank, in Code-Repositories oder in Backup-Dumps sichtbar sind?

Konkrete Anforderungen:

1. **Verschlüsselung at Rest** — Secrets müssen mit starken kryptographischen Verfahren in der DB gespeichert werden
2. **Automatische Verschlüsselung** — Entwickler dürfen nicht manuell encrypt() aufrufen müssen
3. **Zugriffskontrolle** — Nur Admins + Backend (service_role) dürfen Secrets lesen/schreiben
4. **Rotation** — Master-Key und einzelne Secrets müssen ohne Ausfallzeit rotiert werden können
5. **Audit-Trail** — Jede Änderung an Secrets muss protokolliert werden
6. **Migration** — Bestehende Klartext-Secrets müssen nachträglich verschlüsselt werden können
7. **Health-Check** — Der Verschlüsselungsstatus muss jederzeit überprüfbar sein

## Optionen

1. **Option A: pgcrypto + vault-Schema** (Gewählt)
   - Pro: Keine externe Abhängigkeit, vollständig in Supabase integriert, auditable Trigger
   - Pro: Nutzt `pgp_sym_encrypt` (OpenPGP-konform, starke Verschlüsselung)
   - Pro: SECURITY DEFINER Funktionen für granulare Zugriffskontrolle
   - Contra: Master-Key liegt in PostgreSQL-Config (`app.settings.vault_key`)

2. **Option B: HashiCorp Vault**
   - Pro: Enterprise-Grade, Auto-Unsealing, dynamische Secrets
   - Contra: Overhead für die aktuelle Größe, zusätzlicher Service, Betriebskosten
   - Contra: Setup-Komplexität, erfordert zusätzlichen Container

3. **Option C: AWS Secrets Manager / Azure Key Vault**
   - Pro: Managed Service, automatische Rotation
   - Contra: Cloud-Lock-in, monatliche Kosten, Latenz bei jedem Zugriff
   - Contra: Widerspricht On-Premise-Strategie (self-hosted EU-VPS)

4. **Option D: Nur Umgebungsvariablen + .env**
   - Pro: Einfach
   - Contra: Keine Persistenz in der DB, kein Audit, keine Rotation, Backup-Probleme

## Entscheidung

**Option A: pgcrypto + vault-Schema in Supabase PostgreSQL**

Die Implementierung umfasst:

### Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    vault-Schema (isoliert)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  vault.secrets                                         │ │
│  │  ┌───────┬────────────┬──────────────────┬──────────┐ │ │
│  │  │  id   │   secret   │ encrypted_secret │ category │ │ │
│  │  ├───────┼────────────┼──────────────────┼──────────┤ │ │
│  │  │ UUID  │ Klartext*  │ 🔒 pgp_sym_encrypt│ api_key  │ │ │
│  │  └───────┴────────────┴──────────────────┴──────────┘ │ │
│  │                          ↑                              │ │
│  │              auto_encrypt_trigger()                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Zugriff:                                                     │
│  • vault.encrypt_secret() – SECURITY DEFINER                  │
│  • vault.decrypt_secret() – SECURITY DEFINER                  │
│  • vault.get_secret()     – SECURITY DEFINER (Backend)        │
│                                                              │
│  Master-Key: app.settings.vault_key (ALTER SYSTEM SET)        │
└─────────────────────────────────────────────────────────────┘
```

### Tabellen (public Schema)
- `service_categories` — Kategorisierung (LLM, Database, Infrastruktur etc.)
- `services` — Konkrete Dienste (NeXify, Supabase, Redis etc.)
- `secrets_vault` — Verschlüsselte Credentials (auto-encrypted via Trigger)
- `customer_projects` — Kundenprojekte für Cost-Tracking
- `project_services` — Projekt-Service-Zuordnung
- `cost_tracking` — Monatliche Abrechnungsdaten
- `project_secrets` — Kundenspezifische Secrets
- `doc_index` — Dokumentationsindex

### vault-Schema
- `vault.secrets` — Zentrale, verschlüsselte Secrets-Tabelle (UNIQUE on name)
- `vault.encrypt_secret(text, key_name)` — Verschlüsselungsfunktion
- `vault.decrypt_secret(ciphertext)` — Entschlüsselungsfunktion
- `vault.get_secret(p_name)` — Sichere Abfrage (nur Backend/service_role)
- `vault.auto_encrypt_trigger()` — Automatische Verschlüsselung bei INSERT/UPDATE
- `vault.secrets_overview` — View ohne Klartext-Spalten
- `vault.health_check()` — Vollständiger Verschlüsselungs-Health-Check
- `vault.set_vault_key(text)` — Superuser-only Key-Set
- `vault.rotate_vault_key(old, new)` — Key-Rotation mit Neuverschlüsselung aller Secrets
- `vault.due_for_rotation()` — Fällige Rotationen anzeigen
- `vault.audit_secret_changes()` — Audit-Trigger für Secret-Änderungen
- `vault.migrate_plaintext_secrets()` — Nachträgliche Verschlüsselung
- `vault.migrate_from_public_vault()` — Migration von public.secrets_vault

### Sicherheitsmechanismen
1. **pgcrypto** — `pgp_sym_encrypt()` mit AES-256 via OpenPGP-Format
2. **SECURITY DEFINER** — Funktionen laufen mit Superuser-Rechten
3. **RLS** — Row-Level-Security auf allen Tabellen
4. **Trigger** — Erzwingt automatische Verschlüsselung, kein manuelles encrypt nötig
5. **Isoliertes Schema** — `vault`-Schema getrennt von `public`
6. **Views statt direkter Abfragen** — `vault.secrets_overview` zeigt niemals Klartext

## Konsequenzen

### Positiv
- 🔒 **Keine Klartext-Secrets** in der Datenbank — Backup-Dumps sind sicher
- 🔒 **Keine hartcodierten Secrets** im Code — ADR-018 wird umgesetzt
- 🔒 **Automatische Verschlüsselung** — Entwickler können Secrets nicht versehentlich im Klartext speichern
- 🔒 **Rotation-fähig** — `vault.rotate_vault_key()` erlaubt Schlüsselwechsel ohne Ausfallzeit
- 🔒 **Audit-Trail** — Jede Secret-Änderung wird in `audit_logs` protokolliert
- 🔒 **Health-Check** — `vault.health_check()` testet pgcrypto + Key + Roundtrip
- ✅ **Kostenlos** — Keine zusätzlichen Lizenzkosten, läuft in Supabase PostgreSQL
- ✅ **ISO 27001-konform** — A.8.2 (Informationsklassifizierung), A.8.24 (Schlüsselmanagement)
- ✅ **DSGVO Art. 32** — Geeignete technische Maßnahmen zum Schutz personenbezogener Daten

### Negativ
- ⏱️ **Master-Key muss bei Deployment gesetzt werden** — Manueller Schritt nach jedem DB-Reset
- ⏱️ **Key-Verlust = Datenverlust** — Ohne Master-Key sind alle Secrets unwiderruflich verschlüsselt
- 📋 **Kein dynamisches Secrets** — HashiCorp Vault könnte dynamische DB-Passwörter generieren
- 📋 **Backup des Master-Keys erforderlich** — Muss in einem separaten Secret-Manager gesichert werden

### Neutral
- Baut auf bestehendem pgcrypto auf (wird bereits in anderen Migrationen genutzt)
- Nutzt `current_setting('app.settings.*')` für SQL-Zugriff (kein File-System-Zugriff nötig)
- Service-Katalog wird via Seed-Migration (021) initial befüllt
- Kompatibel mit bestehenden Tools und Backup-Strategien

## Implementierung

### Dateien

| Datei | Beschreibung |
|---|---|
| `supabase/migrations/020_secrets_vault_complete.sql` | Konsolidierte Roll-Up Migration (Tabellen, Funktionen, Trigger, RLS, Views) |
| `supabase/migrations/021_seed_service_catalog.sql` | Seed der Standard-Services (NeXify, Supabase, Redis etc.) |
| `scripts/generate_vault_key.sh` | Master-Key Generator (512 Bit, Base64/Hex/Raw) |

### Setup-Schritte

```bash
# 1. Migration ausführen
psql <DATABASE_URL> -f supabase/migrations/020_secrets_vault_complete.sql
psql <DATABASE_URL> -f supabase/migrations/021_seed_service_catalog.sql

# 2. Master-Key generieren
./scripts/generate_vault_key.sh --length 64 --format base64

# 3. Key in Supabase setzen
psql <DATABASE_URL> -c "SELECT vault.set_vault_key('<generated-key>');"

# 4. Health-Check
psql <DATABASE_URL> -c "SELECT * FROM vault.health_check();"

# 5. Vorhandene Secrets migrieren (falls öffentliche secrets_vault existieren)
psql <DATABASE_URL> -c "SELECT vault.migrate_from_public_vault();"
psql <DATABASE_URL> -c "SELECT vault.migrate_plaintext_secrets();"
```

## Rollback-Plan

1. **Rückbau der vault-Infrastruktur:**
   ```sql
   -- Rollback siehe Ende von 020_secrets_vault_complete.sql
   DROP TRIGGER IF EXISTS trg_vault_auto_encrypt ON vault.secrets;
   DROP TABLE IF EXISTS vault.secrets CASCADE;
   DROP SCHEMA IF EXISTS vault;
   ```

2. **Falls Master-Key verloren geht:**
   - Alle verschlüsselten Secrets sind unwiderruflich verloren
   - Neue API-Keys müssen bei allen Providern neu generiert werden
   - **Prävention:** Master-Key in Bitwarden/1Password + offline Backup

3. **Alternative Strategie:**
   - Umstellung auf HashiCorp Vault möglich (zukünftiger ADR)
   - Fallback auf Umgebungsvariablen (wie in ADR-018 beschrieben)

## Verweise

- [ADR-018: Secret-Management](/docs/adrs/ADR-018-secret-management.md) — Vorläufer-ADR
- [Migration 020](/supabase/migrations/020_secrets_vault_complete.sql) — Vollständige Implementierung
- [Migration 021](/supabase/migrations/021_seed_service_catalog.sql) — Service-Katalog Seed
- [generate_vault_key.sh](/scripts/generate_vault_key.sh) — Master-Key Generator
- [Migration 015](/supabase/migrations/015_secrets_vault.sql) — Ursprüngliche Secrets-Vault-Tabellen
- [vault_encryption.sql](/supabase/migrations/20260521_vault_encryption.sql) — pgcrypto-Encryption-Migration
- [fix_rls_drift.sql](/supabase/migrations/20260521_fix_rls_drift.sql) — RLS-Drift-Fix
- ISO 27001:2022 A.8.2, A.8.24 — Schlüsselmanagement
- DSGVO Art. 32 — Technische und organisatorische Maßnahmen
- OWASP Top 10 A05:2021 — Security Misconfiguration
- [Systeminventar](/docs/system/systeminventar.md) — Übersicht aller Services
