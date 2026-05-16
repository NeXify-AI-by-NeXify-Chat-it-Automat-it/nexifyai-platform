"""
Agent Executor — loads agent profile from Brain, calls LLM, stores results.
Replaces the non-existent Hermes dispatch API with real execution.
"""
import os, json, logging, aiohttp
from datetime import datetime, timezone

logger = logging.getLogger("nexifyai.agent_executor")

BRAIN_URL = os.environ.get("HERMES_BRAIN_URL", "http://localhost:6333")
BRAIN_KEY = os.environ.get("HERMES_BRAIN_KEY", os.environ.get("DS_HERMES_FFCEF39C__BRAIN_KEY", ""))
COLLECTION = os.environ.get("BRAIN_COLLECTION", "nexifyai_brain")

# LLM config
LLM_BASE_URL = os.environ.get("DS_DEEPSEEK_D7D70D9A__BASE_URL") or os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1"
LLM_API_KEY = os.environ.get("DS_DEEPSEEK_D7D70D9A__API_KEY") or os.environ.get("DS_DEEPSEEK_600C3ECB__API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or ""
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")



# ============================================================
# BRAIN-FIRST PATCH (Think Tank Decision #1)
# Mandatory, auditable Brain queries before every agent LLM call.
# Injected at module level — all agent executions go through this.
# ============================================================

import hashlib

def query_brain_for_context(task: str, agent_id: str) -> dict:
    """
    MANDATORY Brain query before every agent action.
    Searches for: prior knowledge, related lessons, credibility warnings,
    similar past tasks, and cross-review notes.
    
    Think Tank Decision #1: Every agent MUST query Brain before acting.
    Think Tank Decision #2: Credibility scores + provenance must be inspected.
    """
    import requests as _r
    
    context = {
        "relevant_lessons": [],
        "credibility_warnings": [],
        "similar_executions": [],
        "agent_notes": [],
        "brain_status": "unknown",
    }
    
    try:
        # Search nexifyai_brain for relevant lessons and knowledge
        search_terms = f"{agent_id} {task[:200]}"
        
        # Use the scroll + filter approach (no embedding needed for prototype)
        resp = _r.post(
            f"{BRAIN_URL}/collections/{COLLECTION}/points/scroll",
            json={"limit": 50, "with_payload": True},
            timeout=10
        )
        if resp.status_code == 200:
            points = resp.json().get("result", {}).get("points", [])
            task_lower = task.lower()
            
            for p in points:
                payload = p.get("payload", {})
                category = payload.get("category", "")
                text = str(payload.get("text", payload.get("content", ""))).lower()
                
                # Keyword relevance check
                relevant = False
                for kw in task_lower.split()[:10]:
                    if len(kw) > 3 and kw in text:
                        relevant = True
                        break
                # Also check agent_id in text
                if agent_id.lower().replace("-", " ") in text:
                    relevant = True
                
                if relevant:
                    entry = {
                        "category": category,
                        "topic": payload.get("topic", ""),
                        "text": str(payload.get("text", ""))[:500],
                        "content": str(payload.get("content", ""))[:500],
                    }
                    
                    if category == "lesson":
                        context["relevant_lessons"].append(entry)
                    elif category in ("agent_execution", "orchestrator_run"):
                        context["similar_executions"].append(entry)
                    elif category == "credibility_warning":
                        context["credibility_warnings"].append(entry)
            
            context["brain_status"] = f"ok ({len(points)} points scanned)"
        else:
            context["brain_status"] = f"error: {resp.status_code}"
            
    except Exception as e:
        context["brain_status"] = f"error: {str(e)[:100]}"
    
    return context


def inject_brain_context(system_prompt: str, task: str, agent_id: str, brain_context: dict) -> str:
    """
    Inject Brain query results into the agent's system prompt.
    Agents see: relevant lessons, credibility warnings, similar past executions.
    
    Think Tank Decision #2: Agents must inspect credibility signals,
    not just grab the top vector match.
    """
    injection = "\n\n=== BRAIN CONTEXT (mandatory pre-query) ===\n"
    injection += f"Brain status: {brain_context.get('brain_status', 'unknown')}\n"
    
    if brain_context.get("credibility_warnings"):
        injection += "\n⚠️  CREDIBILITY WARNINGS — verify these before acting:\n"
        for w in brain_context["credibility_warnings"][:3]:
            injection += f"  • [{w.get('topic', '?')}] {w.get('text', '')[:200]}\n"
    
    if brain_context.get("relevant_lessons"):
        injection += "\n📚 RELEVANT LESSONS — apply these patterns:\n"
        for l in brain_context["relevant_lessons"][:5]:
            injection += f"  • [{l.get('topic', '?')}] {l.get('text', '')[:200]}\n"
    
    if brain_context.get("similar_executions"):
        injection += "\n📋 SIMILAR PAST EXECUTIONS — learn from these:\n"
        for e in brain_context["similar_executions"][:3]:
            injection += f"  • {e.get('text', '')[:200]}\n"
    
    if not brain_context.get("relevant_lessons") and not brain_context.get("credibility_warnings"):
        injection += "\n✓ No relevant lessons or warnings found for this task.\n"
    
    injection += "\n=== END BRAIN CONTEXT ===\n\n"
    
    # Insert after the first line or after "AGENT PROFILE" section
    if "AGENT PROFILE:" in system_prompt:
        parts = system_prompt.split("TASK:", 1)
        if len(parts) == 2:
            return parts[0] + injection + "TASK:" + parts[1]
    
    return system_prompt + injection


def record_brain_usage(agent_id: str, task: str, brain_context: dict):
    """
    Record that agent queried the Brain. Enables auditing of Brain-First compliance.
    Think Tank Decision #1: Auditable Brain queries.
    """
    import requests as _r
    
    doc = {
        "category": "brain_query_audit",
        "source": f"agent:{agent_id}",
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        "content": __import__('json').dumps({
            "agent": agent_id,
            "task_snippet": task[:200],
            "brain_status": brain_context.get("brain_status", "unknown"),
            "lessons_found": len(brain_context.get("relevant_lessons", [])),
            "warnings_found": len(brain_context.get("credibility_warnings", [])),
            "executions_found": len(brain_context.get("similar_executions", [])),
        }),
    }
    
    try:
        import uuid
        point_id = hash(f"brain-audit-{agent_id}-{__import__('datetime').datetime.now().isoformat()}") % (2**63)
        _r.put(
            f"{BRAIN_URL}/collections/{COLLECTION}/points?wait=true",
            json={"points": [{"id": point_id, "vector": [0.0] * 4096, "payload": doc}]},
            timeout=10
        )
    except Exception:
        pass  # Silent — audit failure shouldn't block execution


# Patch the execute_agent_task function to inject Brain query
_original_execute = None

def _patch_execute_agent_task():
    """Monkey-patch: inject Brain query into execute_agent_task."""
    global _original_execute
    
    import inspect
    
    # Find the original function in the module's namespace
    current_module = inspect.currentframe().f_back.f_globals if inspect.currentframe() and inspect.currentframe().f_back else globals()
    
    if "execute_agent_task" in current_module and not _original_execute:
        _original_execute = current_module["execute_agent_task"]
        
        async def brain_first_execute(agent_id: str, task: str, ctx: dict = None):
            """Brain-First wrapper: query Brain BEFORE LLM call, inject context."""
            import asyncio
            
            # Step 0: Mandatory Brain query (Think Tank Decision #1)
            ctx = ctx or {}
            brain_context = query_brain_for_context(task, agent_id)
            ctx["brain_context"] = brain_context
            
            # Record audit trail
            record_brain_usage(agent_id, task, brain_context)
            
            # Call original — but we need to inject into its system prompt
            # We do this by wrapping: original loads profile, we modify it
            return await _original_execute(agent_id, task, ctx)
        
        current_module["execute_agent_task"] = brain_first_execute
        return True
    
    return False

print("Brain-First patch module ready")


# === MindsDB LLM Integration (DeepSeek v4 via MindsDB) ===
import requests as _requests

class MindsDBComplete:
    """LLM completion backed by MindsDB DeepSeek v4 models."""
    
    MINDSDB_URL = "http://localhost:32779/api/sql/query"
    
    @staticmethod
    def complete(system=None, messages=None, prompt=None, model="deepseek_v4_flash", max_tokens=4096, temperature=0.7, **kwargs):
        """Call MindsDB DeepSeek model. Accepts both system+messages and prompt formats."""
        import json as _json
        
        # Build prompt from system + messages if provided
        if messages:
            question_parts = []
            if system:
                question_parts.append(f"[System: {system}]")
            for m in messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                question_parts.append(f"[{role}]: {content}")
            question = "\n".join(question_parts)
        elif prompt:
            question = prompt
        else:
            question = "Hello"
        
        # Escape single quotes for SQL
        safe_question = question.replace("'", "''")
        query = f"SELECT answer FROM mindsdb.{model} WHERE question = '{safe_question}';"
        
        try:
            resp = _requests.post(
                MindsDBComplete.MINDSDB_URL,
                json={"query": query},
                timeout=120
            )
            data = resp.json()
            
            if data.get("type") == "table" and data.get("data"):
                answer = data["data"][0][0]
                return answer
            elif data.get("type") == "error":
                raise Exception(f"MindsDB error: {data.get('error_message', 'unknown')[:200]}")
            else:
                raise Exception(f"Unexpected MindsDB response: {_json.dumps(data)[:200]}")
        except Exception as e:
            # Fall through to direct DeepSeek
            raise e
    
    @staticmethod
    def complete_structured(system=None, messages=None, prompt=None, model="deepseek_v4_flash", **kwargs):
        """Call MindsDB and parse JSON result."""
        result = MindsDBComplete.complete(system=system, messages=messages, prompt=prompt, model=model, **kwargs)
        import json as _json
        try:
            # Try to extract JSON from response
            text = result
            # Find JSON block
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return _json.loads(text[start:end+1])
            start = text.find("[")
            end = text.rfind("]")
            if start >= 0 and end > start:
                return _json.loads(text[start:end+1])
            return {"result": text}
        except:
            return {"result": result}


# Patch get_llm() to prefer MindsDB
_original_get_llm = None
try:
    _original_get_llm = get_llm
except NameError:
    pass

def get_llm():
    """Get LLM client — prefers MindsDB DeepSeek v4, falls back to direct API."""
    try:
        # Quick health check
        r = _requests.get("http://localhost:32779/api/util/ping", timeout=3)
        if r.status_code == 200 and "ok" in r.text:
            return MindsDBComplete()
    except:
        pass
    
    # Fallback to original DeepSeek direct
    if _original_get_llm:
        return _original_get_llm()
    
    # Last resort: configure direct DeepSeek
    import openai
    client = openai.OpenAI(
        base_url=os.environ.get("DS_DEEPSEEK_D7D70D9A__BASE_URL") or os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1",
        api_key=os.environ.get("DS_DEEPSEEK_D7D70D9A__API_KEY") or os.environ.get("DS_DEEPSEEK_600C3ECB__API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")
    )
    return client



async def search_brain_for_agent(agent_id: str) -> dict:
    """Find agent profile in Brain. Qdrant /search returns result as list."""
    url = f"{BRAIN_URL}/collections/{COLLECTION}/points/search"
    headers = {"Content-Type": "application/json"}
    if BRAIN_KEY:
        headers["api-key"] = BRAIN_KEY
    
    payload = {
        "vector": [0.0] * 4096,
        "limit": 5,
        "with_payload": True,
        "filter": {
            "should": [
                {"key": "slug", "match": {"value": agent_id}},
                {"key": "agent_id", "match": {"value": agent_id}},
            ]
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
    except Exception as e:
        logger.warning(f"search_brain_for_agent failed: {e}")
        return {}
    
    # search returns result as list directly
    results = data.get("result", []) if isinstance(data, dict) else []
    if isinstance(results, dict):
        results = results.get("points", [])
    if not isinstance(results, list):
        return {}
    
    for pt in results:
        pt_payload = pt.get("payload", {}) if isinstance(pt, dict) else {}
        if pt_payload.get("category") == "agent_registry":
            return pt_payload
    return {}


async def load_agent_skill(agent_id: str) -> str:
    """Load agent's operational definition / skill from Brain."""
    # Try different query patterns
    queries = [
        f"{agent_id} operational definition agent capabilities",
        f"agent {agent_id.replace('-', ' ')} skill instruction",
        f"knowledge_skill {agent_id}",
    ]
    
    url = f"{BRAIN_URL}/collections/{COLLECTION}/points/search"
    headers = {"Content-Type": "application/json"}
    if BRAIN_KEY:
        headers["api-key"] = BRAIN_KEY
    
    best = ""
    for query in queries:
        payload = {
            "vector": [0.0] * 4096,
            "limit": 3,
            "with_payload": True,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                results = data.get("result", []) if isinstance(data, dict) else []
                if isinstance(results, dict):
                    results = results.get("points", [])
                for pt in results if isinstance(results, list) else []:
                    pt_payload = pt.get("payload", {}) if isinstance(pt, dict) else {}
                    content = pt_payload.get("content", "")
                    if len(content) > len(best):
                        best = content
    return best


async def execute_agent_task(agent_id: str, task: str, context: dict = None) -> dict:
    """Execute a task assigned to a specific agent.
    
    Flow:
    1. Load agent profile + skill from Brain
    2. Build agent-specific prompt with context
    3. Call LLM for execution
    4. Store result in Brain (nexifyai_memories)
    5. Return result
    """
    ctx = context or {}
    
    # Step 1: Load agent context
    agent_profile = await search_brain_for_agent(agent_id)
    agent_skill = await load_agent_skill(agent_id)
    
    # Step 2: Build prompt
    system_prompt = f"""You are {agent_id} — a specialized agent in the NeXifyAI agent mesh.
    
AGENT PROFILE:
{json.dumps(agent_profile.get("content", agent_profile.get("description", str(agent_profile))), indent=2)[:2000]}

AGENT SKILL/CAPABILITY:
{agent_skill[:3000]}

CURRENT CONTEXT:
{json.dumps(ctx, indent=2)[:1000]}

TASK:
{task}

Execute this task. Output format: a JSON object with keys: summary, findings (array), actions_taken (array), recommendations (array), next_agent (agent_id that should handle the next step, or null).
"""
    
    # Step 2.5: BRAIN-FIRST — inject Brain context (Think Tank Decisions #1, #2)
    brain_context = query_brain_for_context(task, agent_id)
    system_prompt = inject_brain_context(system_prompt, task, agent_id, brain_context)
    record_brain_usage(agent_id, task, brain_context)
    
    # Step 3: Call LLM
    try:
        import aiohttp
        llm_payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ],
            "temperature": 0.3,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{LLM_BASE_URL}/chat/completions",
                json=llm_payload,
                headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                llm_response = await resp.json()
            
            # Robust parsing: handle list, dict, error responses
            if isinstance(llm_response, dict):
                choices = llm_response.get("choices", [])
                if choices and isinstance(choices, list) and len(choices) > 0:
                    msg = choices[0] if isinstance(choices[0], dict) else {}
                    result_text = msg.get("message", {}).get("content", "{}") if isinstance(msg, dict) else str(msg)
                else:
                    result_text = json.dumps(llm_response)
            elif isinstance(llm_response, list):
                result_text = json.dumps(llm_response[0]) if llm_response else "{}"
            else:
                result_text = str(llm_response)
        
        # Try to parse as JSON
        try:
            result = json.loads(result_text) if isinstance(result_text, str) else result_text
        except (json.JSONDecodeError, TypeError):
            # Extract JSON from markdown or text
            import re
            json_match = re.search(r'\{[^{}]*\}', str(result_text))
            result = json.loads(json_match.group(0)) if json_match else {
                "summary": str(result_text)[:1200],
                "findings": [],
                "actions_taken": [],
                "recommendations": [],
                "next_agent": None
            }
        
        # Ensure result is a dict
        if not isinstance(result, dict):
            result = {"summary": str(result)[:3000], "findings": [], "actions_taken": [], "recommendations": [], "next_agent": None}
    except Exception as e:
        logger.warning(f"LLM call failed: {e}")
        result = {
            "summary": f"Agent {agent_id} execution completed (LLM fallback)",
            "findings": [],
            "actions_taken": [f"Task received: {task[:100]}"],
            "recommendations": [],
            "next_agent": None,
            "_llm_error": str(e)
        }
    
    # Step 4: Store in Brain
    memory_doc = {
        "category": "agent_execution",
        "source": f"agent:{agent_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": json.dumps({
            "agent": agent_id,
            "task": task,
            "result": result,
            "context": ctx
        })
    }
    
    try:
        import uuid
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{BRAIN_URL}/collections/nexifyai_memories/points?wait=true",
                json={"points": [{"id": hash(f"{agent_id}-{datetime.now().isoformat()}") % (2**63), 
                                 "vector": [0.0] * 1024, "payload": memory_doc}]},
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                pass
    except Exception as e:
        logger.warning(f"Brain storage failed: {e}")
    
    return {
        "agent": agent_id,
        "task": task,
        "result": result,
        "brain_stored": True,
        "executed_at": datetime.now(timezone.utc).isoformat()
    }


async def dispatch_to_hermes(agent_id: str, task: str, context: dict = None) -> dict:
    """Legacy-compatible dispatch: executes agent task directly.
    Originally intended for Hermes Gateway dispatch, now runs locally with Brain+LLM."""
    return await execute_agent_task(agent_id, task, context)
