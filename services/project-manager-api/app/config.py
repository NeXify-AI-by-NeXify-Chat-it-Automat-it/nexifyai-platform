"""Configuration from environment variables only."""
import os
from pathlib import Path

PROJECT_MANAGER_API_TOKEN = os.environ.get("PROJECT_MANAGER_API_TOKEN", "")
BRAIN_API_URL = os.environ.get("BRAIN_API_URL", "http://127.0.0.1:8420")
BRAIN_API_TOKEN = os.environ.get("BRAIN_API_TOKEN", "")

DATA_DIR = Path("/opt/nexify/project-manager/data")
EVIDENCE_DIR = Path("/opt/nexify/project-manager/evidence")
QUEUE_DIR = Path("/opt/nexify/project-manager/queue")
LOG_DIR = Path("/var/log/nexify/project-manager")
REGISTRY_DIR = Path("/opt/nexify/goose-skill-bridge/registry")

DATA_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
