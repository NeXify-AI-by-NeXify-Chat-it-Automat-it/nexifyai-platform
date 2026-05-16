"""
NeXifyAI — Brain Migration Runner
Idempotent, append-only, auditierbar.

Usage:
    from backend.brain.migrate import apply_migrations, get_current_version
    apply_migrations()
    print(f"Brain schema v{get_current_version()}")
"""

import os
import sqlite3
from datetime import datetime, timezone
from typing import List, Tuple

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
BRAIN_DB_PATH = "/opt/data/brain/brain.db"


def get_current_version() -> int:
    """Get current brain schema version. Returns 0 if unversioned."""
    try:
        conn = sqlite3.connect(BRAIN_DB_PATH)
        cursor = conn.cursor()

        # Check if schema_version table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='brain_schema_version'"
        )
        if not cursor.fetchone():
            conn.close()
            return 0

        cursor.execute("SELECT MAX(version) FROM brain_schema_version")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else 0
    except Exception as e:
        print(f"[brain] get_current_version error: {e}")
        return 0


def _discover_migrations() -> List[Tuple[int, str, str]]:
    """Discover migration files in MIGRATIONS_DIR. Returns [(version, filename, path)]."""
    migrations = []
    
    if not os.path.exists(MIGRATIONS_DIR):
        return migrations
    
    for fname in sorted(os.listdir(MIGRATIONS_DIR)):
        if not fname.endswith(".sql"):
            continue
        
        # Parse version from filename: 001_initial.sql → 1
        try:
            version = int(fname.split("_")[0])
        except ValueError:
            continue
        
        description = fname.replace(".sql", "").replace(f"{version:03d}_", "").replace("_", " ")
        
        path = os.path.join(MIGRATIONS_DIR, fname)
        migrations.append((version, description, path))
    
    return sorted(migrations, key=lambda x: x[0])


def apply_migrations() -> List[Tuple[int, str]]:
    """
    Apply all pending migrations in order.
    Returns list of (version, description) tuples for applied migrations.
    """
    current = get_current_version()
    migrations = _discover_migrations()
    applied = []

    conn = sqlite3.connect(BRAIN_DB_PATH)
    cursor = conn.cursor()

    # Ensure schema_version table exists (idempotent bootstrap)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brain_schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL,
            description TEXT
        )
    """)

    for version, description, path in migrations:
        if version <= current:
            continue

        # Read and execute migration
        with open(path) as f:
            sql = f.read()

        try:
            cursor.executescript(sql)
            cursor.execute(
                "INSERT INTO brain_schema_version (version, applied_at, description) VALUES (?, ?, ?)",
                (version, datetime.now(timezone.utc).isoformat(), description),
            )
            conn.commit()
            applied.append((version, description))
            print(f"[brain] Migration {version:03d} applied: {description}")
        except Exception as e:
            print(f"[brain] Migration {version:03d} FAILED: {e}")
            conn.rollback()
            break  # Stop on failure — don't apply further migrations

    conn.close()
    return applied


def get_migration_status() -> dict:
    """Get full migration status for diagnostics."""
    current = get_current_version()
    all_migrations = _discover_migrations()
    total = len(all_migrations)
    applied_count = sum(1 for v, _, _ in all_migrations if v <= current)

    return {
        "current_version": current,
        "total_migrations": total,
        "applied_migrations": applied_count,
        "pending_migrations": total - applied_count,
        "migration_dir": MIGRATIONS_DIR,
    }
