#!/usr/bin/env python3
"""MCP Worker Isolation — each worker gets scoped, lease-based credentials."""
"""No worker ever touches os.environ or persistent secrets directly."""
import os, sys, json, uuid
from datetime import datetime, timezone

class ScopedWorkerIdentity:
    """Identity for a single worker execution context."""
    def __init__(self, worker_id, task_id="", capabilities=None):
        self.worker_id = worker_id
        self.task_id = task_id or str(uuid.uuid4())[:8]
        self.capabilities = capabilities or []
        self.leases = {}
        self.created = datetime.now(timezone.utc)
        self.context_id = f"{worker_id}/{self.task_id}"

    def request_credential(self, secret_name, ttl=3600):
        """Request a time-limited credential for this worker."""
        import sys
        sys.path.insert(0, "/services/runtime/security/rotation")
        from lease_manager import get_lease_manager
        lm = get_lease_manager()
        lease = lm.issue_lease(secret_name, ttl_seconds=ttl, scope=self.context_id, worker_id=self.worker_id)
        if lease:
            self.leases[lease.id] = lease
        return lease

    def use_credential(self, lease_id):
        """Access a credential via its lease. Returns None if expired."""
        import sys
        sys.path.insert(0, "/services/runtime/security/rotation")
        from lease_manager import get_lease_manager
        lm = get_lease_manager()
        return lm.access_secret(lease_id)

    def revoke_all(self):
        """Revoke all credentials held by this worker."""
        import sys
        sys.path.insert(0, "/services/runtime/security/rotation")
        from lease_manager import get_lease_manager
        lm = get_lease_manager()
        count = lm.revoke_all_for_worker(self.worker_id)
        self.leases = {}
        return count

    def to_dict(self):
        return {"worker_id": self.worker_id, "task_id": self.task_id,
                "context_id": self.context_id, "leases": len(self.leases),
                "created": self.created.isoformat()}


class WorkerIsolationManager:
    """Manages all active worker identities and their credential isolation."""
    def __init__(self):
        self.workers = {}

    def spawn_worker(self, worker_id, task_id="", capabilities=None):
        """Create a new isolated worker identity."""
        identity = ScopedWorkerIdentity(worker_id, task_id, capabilities)
        self.workers[identity.context_id] = identity
        return identity

    def get_worker(self, context_id):
        return self.workers.get(context_id)

    def terminate_worker(self, context_id):
        """Revoke all credentials and remove worker."""
        worker = self.workers.get(context_id)
        if worker:
            count = worker.revoke_all()
            del self.workers[context_id]
            return count
        return 0

    def status(self):
        return {"active_workers": len(self.workers),
                "workers": [w.to_dict() for w in self.workers.values()]}


_isol_mgr = None


def get_isolation_manager():
    global _isol_mgr
    if _isol_mgr is None:
        _isol_mgr = WorkerIsolationManager()
    return _isol_mgr


if __name__ == "__main__":
    wm = get_isolation_manager()
    w = wm.spawn_worker("agent-alpha", capabilities=["read:mongo", "write:brain"])
    lease = w.request_credential("MONGODB", ttl=120)
    val = w.use_credential(lease.id) if lease else None
    print(f"Worker {w.worker_id} got lease: {lease.id[:8] if lease else None}.. val_len={len(val) if val else 0}")
    print(f"Terminated: {wm.terminate_worker(w.context_id)} credentials revoked")
    print(json.dumps(wm.status(), indent=2))
