"""Tests for TaskGenerator — GitHub webhook event → PM task mapping."""
import json, sys, os, time
sys.path.insert(0, "services/project-manager-api")

os.environ.setdefault("DATA_DIR", "/tmp/nexify-test-tg")
os.makedirs(os.environ["DATA_DIR"], exist_ok=True)

from app.task_generator import generate_task
from app.config import DATA_DIR

# Clean test database
_DB = DATA_DIR / "tasks.db"
if _DB.exists():
    _DB.unlink()

_SESSION = str(time.time_ns())[-6:]
def _did(n): return f"test-{_SESSION}-{n:04d}"
def _ip(a, t="Test issue", n=42, l=None):
    return {"action": a, "issue": {"number": n, "title": t, "state": "open", "labels": l or []}, "repository": {"full_name": "test-org/test-repo"}}
def _pp(): return {"hook_id": 123, "zen": "test"}
def _pr_payload(action, title="PR title", number=7):
    return {"action": action, "pull_request": {"number": number, "title": title, "labels": []}, "repository": {"full_name": "test-org/test-repo"}}
def _wf_payload(conclusion):
    return {"action": "completed", "workflow_run": {"name": "CI", "conclusion": conclusion}, "repository": {"full_name": "test-org/test-repo"}}
def _cs_payload(action):
    return {"action": action, "alert": {"number": 1, "rule": {"description": "SSRF", "severity": "error"}}, "repository": {"full_name": "test-org/test-repo"}}

tests = {}

def t(n, f): tests[n] = f

t("ping_no_task", lambda: (lambda r: r["ok"] and not r["task_created"])(generate_task("ping", _pp(), delivery_id=_did(1))))
t("issues_opened", lambda: (lambda r: r["ok"] and r["task_created"] and r["event"]=="issues")(generate_task("issues", _ip("opened"), delivery_id=_did(2))))
t("issues_closed", lambda: (lambda r: r["ok"] and not r["task_created"])(generate_task("issues", _ip("closed"), delivery_id=_did(3))))
t("priority_p0", lambda: (lambda r: r["ok"] and r["task_created"] and r["priority"]=="P0")(generate_task("issues", _ip("opened", l=[{"name":"priority-p0"}]), delivery_id=_did(4))))
t("priority_security", lambda: (lambda r: r["ok"] and r["task_created"] and r["priority"]=="P1")(generate_task("issues", _ip("opened", l=[{"name":"security"}]), delivery_id=_did(5))))
t("issue_comment", lambda: (lambda p: p.update({"action":"created","comment":{"body":"fix"}}) or (lambda r: r["ok"] and r["task_created"])(generate_task("issue_comment", p, delivery_id=_did(6))))(_ip("opened")))
t("workflow_fail", lambda: (lambda r: r["ok"] and r["task_created"])(generate_task("workflow_run", _wf_payload("failure"), delivery_id=_did(7))))
t("workflow_success", lambda: (lambda r: r["ok"] and not r["task_created"])(generate_task("workflow_run", _wf_payload("success"), delivery_id=_did(8))))
t("code_scanning", lambda: (lambda r: r["ok"] and r["task_created"])(generate_task("code_scanning_alert", _cs_payload("created"), delivery_id=_did(9))))
t("dedupe", lambda: (lambda d: (generate_task("issues", _ip("opened"), delivery_id=d)["task_created"] and not generate_task("issues", _ip("opened"), delivery_id=d)["task_created"] and generate_task("issues", _ip("opened"), delivery_id=d).get("duplicate"))(_did(99))))
t("malformed", lambda: generate_task("issues", {}, delivery_id=_did(20))["ok"])
t("silent", lambda: not generate_task("star", {"action":"created"})["task_created"])
t("no_secrets", lambda: (lambda r: r["ok"] and "sk-abc123" not in r.get("goal",""))(generate_task("issues", _ip("opened", t="Fix key=sk-abc123"), delivery_id=_did(30))))
t("pr_opened", lambda: (lambda r: r["ok"] and r["task_created"])(generate_task("pull_request", _pr_payload("opened"), delivery_id=_did(40))))
t("pr_sync", lambda: (lambda r: r["ok"] and r["task_created"])(generate_task("pull_request", _pr_payload("synchronize"), delivery_id=_did(41))))
t("unmapped", lambda: not generate_task("deployment", {"action":"created"})["task_created"])

passed = 0
for name in sorted(tests):
    try:
        tests[name]()
        print(f"  \u2705 {name}")
        passed += 1
    except Exception as e:
        print(f"  \u274c {name}: {e}")
print(f"\n{'='*40}\nPassed: {passed}/{len(tests)}")
sys.exit(0 if passed == len(tests) else 1)
