"""
Review Cycle API Routes.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from .engine import (
    ReviewSession, ReviewFinding, ReviewCycleResult, ReviewStatus,
    REVIEWER_AGENT_PROFILES, REVIEW_PROMPT_TEMPLATE,
    store_review_in_brain, get_past_review_patterns,
)

review_router = APIRouter(prefix="/api/review", tags=["review-cycle"])

class ReviewRequest(BaseModel):
    task: str = Field(..., description="Task description for review")
    implementation: str = Field(..., description="Code/implementation to review")
    files: list[str] = Field(default=[], description="Files changed")
    reviewers: list[str] = Field(default=["security-auditor", "quality-engineer"],
                                  description="Reviewer agents to use")
    max_iterations: int = Field(default=3, ge=1, le=5)

class ReviewResponse(BaseModel):
    session_id: str
    status: str
    task: str
    findings: list[dict]
    approved: bool
    iterations: int
    summary: str

@review_router.post("/start", response_model=ReviewResponse)
async def start_review(request: ReviewRequest, background_tasks: BackgroundTasks):
    """Start a review cycle. Routes to security-auditor + quality-engineer."""
    session_id = str(uuid.uuid4())[:8]
    
    # Check Brain for past patterns on this task
    past_patterns = await get_past_review_patterns(request.task)
    
    session = ReviewSession(
        session_id=session_id,
        task=request.task,
        implementation=request.implementation,
        implemented_files=request.files,
        max_iterations=request.max_iterations,
    )
    
    # Run the review — in a real deployment, this would call the Hermes agents
    # For now, we generate the review prompts that Hermes agents will consume
    review_results = []
    
    for reviewer_name in request.reviewers:
        if reviewer_name not in REVIEWER_AGENT_PROFILES:
            raise HTTPException(400, f"Unknown reviewer: {reviewer_name}")
        
        profile = REVIEWER_AGENT_PROFILES[reviewer_name]
        
        # Build the review prompt
        prompt = REVIEW_PROMPT_TEMPLATE.format(
            agent_name=reviewer_name,
            agent_role=profile["focus"],
            focus=profile["focus"],
            task=request.task,
            implementation=request.implementation[:8000],
            files=", ".join(request.files),
            previous_findings="None (first review)",
        )
        
        review_results.append({
            "reviewer": reviewer_name,
            "focus": profile["focus"],
            "checks": profile["checks"],
            "prompt": prompt,
            "prompt_length": len(prompt),
        })
    
    findings_list = []
    for r in review_results:
        findings_list.append({
            "reviewer": r["reviewer"],
            "focus": r["focus"],
            "checks_count": len(r["checks"]),
            "checks": r["checks"][:5],
            "status": "prompt_generated",
        })
    
    # Store in Brain
    result = ReviewCycleResult(
        session_id=session_id,
        approved=False,  # Will be set after actual agent execution
        iterations=1,
        total_findings=0,
        resolved_findings=0,
        critical_unresolved=0,
        duration_seconds=0,
        total_cost=0,
        summary=f"Review initiated for: {request.task[:100]}"
    )
    background_tasks.add_task(store_review_in_brain, session, result)
    
    return ReviewResponse(
        session_id=session_id,
        status=ReviewStatus.IN_REVIEW,
        task=request.task,
        findings=findings_list,
        approved=False,
        iterations=1,
        summary=f"Review prompts generated for {len(request.reviewers)} agents. Past patterns found: {len(past_patterns)}"
    )

@review_router.get("/reviewers")
async def list_reviewers():
    """List available reviewer agents and their focus areas."""
    return {
        "reviewers": {
            name: {"focus": profile["focus"], "checks": len(profile["checks"]), 
                   "top_checks": profile["checks"][:5]}
            for name, profile in REVIEWER_AGENT_PROFILES.items()
        }
    }

@review_router.get("/past")
async def past_reviews(q: str = "", limit: int = 10):
    """Get past review patterns from Brain."""
    patterns = await get_past_review_patterns(q)
    return {"query": q, "patterns": patterns, "count": len(patterns)}
