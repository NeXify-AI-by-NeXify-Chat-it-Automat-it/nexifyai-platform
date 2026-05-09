"""
NeXifyAI — Session Governance Runtime (Sprint D)

NOT: blind --resume without SESSION_ID
BUT:  governed session lifecycle with registry, heartbeat, retry, recovery

CRITICAL: Prevents crash-loops, zombie sessions, runtime drift.
Foundation for deterministic agent execution.
"""
import json
import time
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


# ═══════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════

class SessionStatus(Enum):
    RUNNING = "running"
    IDLE = "idle"
    CRASHED = "crashed"
    STALE = "stale"
    RECOVERED = "recovered"
    CIRCUIT_OPEN = "circuit_open"
    TERMINATED = "terminated"

@dataclass
class SessionRecord:
    """Runtime session state."""
    session_id: str
    agent: str = "hermes"
    status: SessionStatus = SessionStatus.RUNNING
    started_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    last_turn_at: float = 0.0
    retry_count: int = 0
    crash_count: int = 0
    max_retries: int = 3
    last_error: str = ""
    last_crash_time: float = 0.0
    runtime_lock: bool = False
    governance_lock: bool = False
    circuit_open: bool = False
    circuit_opened_at: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════
# SESSION GOVERNOR
# ═══════════════════════════════════════════════════

