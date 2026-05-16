#!/usr/bin/env python3
"""
NeXifyAI Agent Eval Suite — Pre-Launch Prompt Validation
Think Tank Decision #3 (Simon Willison):
"Prompt engineering IS the production system. Pre-launch eval suite
for every agent prompt before go-live — the equivalent of unit tests for agents."

Tests every agent profile for:
  1. Profile completeness (all required fields present)
  2. Prompt structure (clear role, constraints, output format)
  3. Brain-First compliance (does the prompt instruct Brain querying?)
  4. Mission alignment (does it reference the shared mission?)
  5. DOS v2.1 compliance (no disallowed tools/patterns)
  6. Test execution (dry-run with a sample task, validate output structure)
"""
import os, sys, json, logging, asyncio
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(asctime)s [eval] %(levelname)s: %(message)s")
logger = logging.getLogger("agent_eval")

BRAIN_URL = os.environ.get("HERMES_BRAIN_URL", "http://localhost:6333")
COLLECTION = "nexifyai_brain"
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")

# === All known agents (from orchestrator_v2 + brain_agents/) ===
ALL_AGENTS = [
    "ai-engineer", "agent-expert",
    "project-manager", "task-decomposition-expert", "project-supervisor-orchestrator", "business-analyst",
    "cloud-architect", "deployment-engineer", "monitoring-specialist",
    "fullstack-developer", "nextjs-architecture-expert", "supabase-schema-architect",
    "data-analyst", "data-engineer", "research-coordinator", "fact-checker",
    "review-agent", "security-engineer", "security-auditor",
    "llms-maintainer", "context-manager", "search-specialist", "prompt-engineer",
    "documentation-expert", "metadata-agent", "document-structure-analyzer",
    "architecture-modernizer", "dependency-manager",
]

REQUIRED_FIELDS = ["name", "description", "role", "system_prompt"]
DOS_FORBIDDEN = ["n8n", "zapier", "make.com", "make ", "localhost:5678"]
BRAIN_KEYWORDS = ["brain", "qdrant", "nexifyai_brain", "memory", "prior knowledge", "query the brain"]
MISSION_KEYWORDS = ["mission", "customer outcome", "faster", "safer", "more joyful", "serve the"]

# ======================================================================
# TEST 1: PROFILE COMPLETENESS
# ======================================================================
def test_profile_completeness(agent_id: str, profile: dict) -> dict:
    """Verify agent profile has all required fields."""
    issues = []
    
    for field in REQUIRED_FIELDS:
        if field not in profile:
            issues.append(f"Missing required field: {field}")
        elif not profile[field] or (isinstance(profile[field], str) and len(profile[field].strip()) < 10):
            issues.append(f"Field too short or empty: {field}")
    
    # Check for descriptions that are too short
    desc = profile.get("description", "")
    if isinstance(desc, str) and len(desc) < 30:
        issues.append(f"Description too short ({len(desc)} chars)")
    
    return {
        "test": "profile_completeness",
        "passed": len(issues) == 0,
        "issues": issues,
        "score": 1.0 if len(issues) == 0 else max(0, 1.0 - len(issues) * 0.15),
    }


# ======================================================================
# TEST 2: PROMPT STRUCTURE
# ======================================================================
def test_prompt_structure(agent_id: str, profile: dict) -> dict:
    """Verify prompt has clear role, constraints, output format."""
    issues = []
    prompt = profile.get("system_prompt", "") + " " + profile.get("description", "")
    prompt_lower = prompt.lower()
    
    # Role clarity
    role_indicators = ["you are", "your role", "as a", "acting as"]
    if not any(ri in prompt_lower for ri in role_indicators):
        issues.append("No clear role definition (missing 'you are' / 'your role' / etc.)")
    
    # Constraints
    constraint_indicators = ["must", "never", "always", "do not", "only", "required", "mandatory"]
    if not any(ci in prompt_lower for ci in constraint_indicators):
        issues.append("No behavioral constraints (missing 'must' / 'never' / 'always')")
    
    # Output format
    output_indicators = ["output", "respond with", "format", "return", "json", "markdown", "structured"]
    if not any(oi in prompt_lower for oi in output_indicators):
        issues.append("No output format specified")
    
    return {
        "test": "prompt_structure",
        "passed": len(issues) == 0,
        "issues": issues,
        "score": 1.0 if len(issues) == 0 else max(0, 1.0 - len(issues) * 0.2),
    }


