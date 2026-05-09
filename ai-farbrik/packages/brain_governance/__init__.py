"""
NeXifyAI — Brain Governance Layer (Phase 0.3)

The Brain is NOT a feature. It IS the company.

This layer governs ALL brain operations:
  - Retrieval Governance (who can read what)
  - Write Governance (who can write what, with what confidence)
  - Reconciliation (conflict detection + resolution)
  - Memory Lifecycle (retention, decay, expiration)
  - Trust Scoring (source reliability, corroboration)
  - Audit Trail (every read + write logged)

Mandatory agents (Phase 2):
  - AI-Brain-Governor   — retrieval/write gatekeeper
  - AI-Auditor          — truth verification, hallucination detection
  - AI-Reconciliation    — conflict resolution
  - AI-Memory-Manager   — lifecycle, retention policies
  - AI-Retrieval        — governed semantic search

NO: direct brain writes, unvalidated embeddings, unstructured memories
YES: governed, attributed, versioned, auditable cognitive operations
"""
import json
import time
import uuid
import sqlite3
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════
# BRAIN GOVERNANCE TYPES
# ═══════════════════════════════════════════════════

class AccessLevel(Enum):
    """Who can access what in the brain."""
    PUBLIC = "public"           # Anyone can read
    AGENT = "agent"             # Authenticated agents only
    GOVERNED = "governed"       # Requires capability token
    RESTRICTED = "restricted"   # Requires explicit approval
    CEO_ONLY = "ceo_only"       # Pascal only

class WritePolicy(Enum):
    """How writes are governed."""
    ANY = "any"                           # Unrestricted (deprecated)
    ATTRIBUTED = "attributed"             # Must have source attribution
    CORROBORATED = "corroborated"         # Must be confirmed by another source
    GOVERNED = "governed"                 # Requires governance approval
    BLOCKED = "blocked"                   # Only via reconciliation

class TrustLevel(Enum):
    """How much we trust a source."""
    UNTRUSTED = 0.0
    LOW = 0.2
    MEDIUM = 0.5
    HIGH = 0.8
    CANONICAL = 1.0

@dataclass
class BrainAccessRule:
    """A rule governing brain access."""
    rule_id: str = field(default_factory=lambda: f"bar_{uuid.uuid4().hex[:8]}")
    category: str = "*"                    # Which memory category
    access_level: AccessLevel = AccessLevel.AGENT
    write_policy: WritePolicy = WritePolicy.ATTRIBUTED
    required_capability: str = ""          # e.g., "brain.write"
    min_confidence: float = 0.3
    sources_allowed: List[str] = field(default_factory=list)  # Empty = all
    sources_blocked: List[str] = field(default_factory=list)

@dataclass
class BrainAuditEntry:
    """Every brain operation is logged."""
    audit_id: str = field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:12]}")
    operation: str = ""                    # "read", "write", "update", "delete"
    memory_id: str = ""
    category: str = ""
    actor: str = ""                        # agent_id or "system"
    capability_used: str = ""
    approved: bool = False
    denied_reason: str = ""
    timestamp: float = field(default_factory=time.time)


# ═══════════════════════════════════════════════════
# BRAIN GOVERNOR
# ═══════════════════════════════════════════════════

