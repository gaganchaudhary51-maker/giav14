from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.core.model_router import route
from app.models.budget import decide
router=APIRouter(prefix="/models",tags=["models"])
class RouteRequest(BaseModel):
    text:str=Field(min_length=1,max_length=10000); risk:str="low"; complexity:str="simple"; failure_count:int=0
class BudgetRequest(BaseModel):
    task_type:str=Field(min_length=1,max_length=100); complexity:str="simple"; failure_count:int=0
class ContextRequest(BaseModel):
    task:str=Field(min_length=1,max_length=10000); files:list[str]=Field(default_factory=list,max_length=500); memories:list[str]=Field(default_factory=list,max_length=500); char_budget:int=Field(default=12000,ge=100,le=100000)
def auth(a):
    if not a or not a.startswith("Bearer "): raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid: raise HTTPException(401,"Invalid or expired token")
    return uid
@router.post("/route")
def model_route(p:RouteRequest,authorization:str|None=Header(default=None)):
    auth(authorization); complexity=p.complexity
    if complexity=="simple" and any(x in p.text.lower() for x in ["debug","database","api","bug","fix"]):
        complexity="medium"
    d=route(p.text,p.risk,complexity)
    return {"tier":("medium" if d.tier=="standard" else d.tier),"reason":d.reason,"estimated_priority":d.estimated_priority}
@router.post("/escalate")
def escalate(p:RouteRequest,authorization:str|None=Header(default=None)):
    auth(authorization); d=route(p.text,p.risk,"complex" if p.failure_count>=2 else p.complexity)
    return {"to":("premium" if p.failure_count>=2 else ("medium" if d.tier=="standard" else d.tier)),"reason":d.reason}
@router.post("/context")
def context(p:ContextRequest,authorization:str|None=Header(default=None)):
    auth(authorization); chunks=[]; used=0
    for item in p.files+p.memories:
        remaining=p.char_budget-used
        if remaining<=0: break
        take=item[:remaining]; chunks.append(take); used+=len(take)
    return {"task":p.task,"context":chunks,"chars_used":used,"estimated_chars":used,"char_budget":p.char_budget}
@router.post("/budget")
def budget(p:BudgetRequest,authorization:str|None=Header(default=None)):
    auth(authorization); return decide(p.task_type,p.complexity,p.failure_count).__dict__
