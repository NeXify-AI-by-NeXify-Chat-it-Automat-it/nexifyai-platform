"""
Security Routes — AI-CSO Enterprise Security Governance.

Bridges the AI-CSO module (AICSOCore + CSOApiRouter) into the FastAPI backend.
Provides 11 security endpoints under /api/security/*.

Endpoints:
  GET  /api/security/health           — CSO health score (8 dimensions)
  GET  /api/security/runtime          — Runtime discovery
  POST /api/security/threat-scan      — Full threat scan
  POST /api/security/governance-check — Policy enforcement check
  POST /api/security/runtime-audit    — Full runtime audit
  POST /api/security/session-validate — Session validation
  POST /api/security/recovery-check   — Recovery validation
  GET  /api/security/events           — Security event ledger
  GET  /api/security/incidents        — Open incidents
  GET  /api/security/compliance       — Compliance report (5 frameworks)
  GET  /api/security/policies         — Active policies
"""

import sys
import logging
from pathlib import Path

logger = logging.getLogger("nexifyai.routes.security")

# ── AI-CSO Module Discovery ────────────────────────────────────
# Try multiple possible locations for the ai-farbrik module
AI_FARBRIK_CANDIDATES = [
    Path("/opt/ai-farbrik"),                                    # Local container
    Path("/opt/nexifyai-website-sicherheitskopie/ai-farbrik"),  # VPS repo
    Path(__file__).parent.parent.parent / "ai-farbrik",         # Relative to backend dir
]

AI_FARBRIK_PATH = None
for candidate in AI_FARBRIK_CANDIDATES:
    security_path = candidate / "core" / "security"
    if security_path.exists() and (security_path / "__init__.py").exists():
        AI_FARBRIK_PATH = str(candidate)
        break

if AI_FARBRIK_PATH is None:
    raise ImportError(
        f"AI-CSO module not found. Tried: {[str(p) for p in AI_FARBRIK_CANDIDATES]}"
    )

if AI_FARBRIK_PATH not in sys.path:
    sys.path.insert(0, AI_FARBRIK_PATH)

logger.info(f"AI-CSO module loaded from: {AI_FARBRIK_PATH}")

# ── Import AI-CSO Components ──────────────────────────────────
from core.security.core import AICSOCore          # noqa: E402
from core.security.api import CSOApiRouter         # noqa: E402

# ── Singleton CSO Instance ────────────────────────────────────
cso_core = AICSOCore()
cso_api = CSOApiRouter(cso_core)
router = cso_api.to_fastapi_router()

logger.info(
    "AI-CSO Security Router initialized — 11 endpoints registered under /api/security/*"
)
