"""
NeXifyAI Review Cycle — adapted from hamelsmu/claude-review-loop.

Original: Stop-hook driven review loop with Codex CLI as reviewer.
Adaptation: 3-phase agent orchestration (implement → review → fix)
using existing Hermes agents + Brain persistence.

Phase 1: ai-engineer implements the task
Phase 2: security-auditor + quality-engineer review in parallel
Phase 3: ai-engineer addresses feedback, loop until consensus
"""
import asyncio, json, hashlib, time, logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("review_cycle.engine")

# ── Review status tracking ──
class ReviewStatus:
    PENDING = "pending"
    IN_IMPLEMENTATION = "implementing"
    IN_REVIEW = "in_review"
    NEEDS_FIXES = "needs_fixes"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class ReviewFinding:
    """A single finding from a reviewer."""
    id: str
    reviewer: str
    severity: str  # critical, major, minor, suggestion
    category: str  # security, performance, architecture, style, logic, testing
    file_path: Optional[str] = None
    line_range: Optional[str] = None
    description: str = ""
    recommendation: str = ""
    resolved: bool = False

@dataclass
class ReviewSession:
    """A complete review cycle session."""
    session_id: str
    task: str
    status: str = ReviewStatus.PENDING
    
    # Implementation
    implementation: Optional[str] = None
    implemented_files: list[str] = field(default_factory=list)
    
    # Reviews
    security_findings: list[ReviewFinding] = field(default_factory=list)
    quality_findings: list[ReviewFinding] = field(default_factory=list)
    
    # Resolution
    iterations: int = 0
    max_iterations: int = 3
    
    # Timing
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    total_cost: float = 0.0

@dataclass
class ReviewCycleResult:
    """Final result of a review cycle."""
    session_id: str
    approved: bool
    iterations: int
    total_findings: int
    resolved_findings: int
    critical_unresolved: int
    duration_seconds: float
    total_cost: float
    summary: str

# ── Review phase orchestration ──
REVIEWER_AGENT_PROFILES = {
    "security-auditor": {
        "focus": "security",
        "checks": [
            "SQL injection / NoSQL injection",
            "XSS / CSRF vulnerabilities",
            "Sensitive data exposure",
            "Authentication / authorization flaws",
            "Insecure dependencies",
            "Missing input validation",
            "Hardcoded secrets / credentials",
            "Missing rate limiting",
            "Insecure file operations",
        ]
    },
    "quality-engineer": {
        "focus": "code_quality",
        "checks": [
            "Type safety / null handling",
            "Error handling completeness",
            "Test coverage gaps",
            "Performance bottlenecks",
            "API contract violations",
            "Concurrency issues",
            "Memory leaks",
            "Logging adequacy",
            "Documentation accuracy",
        ]
    }
}

REVIEW_PROMPT_TEMPLATE = """You are the {agent_name} ({agent_role}).
Review the following implementation for {focus} issues.

TASK: {task}

IMPLEMENTATION:
{implementation}

CHANGED FILES: {files}

Previous findings (if any): {previous_findings}

Review the implementation for {focus} concerns. For each finding, provide:
1. SEVERITY: critical | major | minor | suggestion
2. CATEGORY: the specific area
3. LOCATION: file and line range if applicable
4. DESCRIPTION: what's wrong
5. RECOMMENDATION: how to fix it

Be thorough but practical. Focus on issues that would actually cause problems in production.
Do NOT flag style preferences or minor formatting issues.

End with: APPROVED (no issues) or NEEDS_FIXES (list remaining issues)."""

# ── Brain integration for review patterns ──
async def store_review_in_brain(session: ReviewSession, result: ReviewCycleResult):
    """Store review results in Brain for pattern learning."""
    import httpx
    
    point_id = hashlib.sha256(
        f"review:{session.session_id}:{time.time()}".encode()
    ).hexdigest()[:16]
    
    payload = {
        "category": "code_review",
        "title": session.task[:120],
        "content": json.dumps({
            "session_id": session.session_id,
            "task": session.task,
            "approved": result.approved,
            "iterations": result.iterations,
            "total_findings": result.total_findings,
            "critical_unresolved": result.critical_unresolved,
            "duration": result.duration_seconds,
            "cost": result.total_cost,
            "security_findings": [f.description[:100] for f in session.security_findings if f.severity == "critical"],
            "quality_findings": [f.description[:100] for f in session.quality_findings if f.severity == "critical"],
            "pattern_summary": result.summary,
        }),
        "timestamp": time.time(),
        "source": "review-cycle",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            await client.put(
                "http://localhost:6333/collections/nexifyai_brain/points",
                json={"points": [{"id": point_id, "vector": [0.0]*1536, "payload": payload}]},
                timeout=10
            )
    except Exception as e:
        logger.warning(f"Brain storage failed: {e}")

async def get_past_review_patterns(task_keywords: str) -> list[dict]:
    """Get past review patterns from Brain to avoid repeating mistakes."""
    import httpx
    words = task_keywords.split()[:5]
    body = {
        "limit": 5, "with_payload": True, "with_vector": False,
        "filter": {
            "must": [
                {"key": "category", "match": {"value": "code_review"}},
            ],
            "should": [{"key": "content", "match": {"text": w}} for w in words],
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "http://localhost:6333/collections/nexifyai_brain/points/scroll",
                json=body, timeout=10
            )
            return [p["payload"] for p in r.json().get("result", {}).get("points", [])]
    except Exception:
        return []