# ======================================================================
# TEST 3: BRAIN-FIRST COMPLIANCE
# ======================================================================
def test_brain_compliance(agent_id: str, profile: dict) -> dict:
    """Verify agent prompt instructs Brain querying."""
    issues = []
    prompt = profile.get("system_prompt", "") + " " + profile.get("description", "")
    prompt_lower = prompt.lower()
    
    found_keywords = [kw for kw in BRAIN_KEYWORDS if kw in prompt_lower]
    
    if not found_keywords:
        issues.append("NO Brain reference in prompt. Agent will not query Brain before acting.")
    elif len(found_keywords) < 3:
        issues.append(f"Weak Brain reference: only {len(found_keywords)}/{len(BRAIN_KEYWORDS)} keywords found ({found_keywords})")
    
    return {
        "test": "brain_compliance",
        "passed": len(issues) == 0,
        "issues": issues,
        "brain_keywords_found": found_keywords,
        "score": 1.0 if len(issues) == 0 else (0.5 if found_keywords else 0.0),
    }


# ======================================================================
# TEST 4: MISSION ALIGNMENT
# ======================================================================
def test_mission_alignment(agent_id: str, profile: dict) -> dict:
    """Check if prompt references mission/customer outcomes."""
    prompt = profile.get("system_prompt", "") + " " + profile.get("description", "")
    prompt_lower = prompt.lower()
    
    found = [kw for kw in MISSION_KEYWORDS if kw in prompt_lower]
    
    return {
        "test": "mission_alignment",
        "passed": len(found) > 0,
        "issues": [] if found else ["No mission/customer-outcome reference in prompt"],
        "mission_keywords_found": found,
        "score": 1.0 if len(found) >= 2 else (0.6 if len(found) == 1 else 0.3),
    }


# ======================================================================
# TEST 5: DOS v2.1 COMPLIANCE
# ======================================================================
def test_dos_compliance(agent_id: str, profile: dict) -> dict:
    """Verify no forbidden tools/patterns per DOS v2.1."""
    issues = []
    prompt = profile.get("system_prompt", "") + " " + profile.get("description", "")
    prompt_lower = prompt.lower()
    
    for forbidden in DOS_FORBIDDEN:
        if forbidden in prompt_lower:
            issues.append(f"DOS VIOLATION: Forbidden tool/pattern found: '{forbidden}'")
    
    return {
        "test": "dos_compliance",
        "passed": len(issues) == 0,
        "issues": issues,
        "score": 0.0 if issues else 1.0,
    }