class BrainGovernor:
    """
    The gatekeeper for ALL brain operations.

    Every read and write must pass through:
      check_read_access() → check_write_policy() → audit()

    NO direct SQL queries to brain.db bypassing this layer.
    """

    def __init__(self, brain_db_path: str = "/opt/data/brain/brain.db",
                 audit_db_path: str = "/opt/data/brain/audits/brain_audit.db"):
        self.brain_db_path = brain_db_path
        self.audit_db_path = audit_db_path
        os.makedirs(os.path.dirname(audit_db_path), exist_ok=True)
        self.rules: Dict[str, BrainAccessRule] = {}
        self._audit_log: List[BrainAuditEntry] = []
        self._register_default_rules()
        self._init_audit_db()

    def _register_default_rules(self):
        """Register default access rules."""
        defaults = [
            # Knowledge: PUBLIC read, ATTRIBUTED write
            BrainAccessRule("knowledge", "knowledge",
                AccessLevel.PUBLIC, WritePolicy.ATTRIBUTED),
            # Governance: RESTRICTED read, GOVERNED write
            BrainAccessRule("governance", "governance",
                AccessLevel.RESTRICTED, WritePolicy.GOVERNED,
                required_capability="brain.governance"),
            # Incidents: AGENT read, CORROBORATED write
            BrainAccessRule("incidents", "incident",
                AccessLevel.AGENT, WritePolicy.CORROBORATED),
            # Decisions: RESTRICTED read, GOVERNED write
            BrainAccessRule("decisions", "decision",
                AccessLevel.RESTRICTED, WritePolicy.GOVERNED,
                required_capability="brain.decide"),
            # Facts: AGENT read, CORROBORATED write
            BrainAccessRule("facts", "fact",
                AccessLevel.AGENT, WritePolicy.CORROBORATED,
                sources_blocked=["unverified_llm", "scraped_web"]),
            # Events: AGENT read, ATTRIBUTED write
            BrainAccessRule("events", "event",
                AccessLevel.AGENT, WritePolicy.ATTRIBUTED),
            # Default: AGENT read, ATTRIBUTED write
            BrainAccessRule("*", "*",
                AccessLevel.AGENT, WritePolicy.ATTRIBUTED),
        ]
        for rule in defaults:
            self.rules[rule.rule_id] = rule

    def _init_audit_db(self):
        """Initialize audit database."""
        db = sqlite3.connect(self.audit_db_path)
        db.execute("""
            CREATE TABLE IF NOT EXISTS brain_audit (
                audit_id TEXT PRIMARY KEY,
                operation TEXT NOT NULL,
                memory_id TEXT DEFAULT '',
                category TEXT DEFAULT '',
                actor TEXT NOT NULL,
                capability_used TEXT DEFAULT '',
                approved INTEGER DEFAULT 0,
                denied_reason TEXT DEFAULT '',
                timestamp REAL NOT NULL
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_audit_actor ON brain_audit(actor)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON brain_audit(timestamp)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_audit_op ON brain_audit(operation)")
        db.commit()
        db.close()

    # ── READ GOVERNANCE ──

    def check_read_access(self, category: str, actor: str,
                          capabilities: List[str] = None) -> Tuple[bool, str]:
        """
        Check if an actor can READ from a brain category.

        Returns: (allowed, reason)
        """
        capabilities = capabilities or []
        rule = self._find_rule(category)

        # CEO always has access
        if "brain.ceo" in capabilities:
            return True, "CEO access"

        # Check access level
        if rule.access_level == AccessLevel.PUBLIC:
            return True, "Public category"

        if rule.access_level == AccessLevel.AGENT and actor:
            return True, "Agent access"

        if rule.access_level == AccessLevel.GOVERNED:
            if rule.required_capability in capabilities:
                return True, f"Capability {rule.required_capability} granted"
            return False, f"Missing capability: {rule.required_capability}"

        if rule.access_level == AccessLevel.RESTRICTED:
            if "brain.restricted" in capabilities or "brain.ceo" in capabilities:
                return True, "Restricted access granted"
            return False, "Restricted category — requires brain.restricted capability"

        if rule.access_level == AccessLevel.CEO_ONLY:
            if "brain.ceo" in capabilities:
                return True, "CEO access"
            return False, "CEO only"

        return True, "Default allow"

    # ── WRITE GOVERNANCE ──

    def check_write_policy(self, category: str, actor: str, source: str,
                           confidence: float,
                           capabilities: List[str] = None) -> Tuple[bool, str]:
        """
        Check if an actor can WRITE to a brain category.

        Returns: (allowed, reason)
        """
        capabilities = capabilities or []
        rule = self._find_rule(category)

        # Blocked sources
        if source in rule.sources_blocked:
            return False, f"Source '{source}' is blocked for category '{category}'"

        # CEO always has access
        if "brain.ceo" in capabilities:
            return True, "CEO write access"

        # Blocked policy
        if rule.write_policy == WritePolicy.BLOCKED:
            return False, f"Category '{category}' is write-blocked (reconciliation only)"

        # Any — deprecated but functional
        if rule.write_policy == WritePolicy.ANY:
            return True, "Any write allowed (deprecated)"

        # Attributed — must have source
        if rule.write_policy == WritePolicy.ATTRIBUTED:
            if not source:
                return False, "Write requires source attribution"
            if confidence < rule.min_confidence:
                return False, f"Confidence {confidence} below minimum {rule.min_confidence}"
            return True, "Attributed write allowed"

        # Corroborated — needs confirmation
        if rule.write_policy == WritePolicy.CORROBORATED:
            if confidence < 0.6:
                return False, f"Corroborated write requires confidence ≥ 0.6, got {confidence}"
            if not source or source == "unverified":
                return False, "Corroborated write requires verified source"
            return True, "Corroborated write allowed"

        # Governed — requires capability
        if rule.write_policy == WritePolicy.GOVERNED:
            if rule.required_capability and rule.required_capability not in capabilities:
                return False, f"Governed write requires {rule.required_capability}"
            return True, "Governed write approved"

        return True, "Default allow"

    # ── FULL GOVERNANCE CHECK ──

    def govern_read(self, category: str, actor: str,
                    capabilities: List[str] = None) -> BrainAuditEntry:
        """Govern a read operation."""
        allowed, reason = self.check_read_access(category, actor, capabilities)
        entry = BrainAuditEntry(
            operation="read",
            category=category,
            actor=actor,
            approved=allowed,
            denied_reason="" if allowed else reason,
        )
        self._record_audit(entry)
        return entry

    def govern_write(self, category: str, actor: str, source: str,
                     confidence: float, capabilities: List[str] = None,
                     memory_id: str = "") -> BrainAuditEntry:
        """Govern a write operation."""
        allowed, reason = self.check_write_policy(
            category, actor, source, confidence, capabilities
        )
        entry = BrainAuditEntry(
            operation="write",
            memory_id=memory_id,
            category=category,
            actor=actor,
            approved=allowed,
            denied_reason="" if allowed else reason,
        )
        self._record_audit(entry)
        return entry

    # ── AUDIT ──

    def _record_audit(self, entry: BrainAuditEntry):
        """Record an audit entry."""
        self._audit_log.append(entry)

        db = sqlite3.connect(self.audit_db_path)
        db.execute("""
            INSERT INTO brain_audit (audit_id, operation, memory_id, category, actor,
                                     capability_used, approved, denied_reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry.audit_id, entry.operation, entry.memory_id, entry.category,
              entry.actor, entry.capability_used, int(entry.approved),
              entry.denied_reason, entry.timestamp))
        db.commit()
        db.close()

    def get_audit_trail(self, actor: str = "", limit: int = 100) -> List[BrainAuditEntry]:
        """Retrieve audit trail."""
        entries = self._audit_log
        if actor:
            entries = [e for e in entries if e.actor == actor]
        return entries[-limit:]

    def audit_stats(self) -> Dict[str, Any]:
        """Audit statistics."""
        total = len(self._audit_log)
        approved = sum(1 for e in self._audit_log if e.approved)
        denied = total - approved
        by_op = defaultdict(int)
        for e in self._audit_log:
            by_op[e.operation] += 1

        return {
            "total_operations": total,
            "approved": approved,
            "denied": denied,
            "approval_rate": round(approved / max(1, total) * 100, 1),
            "by_operation": dict(by_op),
        }

    # ── RECONCILIATION ──

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect conflicting memories in the brain.

        Conflicts: same category + contradictory content + different sources.
        """
        db = sqlite3.connect(self.brain_db_path)
        conflicts = []

        # Find memories with similar hashes but different content
        rows = db.execute("""
            SELECT m1.id, m1.category, m1.source, m1.confidence,
                   m2.id, m2.category, m2.source, m2.confidence
            FROM memories m1
            JOIN memories m2 ON m1.category = m2.category
            WHERE m1.id < m2.id
              AND m1.hash IS NOT NULL AND m2.hash IS NOT NULL
              AND m1.hash != m2.hash
              AND m1.source != m2.source
            LIMIT 50
        """).fetchall()

        for row in rows:
            conflicts.append({
                "memory_1": row[0],
                "category": row[1],
                "source_1": row[2],
                "confidence_1": row[3],
                "memory_2": row[4],
                "source_2": row[6],
                "confidence_2": row[7],
            })

        db.close()
        return conflicts

    # ── HELPERS ──

    def _find_rule(self, category: str) -> BrainAccessRule:
        """Find the matching rule for a category."""
        # Exact match
        for rule in self.rules.values():
            if rule.category == category:
                return rule
        # Wildcard
        for rule in self.rules.values():
            if rule.category == "*":
                return rule
        return BrainAccessRule()  # Default

    def check_brain_health(self) -> Dict[str, Any]:
        """Comprehensive brain health check."""
        db = sqlite3.connect(self.brain_db_path)

        total = db.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        fts_count = db.execute("SELECT COUNT(*) FROM memories_fts").fetchone()[0]
        fts_match = fts_count >= total

        # Check for missing hashes
        no_hash = db.execute(
            "SELECT COUNT(*) FROM memories WHERE hash IS NULL OR hash = ''"
        ).fetchone()[0]

        # Check for missing categories
        no_cat = db.execute(
            "SELECT COUNT(*) FROM memories WHERE category IS NULL OR category = ''"
        ).fetchone()[0]

        # Latest memory age
        latest = db.execute(
            "SELECT created_at FROM memories ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        latest_age_h = (time.time() - time.mktime(
            time.strptime(str(latest[0])[:19], "%Y-%m-%dT%H:%M:%S")
        )) / 3600 if latest and latest[0] else 0

        db.close()

        health_score = 100
        issues = []

        if not fts_match:
            health_score -= 30
            issues.append(f"FTS5 mismatch: {fts_count}/{total}")
        if no_hash > 0:
            health_score -= 10
            issues.append(f"{no_hash} memories without hash")
        if no_cat > 10:
            health_score -= 10
            issues.append(f"{no_cat} memories without category")
        if latest_age_h > 24:
            health_score -= 20
            issues.append(f"No new memories in {latest_age_h:.0f}h")

        return {
            "brain_health_score": health_score,
            "total_memories": total,
            "fts5_entries": fts_count,
            "fts5_synced": fts_match,
            "no_hash": no_hash,
            "no_category": no_cat,
            "latest_memory_age_hours": round(latest_age_h, 1),
            "issues": issues,
            "audit": self.audit_stats(),
        }


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_governor: Optional[BrainGovernor] = None

def get_brain_governor() -> BrainGovernor:
    global _governor
    if _governor is None:
        _governor = BrainGovernor()
    return _governor
