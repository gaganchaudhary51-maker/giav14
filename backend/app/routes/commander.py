from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.commander.router import dispatch
from app.tasks.store import task_store
from app.events.bus import event_bus

router=APIRouter(prefix="/commander",tags=["commander"])
class Command(BaseModel):
    text:str=Field(min_length=1,max_length=10000)
    risk:str="LOW"; complexity:str="normal"; failure_count:int=0
def auth(a):
    if not a or not a.startswith("Bearer ") or not verify_token(a[7:]): raise HTTPException(401,"Authentication required")
@router.post("/dispatch")
def run(payload:Command,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    result=dispatch(payload.text,payload.risk,payload.complexity,payload.failure_count)
    task=task_store.create(payload.text,result["model"],[a["id"] for a in result["agents"]],result["requires_approval"])
    event_bus.publish("TASK_CREATED",task)
    return {**result,"task":task}
