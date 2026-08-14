from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.skills.registry import skill_registry
from app.core.agent_team import skills_for_team

router=APIRouter(prefix="/skills",tags=["skills"])

class SkillRequest(BaseModel):
    domain:str=Field(min_length=1,max_length=100)

@router.post("/domain")
def domain_skills(payload:SkillRequest,authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")
    return {"domain":payload.domain,"skills":skill_registry.for_domain(payload.domain)}

@router.get("/domains")
def domains(authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")
    return {"domains":skill_registry.all_domains()}

class TeamRequest(BaseModel):
    task:str=Field(min_length=1,max_length=10000)
@router.post("/team")
def team(payload:TeamRequest,authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")
    return {"task":payload.task,"skills":skills_for_team(payload.task)}
