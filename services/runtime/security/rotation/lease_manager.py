#!/usr/bin/env python3
"""Lease-Based Credential Manager — credentials with TTL, scoped access, auto-revoke."""
import os, json, time, uuid, logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("nexifyai.security.lease")

class CredentialLease:
    """A single credential lease with TTL."""
    def __init__(self, secret_name, value, ttl_seconds=3600, scope="", worker_id=""):
        self.id = str(uuid.uuid4())
        self.secret_name = secret_name
        self.value = value
        self.created = datetime.now(timezone.utc)
        self.expires = self.created + timedelta(seconds=ttl_seconds)
        self.scope = scope
        self.worker_id = worker_id
        self.access_count = 0
        self.revoked = False

    def is_valid(self):
        return not self.revoked and datetime.now(timezone.utc) < self.expires

    def access(self):
        if not self.is_valid():
            return None
        self.access_count += 1
        return self.value

    def revoke(self):
        self.revoked = True

    def to_dict(self):
        return {"id": self.id, "secret": self.secret_name, "created": self.created.isoformat(),
                "expires": self.expires.isoformat(), "scope": self.scope, "worker": self.worker_id,
                "access_count": self.access_count, "revoked": self.revoked,
                "valid": self.is_valid()}


class LeaseManager:
    """Manages all active credential leases. Auto-cleanup on expiry."""
    def __init__(self):
        self.leases = {}  # lease_id -> CredentialLease

    def issue_lease(self, secret_name, ttl_seconds=3600, scope="", worker_id="system"):
        """Issue a time-limited lease for a secret."""
        import sys
        sys.path.insert(0, "/services/runtime/security/vault")
        from vault_compat import get_vault
        v = get_vault(worker_id)
        value = v.get(secret_name)
        if not value:
            return None
        lease = CredentialLease(secret_name, value, ttl_seconds, scope, worker_id)
        self.leases[lease.id] = lease
        # Log to audit
        with open("/services/runtime/security/audit/events.log", "a") as f:
            f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                                "type": "lease_issued", "lease_id": lease.id,
                                "secret": secret_name, "worker": worker_id,
                                "ttl": ttl_seconds, "scope": scope}) + "\n")
        return lease

    def get_lease(self, lease_id):
        return self.leases.get(lease_id)

    def access_secret(self, lease_id):
        """Use a lease to access a secret. Returns None if expired/revoked."""
        lease = self.leases.get(lease_id)
        if not lease:
            return None
        val = lease.access()
        if val is None:
            # Auto-cleanup expired leases
            self.cleanup()
            return None
        # Log access
        with open("/services/runtime/security/audit/events.log", "a") as f:
            f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                                "type": "lease_access", "lease_id": lease.id,
                                "secret": lease.secret_name, "count": lease.access_count}) + "\n")
        return val

    def revoke_lease(self, lease_id):
        lease = self.leases.get(lease_id)
        if lease:
            lease.revoke()
            with open("/services/runtime/security/audit/events.log", "a") as f:
                f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                                    "type": "lease_revoked", "lease_id": lease.id,
                                    "secret": lease.secret_name}) + "\n")

    def revoke_all_for_worker(self, worker_id):
        count = 0
        for lid, lease in list(self.leases.items()):
            if lease.worker_id == worker_id:
                lease.revoke()
                count += 1
        return count

    def cleanup(self):
        """Remove expired leases."""
        now = datetime.now(timezone.utc)
        expired = [lid for lid, l in self.leases.items() if l.expires < now or l.revoked]
        for lid in expired:
            del self.leases[lid]
        return len(expired)

    def status(self):
        self.cleanup()
        valid = [l.to_dict() for l in self.leases.values() if l.is_valid()]
        return {"active_leases": len(valid), "leases": valid}


_manager = None


def get_lease_manager():
    global _manager
    if _manager is None:
        _manager = LeaseManager()
    return _manager


if __name__ == "__main__":
    import sys
    lm = get_lease_manager()
    lease = lm.issue_lease("MONGODB", ttl_seconds=60, worker_id="test-worker")
    if lease:
        val = lm.access_secret(lease.id)
        logger.info("Lease %s... valid=%s val_len=%d", lease.id[:8], lease.is_valid(), len(val) if val else 0)
        lm.revoke_lease(lease.id)
        logger.info("After revoke: valid=%s", lease.is_valid())
    logger.info("Status: %s", json.dumps(lm.status()))
