"""Robust project tracker loader with error handling."""
import json
import logging
from pathlib import Path

logger = logging.getLogger("pm.project_tracker")

TRACKER_PATHS = [
    Path("/root/.local/share/goose/projects.json"),
    Path("/root/.config/goose/projects.json"),
]

def load_tracker() -> tuple[bool, list | dict | None, str]:
    for path in TRACKER_PATHS:
        if path.exists():
            try:
                content = path.read_text()
                if not content.strip():
                    return False, None, f"Tracker file is empty: {path}"
                data = json.loads(content)
                logger.info("Tracker loaded from %s", path)
                return True, data, ""
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse projects.json file: {path} - {e}"
                logger.error(error_msg)
                return False, None, error_msg
    return True, [], "No projects.json found (non-blocking)"

def validate_tracker(data: list | dict | None) -> tuple[bool, str]:
    if data is None:
        return False, "Project tracker is null"
    return True, "Project tracker valid"