class SessionGovernor:
    """
    Governed session lifecycle management.

    Enforces:
      - Session validation before resume
      - Heartbeat monitoring (stale detection)
      - Crash counting with circuit breaker
      - Exponential backoff retry
      - Recovery logging + audit
      - Zombie session detection

    PROHIBITED:
      - hermes chat --resume without SESSION_ID
      - Blind restart loops
      - Infinite crash-retry cycles
    """

    def __init__(self, registry_dir: str = "/opt/data/runtime/sessions",
                 audit_dir: str = "/opt/data/runtime/audit",
                 max_retries: int = 3,
                 backoff_base: int = 30,
                 heartbeat_timeout: int = 300,
                 circuit_breaker_threshold: int = 5):
        self.registry_dir = registry_dir
        self.audit_dir = audit_dir
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.heartbeat_timeout = heartbeat_timeout
        self.circuit_breaker_threshold = circuit_breaker_threshold
        os.makedirs(registry_dir, exist_ok=True)
        os.makedirs(audit_dir, exist_ok=True)

    # ── Session CRUD ──

    def register(self, session_id: str, agent: str = "hermes") -> SessionRecord:
        """Register a new session."""
        session = SessionRecord(
            session_id=session_id,
            agent=agent,
        )
        self._persist(session)
        self._audit("SESSION_REGISTERED", f"session={session_id} agent={agent}")
        return session

    def load(self, session_id: str) -> Optional[SessionRecord]:
        """Load a session from the registry."""
        path = os.path.join(self.registry_dir, f"{session_id}.json")
        if not os.path.exists(path):
            return None
        try:
            data = json.load(open(path))
            return SessionRecord(
                session_id=data["session_id"],
                agent=data.get("agent", "hermes"),
                status=SessionStatus(data.get("status", "running")),
                started_at=data.get("started_at", time.time()),
                last_heartbeat=data.get("last_heartbeat", 0),
                last_turn_at=data.get("last_turn_at", 0),
                retry_count=data.get("retry_count", 0),
                crash_count=data.get("crash_count", 0),
                max_retries=data.get("max_retries", self.max_retries),
                last_error=data.get("last_error", ""),
                last_crash_time=data.get("last_crash_time", 0),
                runtime_lock=data.get("runtime_lock", False),
                governance_lock=data.get("governance_lock", False),
                circuit_open=data.get("circuit_open", False),
                circuit_opened_at=data.get("circuit_opened_at", 0),
            )
        except Exception:
            return None

    def _persist(self, session: SessionRecord):
        """Persist session to disk."""
        path = os.path.join(self.registry_dir, f"{session.session_id}.json")
        data = {
            "session_id": session.session_id,
            "agent": session.agent,
            "status": session.status.value,
            "started_at": session.started_at,
            "last_heartbeat": session.last_heartbeat,
            "last_turn_at": session.last_turn_at,
            "retry_count": session.retry_count,
            "crash_count": session.crash_count,
            "max_retries": session.max_retries,
            "last_error": session.last_error,
            "last_crash_time": session.last_crash_time,
            "runtime_lock": session.runtime_lock,
            "governance_lock": session.governance_lock,
            "circuit_open": session.circuit_open,
            "circuit_opened_at": session.circuit_opened_at,
        }
        json.dump(data, open(path, "w"), indent=2)

    # ── Validation ──

    def validate(self, session_id: str) -> tuple:
        """
        Validate a session before resume.

        Returns: (status, reason)
          - VALID: Session exists and is healthy
          - INVALID: Session not found
          - STALE: No heartbeat in heartbeat_timeout
          - CIRCUIT_OPEN: Too many crashes
        """
        session = self.load(session_id)
        if not session:
            return ("INVALID", "Session not found")

        # Check heartbeat
        age = time.time() - session.last_heartbeat
        if age > self.heartbeat_timeout:
            session.status = SessionStatus.STALE
            self._persist(session)
            self._audit("SESSION_STALE", f"session={session_id} age={age:.0f}s")
            return ("STALE", f"No heartbeat for {age:.0f}s")

        # Check circuit breaker
        if session.crash_count >= self.circuit_breaker_threshold:
            if not session.circuit_open:
                session.circuit_open = True
                session.circuit_opened_at = time.time()
                session.status = SessionStatus.CIRCUIT_OPEN
                self._persist(session)
            self._audit("CIRCUIT_OPEN", f"session={session_id} crashes={session.crash_count}")
            return ("CIRCUIT_OPEN", f"Crash count {session.crash_count} >= threshold {self.circuit_breaker_threshold}")

        return ("VALID", "Session healthy")

    # ── Heartbeat ──

    def heartbeat(self, session_id: str):
        """Update session heartbeat."""
        session = self.load(session_id)
        if session:
            session.last_heartbeat = time.time()
            if session.status == SessionStatus.RECOVERED:
                session.status = SessionStatus.RUNNING
            self._persist(session)

    # ── Crash Recording ──

    def record_crash(self, session_id: str, error: str):
        """Record a session crash."""
        session = self.load(session_id)
        if not session:
            session = SessionRecord(session_id=session_id)
            self.register(session_id)

        session.crash_count += 1
        session.last_error = error
        session.last_crash_time = time.time()
        session.status = SessionStatus.CRASHED
        self._persist(session)
        self._audit("SESSION_CRASH", f"session={session_id} crash={session.crash_count}/{self.max_retries} error={error[:100]}")

        # Check circuit breaker
        if session.crash_count >= self.circuit_breaker_threshold:
            session.circuit_open = True
            session.circuit_opened_at = time.time()
            session.status = SessionStatus.CIRCUIT_OPEN
            self._persist(session)
            self._audit("CIRCUIT_OPEN", f"session={session_id} threshold={self.circuit_breaker_threshold}")

    # ── Retry Logic ──

    def should_retry(self, session_id: str) -> tuple:
        """
        Check if a session should be retried.

        Returns: (allowed, reason, wait_seconds)
        """
        session = self.load(session_id)
        if not session:
            return (False, "Session not found", 0)

        if session.crash_count >= self.max_retries:
            self._audit("RETRY_EXHAUSTED", f"session={session_id} crashes={session.crash_count}/{self.max_retries}")
            return (False, f"Retry budget exhausted ({session.crash_count}/{self.max_retries})", 0)

        if session.circuit_open:
            return (False, "Circuit breaker open", 0)

        # Exponential backoff
        backoff = self.backoff_base * (2 ** session.retry_count)
        backoff = min(backoff, 600)  # Cap at 10 minutes

        elapsed = time.time() - session.last_crash_time
        if elapsed < backoff:
            wait = int(backoff - elapsed)
            return (False, f"Backoff: wait {wait}s", wait)

        return (True, "Ready for retry", 0)

    # ── Recovery ──

    def recover(self, session_id: str) -> Optional[SessionRecord]:
        """
        Recover a crashed/stale session.

        Creates a new session but preserves history for audit.
        """
        old = self.load(session_id)
        if old:
            old.status = SessionStatus.RECOVERED
            self._persist(old)

        new_id = f"{session_id}_recovered_{int(time.time())}"
        session = SessionRecord(
            session_id=new_id,
            agent=old.agent if old else "hermes",
            status=SessionStatus.RECOVERED,
            metadata={"recovered_from": session_id},
        )
        self._persist(session)
        self._audit("SESSION_RECOVERED", f"old={session_id} new={new_id}")
        return session

    # ── Zombie Detection ──

    def detect_zombies(self) -> List[str]:
        """Find zombie sessions: running but no heartbeat, excluding terminated."""
        zombies = []
        for fname in os.listdir(self.registry_dir):
            if not fname.endswith(".json"):
                continue
            session_id = fname.replace(".json", "")
            session = self.load(session_id)
            if not session:
                continue
            # Skip already terminated or recovered
            if session.status in (SessionStatus.TERMINATED, SessionStatus.RECOVERED):
                continue
            status, reason = self.validate(session_id)
            if status == "STALE":
                zombies.append(session_id)
        return zombies

    def cleanup_zombies(self):
        """Mark all zombie sessions as terminated."""
        for session_id in self.detect_zombies():
            session = self.load(session_id)
            if session:
                session.status = SessionStatus.TERMINATED
                self._persist(session)
                self._audit("ZOMBIE_CLEANED", f"session={session_id}")

    # ── Audit ──

    def _audit(self, event: str, detail: str):
        """Write audit entry."""
        log_path = os.path.join(self.audit_dir, "runtime.log")
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] {event} | {detail}\n")

    def get_audit_log(self, limit: int = 100) -> List[str]:
        """Read recent audit entries."""
        log_path = os.path.join(self.audit_dir, "runtime.log")
        if not os.path.exists(log_path):
            return []
        with open(log_path) as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-limit:]]

    def stats(self) -> Dict[str, Any]:
        """Session governance statistics."""
        sessions = []
        for fname in os.listdir(self.registry_dir):
            if not fname.endswith(".json"):
                continue
            session_id = fname.replace(".json", "")
            session = self.load(session_id)
            if session:
                sessions.append(session)

        running = sum(1 for s in sessions if s.status == SessionStatus.RUNNING)
        crashed = sum(1 for s in sessions if s.status == SessionStatus.CRASHED)
        recovered = sum(1 for s in sessions if s.status == SessionStatus.RECOVERED)
        zombies = len(self.detect_zombies())

        return {
            "total_sessions": len(sessions),
            "running": running,
            "crashed": crashed,
            "recovered": recovered,
            "zombies_detected": zombies,
            "registry_dir": self.registry_dir,
        }


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_governor: Optional[SessionGovernor] = None

def get_session_governor() -> SessionGovernor:
    global _governor
    if _governor is None:
        _governor = SessionGovernor()
    return _governor
