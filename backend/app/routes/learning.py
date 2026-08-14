from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.learning.engine import learning_engine
from app.learning.updater import learn_from_result, self_update_policy

router=APIRouter(prefix="/learning",tags=["learning"])
class Lesson(BaseModel):
    agent:str=Field(min_length=1,max_length=100)
    domain:str=Field(min_length=1,max_length=100)
    lesson:str=Field(min_length=1,max_length=5000)
    evidence:str=Field(min_length=1,max_length=10000)
    tests_passed:bool=False

def auth(a):
    if not a or not a.startswith("Bearer ") or not verify_token(a[7:]): raise HTTPException(401,"Authentication required")

@router.post("/learn")
def learn(payload:Lesson,authorization:str|None=Header(default=None)):
    auth(authorization); return learn_from_result(payload.agent,payload.domain,payload.lesson,payload.evidence,payload.tests_passed)

@router.get("/recent")
def recent(authorization:str|None=Header(default=None)):
    auth(authorization); return {"items":learning_engine.recent()}

@router.get("/policy")
def policy(authorization:str|None=Header(default=None)):
    auth(authorization); return self_update_policy()
