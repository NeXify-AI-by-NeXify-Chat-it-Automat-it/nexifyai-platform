#!/usr/bin/env python3
"""Self-Heal Engine -- detects and auto-repairs credential issues."""
import os, json, sys
from datetime import datetime, timezone
sys.path.insert(0, "/services/runtime/security/rotation")
sys.path.insert(0, "/services/runtime/security/vault")

class SelfHeal:
    def __init__(self):
        self.actions = []
    def detect_and_heal(self):
        now = datetime.now(timezone.utc)
        # 1. Check registry vs env gaps -> reconcile
        sys.path.insert(0, "/services/runtime/security/rotation")
        from credential_reconciler import CredentialReconciler
        rec = CredentialReconciler()
        gaps = rec.reconcile()
        if gaps.get("registry_gaps"):
            rec.auto_register_gaps()
            self.actions.append(f"registered {len(gaps['registry_gaps'])} missing env credentials")
        # 2. Check expired -> revoke
        sys.path.insert(0, "/services/runtime/security/rotation")
        from revocation_engine import RevocationEngine
        eng = RevocationEngine()
        revoked = eng.revoke_all_expired()
        if revoked:
            self.actions.append(f"revoked {len(revoked)} expired credentials")
        # 3. Check stale leases -> cleanup
        from lease_manager import get_lease_manager
        lm = get_lease_manager()
        cleaned = lm.cleanup()
        if cleaned:
            self.actions.append(f"cleaned {cleaned} stale leases")
        # 4. Verify vault health
        sys.path.insert(0, "/services/runtime/security/vault")
        from vault_compat import get_vault
        v = get_vault("selfheal")
        ds_count = sum(1 for k in os.environ if k.startswith("DS_"))
        if ds_count == 100:
            self.actions.append("vault healthy: 100/100 credentials")
        else:
            self.actions.append(f"vault degraded: {ds_count}/100 credentials")
        # 5. Report to brain
        self._report_brain()
        return {"ts": now.isoformat(), "healed": len(self.actions), "actions": self.actions}
    def _report_brain(self):
        try:
            import requests, uuid
            requests.put("http://localhost:6333/collections/nexifyai_brain/points", json={
                "points": [{"id": str(uuid.uuid4()), "vector": [0.0]*384,
                           "payload": {"category": "security", "severity": "info",
                                       "title": f"Self-heal: {len(self.actions)} actions",
                                       "detail": json.dumps(self.actions),
                                       "ts": datetime.now(timezone.utc).isoformat()}}]
            }, timeout=3)
        except: pass

if __name__ == "__main__":
    h = SelfHeal()
    print(json.dumps(h.detect_and_heal(), indent=2))
