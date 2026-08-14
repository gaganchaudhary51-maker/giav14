from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.core.agent_team import assemble
from app.core.model_router import route
from app.core.approvals import requires_approval
from app.tasks.store import task_store
from app.events.bus import event_bus

router=APIRouter(prefix="/tasks",tags=["tasks"])

class TaskRequest(BaseModel):
    text:str=Field(min_length=1,max_length=10000)

def auth(authorization):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")

@router.post("",status_code=201)
def create_task(payload:TaskRequest,authorization:str|None=Header(default=None)):
    auth(authorization)
    team=assemble(payload.text)
    decision=route(payload.text)
    approval=any(x in payload.text.lower() for x in ["deploy","production","delete","secret"])
    task=task_store.create(payload.text,decision.tier,team,approval)
    event_bus.publish("TASK_CREATED",task)
    if approval: event_bus.publish("APPROVAL_REQUIRED",{"task_id":task["id"]})
    return task

@router.get("/{task_id}")
def get_task(task_id:str,authorization:str|None=Header(default=None)):
    auth(authorization)
    task=task_store.get(task_id)
    if not task: raise HTTPException(404,"Task not found")
    return task

@router.post("/{task_id}/status")
def update_status(task_id:str,status:str,authorization:str|None=Header(default=None)):
    auth(authorization)
    allowed={"PLANNED","APPROVAL_REQUIRED","APPROVED","EXECUTING","EXECUTED","VERIFYING","VERIFIED","FAILED","ROLLED_BACK"}
    if status not in allowed: raise HTTPException(400,"Invalid task state")
    task=task_store.update(task_id,status)
    if not task: raise HTTPException(404,"Task not found")
    event_bus.publish(f"TASK_{status}",task)
    return task
