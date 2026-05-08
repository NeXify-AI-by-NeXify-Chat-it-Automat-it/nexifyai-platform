# Deprecation Policy
# DOS v2.0 Chapter 33: Migrations- & Deprecation-Policies

## API-Deprecation

| Phase | Frist | Aktion |
|---|---|---|
| Ankündigung | T-90 Tage | `Deprecation: true` Header + Changelog |
| Warning | T-60 Tage | `Sunset: [Datum]` Header + E-Mail an Nutzer |
| Sunset | T-0 | Endpunkt entfernt (nur mit MAJOR-Version) |

## Migration-Window

- **Standard:** 90 Tage nach Deprecation-Ankündigung
- **Security-kritisch:** 30 Tage
- **Breaking Changes:** Nur mit MAJOR-Version, min. 90 Tage Vorlauf

## Version-Support-Matrix

| Version | Support |
|---|---|
| Aktuelle MAJOR | Voll-Support (Features, Fixes) |
| Vorherige MAJOR | Security-Patches (6 Monate) |
| Älter | Kein Support |

## Kommunikation

- Changelog in `/CHANGELOG.md`
- Breaking Changes fett markiert
- Migration-Guide für MAJOR-Upgrades
- E-Mail an betroffene Tenant-Admins bei Breaking Changes
