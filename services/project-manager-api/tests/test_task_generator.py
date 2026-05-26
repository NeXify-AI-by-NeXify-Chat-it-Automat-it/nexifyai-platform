"""Tests for TaskGenerator — GitHub webhook event → PM task mapping."""
import json, sys, os, time
sys.path.insert(0, "services/project-manager-api")

os.environ.setdefault("DATA_DIR", "/tmp/nexify-test-tg")
os.makedirs(os.environ["DATA_DIR"], exist_ok=True)

from app.task_generator import generate_task
from app.config import DATA_DIR

_DB = DATA_DIR / "tasks.db"
if _DB.exists():
    _DB.unlink()

_SESSION = str(time.time_ns())[-6:]
def _did(n): return f"test-{_SESSION}-{n:04d}"
def _ip(a, t="Test issue", n=42, l=None):
    return {"action": a, "issue": {"number": n, "title": t, "state": "open", "labels": l or []}, "repository": {"full_name": "test-org/test-repo"}}
def _pp(): return {"hook_id": 123, "zen": "test"}

def test_ping_no_task():
    r = generate_task("ping", _pp(), delivery_id=_did(1))
    assert r["ok"] and not r["task_created"]
def test_issues_opened_creates_task():
    r = generate_task("issues", _ip("opened"), delivery_id=_did(2))
    assert r["ok"] and r["task_created"]
def test_issues_closed_no_task():
    r = generate_task("issues", _ip("closed"), delivery_id=_did(3))
    assert r["ok"] and not r["task_created"]
def test_priority_p0():
    r = generate_task("issues", _ip("opened", l=[{"name":"priority-p0"}]), delivery_id=_did(4))
    assert r["priority"] == "P0"
def test_priority_security():
    r = generate_task("issues", _ip("opened", l=[{"name":"security"}]), delivery_id=_did(5))
    assert r["priority"] == "P1"
def test_issue_comment():
    p = _ip("opened"); p["action"]="created"; p["comment"]={"body":"fix it"}
    r = generate_task("issue_comment", p, delivery_id=_did(6))
    assert r["ok"] and r["task_created"]
def test_workflow_fail():
    p = {"action":"completed","workflow_run":{"name":"CI","conclusion":"failure"},"repository":{"full_name":"t/t"}}
    r = generate_task("workflow_run", p, delivery_id=_did(7))
    assert r["ok"] and r["task_created"]
def test_workflow_success_no_task():
    p = {"action":"completed","workflow_run":{"name":"CI","conclusion":"success"},"repository":{"full_name":"t/t"}}
    r = generate_task("workflow_run", p, delivery_id=_did(8))
    assert r["ok"] and not r["task_created"]
def test_code_scanning():
    p = {"action":"created","alert":{"number":101,"rule":{"description":"SSRF","severity":"error"}},"repository":{"full_name":"t/t"}}
    r = generate_task("code_scanning_alert", p, delivery_id=_did(9))
    assert r["ok"] and r["task_created"]
def test_dedupe():
    did = _did(99)
    r1 = generate_task("issues", _ip("opened"), delivery_id=did)
    r2 = generate_task("issues", _ip("opened"), delivery_id=did)
    assert r1["task_created"] and not r2["task_created"] and r2.get("duplicate")
def test_malformed():
    r = generate_task("issues", {}, delivery_id=_did(20))
    assert r["ok"]
def test_silent():
    r = generate_task("star", {"action":"created"})
    assert r["ok"] and not r["task_created"]
def test_no_secrets():
    r = generate_task("issues", _ip("opened", t="key=sk-abc123"), delivery_id=_did(30))
    assert r["ok"]
def test_pr_opened():
    p = {"action":"opened","pull_request":{"number":7,"title":"Feature X","labels":[]},"repository":{"full_name":"t/t"}}
    r = generate_task("pull_request", p, delivery_id=_did(40))
    assert r["ok"] and r["task_created"]
def test_pr_sync():
    p = {"action":"synchronize","pull_request":{"number":7,"title":"Feature X","labels":[]},"repository":{"full_name":"t/t"}}
    r = generate_task("pull_request", p, delivery_id=_did(41))
    assert r["ok"] and r["task_created"]
def test_unmapped():
    r = generate_task("deployment", {"action":"created"})
    assert r["ok"] and not r["task_created"]
