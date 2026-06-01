# Backup & Retention Policy

**Status:** active | **Version:** 1.0 | **Date:** 2026-05-27
**Classification:** INTERN – VERTRAULICH
**Owner:** NeXifyAI (KI-Lead)

## 1. Purpose

Prevent backup sprawl, disk waste, and stale-data confusion.
Comply with DOS v2.0 §Zero Information Loss — noise excluded, signal retained.

## 2. Retention Rules

| Type | Max Copies | Max Age | Location | Notes |
|------|-----------|---------|----------|-------|
| Pre-mutation snapshot | 3 | 7 days | `/root/branding-backup-*` | Keep latest 3 only, purge older |
| Git-backed repo snapshots | 0 (use git) | N/A | `/root/*-backup-*/` | Forbidden: git is canonical |
| Service backup (Qdrant) | 2 | 7 days | `/root/qdrant_backups/` | Rotate oldest on new |
| Audit snapshot | 1 current | 24h stale → re-probe | `/root/system-audit-*` | Symlink to latest current |
| Temp/scan files | 0 | N/A | `/root/scan_result_*` | Delete after use |
| Config .bak | 0 (use git) | N/A | Any `*.bak*` file | Forbidden: commit or discard |

## 3. Format Rules

- **NO** compiled artifacts in backups (`__pycache__`, `.venv`, `node_modules`)
- **NO** secrets in backups
- **NO** ad-hoc tarball backups if git exists
- Backup naming: `{scope}-backup-{YYYYMMDD}_{HHMM}-{reason}/`

## 4. Validation (per Operational Constitution §III)

Every backup MUST be validated post-creation:
1. Size check (not 0 bytes, not implausibly small/large)
2. Integrity check (tar -tf for tarballs, `git fsck` for repos)
3. Restoration test (verify contents match pre-backup state)
4. Document in `/tmp/backup-validation-{timestamp}.log`

## 5. Cleanup Schedule

- Daily (cron): purge temp/scan files
- Weekly (sunday 03:00): rotate backups per retention rules
- Monthly: full audit of all backup directories

## 6. Violations

Backup without validation = process violation (CI-blocking per Constitution §IV).
Ad-hoc .bak files not in git = design drift (CI-blocking).
