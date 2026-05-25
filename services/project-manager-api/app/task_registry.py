"""SQLite-based task registry."""
import json
import sqlite3
from datetime import datetime, timezone
from app.config import DATA_DIR
from app.schemas import TaskRecord, TaskStatus

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'queued',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload TEXT NOT NULL,
    result TEXT,
    evidence_path TEXT DEFAULT '',
    error TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_status ON tasks(status);
"""

_db_path = DATA_DIR / "tasks.db"

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def generate_task_id(prefix: str = "NX") -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    short = f"{int(datetime.now().microsecond / 1000):03d}"
    return f"{prefix}-{ts}-{short}"

def insert(task: TaskRecord) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO tasks (task_id, status, created_at, updated_at, payload) VALUES (?,?,?,?,?)",
            (task.task_id, task.status.value, task.created_at, task.updated_at, task.model_dump_json()),
        )

def update_status(task_id: str, status: TaskStatus, result: dict | None = None, evidence_path: str = "", error: str = "") -> None:
    with _conn() as c:
        row = c.execute("SELECT payload FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            return
        rec = TaskRecord.model_validate_json(row["payload"])
        rec.status = status
        rec.updated_at = now_iso()
        if result:
            rec.result = result
        if evidence_path:
            rec.evidence_path = evidence_path
        if error:
            rec.error = error
        c.execute(
            "UPDATE tasks SET status=?, updated_at=?, payload=?, result=?, evidence_path=?, error=? WHERE task_id=?",
            (status.value, rec.updated_at, rec.model_dump_json(),
             json.dumps(result) if result else None, evidence_path, error, task_id),
        )

def get(task_id: str) -> TaskRecord | None:
    with _conn() as c:
        row = c.execute("SELECT payload FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            return None
        return TaskRecord.model_validate_json(row["payload"])

def list_tasks(status: str | None = None, limit: int = 50) -> list[TaskRecord]:
    with _conn() as c:
        if status:
            rows = c.execute("SELECT payload FROM tasks WHERE status=? ORDER BY created_at DESC LIMIT ?", (status, limit)).fetchall()
        else:
            rows = c.execute("SELECT payload FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [TaskRecord.model_validate_json(r["payload"]) for r in rows]
