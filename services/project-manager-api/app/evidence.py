"""Evidence storage and warning analysis."""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from app.config import EVIDENCE_DIR
from app.redaction import redact_string

logger = logging.getLogger("pm.evidence")

def save_evidence(task_id: str, output: str, stderr: str) -> str:
    evidence_dir = EVIDENCE_DIR / task_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = evidence_dir / f"output_{ts}.log"
    out_file.write_text(redact_string(output), encoding="utf-8")
    if stderr and stderr.strip():
        err_file = evidence_dir / f"stderr_{ts}.log"
        err_file.write_text(redact_string(stderr), encoding="utf-8")
    meta = evidence_dir / f"meta_{ts}.json"
    meta.write_text(json.dumps({
        "task_id": task_id, "timestamp": ts,
        "files": [f.name for f in evidence_dir.iterdir() if f.is_file()]
    }, indent=2))
    return str(evidence_dir)
