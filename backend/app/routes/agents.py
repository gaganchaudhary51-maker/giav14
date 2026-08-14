from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.agents.registry import agent_registry

router=APIRouter(prefix="/agents",tags=["agents"])
class Assemble(BaseModel):
    domains:list[str]=Field(default_factory=list,max_length=20)
    capabilities:list[str]=Field(default_factory=list,max_length=50)
def auth(a):
    if not a or not a.startswith("Bearer ") or not verify_token(a[7:]): raise HTTPException(401,"Authentication required")
@router.get("")
def list_agents(authorization:str|None=Header(default=None)):
    auth(authorization); return {"agents":agent_registry.list()}
@router.post("/assemble")
def assemble(payload:Assemble,authorization:str|None=Header(default=None)):
    auth(authorization); return {"agents":agent_registry.assemble(payload.domains,payload.capabilities)}