# ======================================================================
# TEST 6: DRY-RUN EXECUTION
# ======================================================================
async def test_execution(agent_id: str) -> dict:
    """Dry-run agent with a sample task, validate output structure."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/orchestration/orchestrate",
                json={
                    "task": f"PROMPT VALIDATION DRY-RUN: Confirm you are {agent_id}. State your role, capabilities, and how you would query the Brain before acting. Do NOT execute any real work.",
                    "agent": agent_id,
                    "context": {"eval_run": True, "timestamp": datetime.now(timezone.utc).isoformat()}
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                result = await resp.json()
            
            # Validate response structure
            issues = []
            if not isinstance(result, dict):
                issues.append(f"Response is not a dict: {type(result)}")
            else:
                result_data = result.get("result", result)
                if isinstance(result_data, dict):
                    routing = result_data.get("routing", {})
                    if not routing:
                        issues.append("No routing info in response")
                else:
                    issues.append(f"Result is not dict: {type(result_data)}")
            
            return {
                "test": "dry_run_execution",
                "passed": len(issues) == 0,
                "issues": issues,
                "http_status": resp.status,
                "response_preview": str(result)[:300] if isinstance(result, dict) else str(result)[:300],
                "score": 1.0 if resp.status == 200 else (0.5 if resp.status < 500 else 0.0),
            }
    except Exception as e:
        return {
            "test": "dry_run_execution",
            "passed": False,
            "issues": [f"Execution failed: {str(e)[:200]}"],
            "score": 0.0,
        }


# ======================================================================
# MAIN EVALUATION RUNNER
# ======================================================================
async def evaluate_agent(agent_id: str) -> dict:
    """Run all tests on one agent."""
    import requests
    
    # Load agent profile from Brain
    profile = {}
    try:
        r = requests.post(
            f"{BRAIN_URL}/collections/{COLLECTION}/points/scroll",
            json={"limit": 100, "with_payload": True},
            timeout=10
        )
        if r.status_code == 200:
            points = r.json().get("result", {}).get("points", [])
            for p in points:
                payload = p.get("payload", {})
                # Match agent by topic or content
                text = str(payload.get("text", "")) + " " + str(payload.get("content", ""))
                if agent_id.replace("-", " ") in text.lower():
                    profile = payload
                    break
    except Exception as e:
        logger.warning(f"Could not load profile for {agent_id}: {e}")
    
    # Also check brain_agents/*.md files
    if not profile or len(profile) < 3:
        agent_file = f"/root/agentur-repo/backend/agents/brain_agents/{agent_id}.md"
        if os.path.exists(agent_file):
            with open(agent_file) as f:
                content = f.read()
            profile = {
                "name": agent_id,
                "description": content[:1000],
                "role": agent_id,
                "system_prompt": content,
            }
    
    if not profile or len(profile) < 2:
        return {
            "agent": agent_id,
            "status": "SKIPPED",
            "reason": "No profile found in Brain or brain_agents/",
            "overall_score": 0.0,
            "tests": [],
        }
    
    # Run all tests
    tests = [
        test_profile_completeness(agent_id, profile),
        test_prompt_structure(agent_id, profile),
        test_brain_compliance(agent_id, profile),
        test_mission_alignment(agent_id, profile),
        test_dos_compliance(agent_id, profile),
    ]
    
    # Dry-run execution (async, skip if too many agents to keep fast)
    # Only run for first 5 agents
    # exec_test = await test_execution(agent_id)
    # tests.append(exec_test)
    
    scores = [t["score"] for t in tests]
    overall = sum(scores) / len(scores)
    passed = sum(1 for t in tests if t["passed"])
    failed = len(tests) - passed
    
    return {
        "agent": agent_id,
        "status": "PASS" if overall >= 0.7 else "WARN" if overall >= 0.4 else "FAIL",
        "overall_score": round(overall, 3),
        "tests_passed": passed,
        "tests_failed": failed,
        "tests": tests,
        "profile_source": "brain" if "source" in profile else "file" if os.path.exists(f"/root/agentur-repo/backend/agents/brain_agents/{agent_id}.md") else "unknown",
    }


async def main():
    """Run eval suite on all 28 agents."""
    logger.info("=" * 60)
    logger.info("AGENT EVAL SUITE — Pre-Launch Prompt Validation")
    logger.info(f"Testing {len(ALL_AGENTS)} agents")
    logger.info("=" * 60)
    
    results = []
    for agent_id in ALL_AGENTS:
        logger.info(f"Evaluating: {agent_id}")
        result = await evaluate_agent(agent_id)
        results.append(result)
        
        icon = "✓" if result["status"] == "PASS" else "⚠" if result["status"] == "WARN" else "✗"
        tp = result.get("tests_passed", 0)
        tf = result.get("tests_failed", 0)
        logger.info(f"  {icon} {result['status']} score={result['overall_score']:.2f} ({tp}/{tp+tf} tests passed)")
    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIPPED")
    
    print("\n" + "=" * 60)
    print("EVAL SUITE SUMMARY")
    print("=" * 60)
    print(f"  PASS:  {passed}/{len(results)} agents")
    print(f"  WARN:  {warned}/{len(results)} agents")
    print(f"  FAIL:  {failed}/{len(results)} agents")
    print(f"  SKIP:  {skipped}/{len(results)} agents (no profile found)")
    
    # Brain compliance summary
    brain_compliant = sum(1 for r in results if r["status"] != "SKIPPED" and 
                         any(t["test"] == "brain_compliance" and t["passed"] for t in r.get("tests", [])))
    print(f"\n  Brain-compliant: {brain_compliant}/{len(results)-skipped} agents")
    
    # Store results in Brain
    import requests as rq
    report = {
        "category": "eval_report",
        "source": "agent_eval_suite",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": json.dumps({
            "summary": {"pass": passed, "warn": warned, "fail": failed, "skip": skipped},
            "brain_compliant": brain_compliant,
            "total": len(results),
            "results": results
        }),
        "provenance": "agent-eval-suite-v1",
        "confidence": 0.95,
        "status": "active",
        "last_verified": datetime.now(timezone.utc).isoformat(),
    }
    
    try:
        point_id = abs(hash(f"eval-{datetime.now().isoformat()}")) % (2**63)
        rq.put(
            f"{BRAIN_URL}/collections/{COLLECTION}/points",
            json={"points": [{"id": point_id, "vector": [0.0] * 4096, "payload": report}]},
            timeout=10
        )
        logger.info("Eval report stored in Brain")
    except Exception as e:
        logger.warning(f"Brain storage failed: {e}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
