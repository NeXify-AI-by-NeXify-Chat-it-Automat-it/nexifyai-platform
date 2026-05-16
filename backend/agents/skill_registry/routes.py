"""Skill Registry API Routes."""
from fastapi import APIRouter, BackgroundTasks
from .registry import list_skills, get_skill, sync_skills_to_brain

skill_router = APIRouter(prefix="/api/skills", tags=["skills"])

@skill_router.get("/")
async def list_all_skills():
    skills = list_skills()
    return {"agents": skills, "count": len(skills)}

@skill_router.get("/{agent_slug}")
async def get_agent_skill(agent_slug: str):
    content = get_skill(agent_slug)
    if not content:
        return {"error": f"Agent '{agent_slug}' not found", "available": list_skills()}
    return {"agent": agent_slug, "skill": content}

@skill_router.post("/sync")
async def sync_skills(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_skills_to_brain)
    return {"status": "syncing", "message": "Skills sync initiated in background"}
