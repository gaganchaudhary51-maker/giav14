from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.approvals.store import approval_store
from app.audit.log import audit_log
from app.events.bus import event_bus
from app.tasks.store import task_store

router=APIRouter(prefix="/approvals",tags=["approvals"])

class Request(BaseModel):
    task_id:str=Field(min_length=1,max_length=200)
    action:str=Field(min_length=1,max_length=200)
    reason:str=Field(min_length=1,max_length=5000)
    risk:str=Field(min_length=1,max_length=100)

class Resolve(BaseModel):
    approve:bool

def auth(a):
    if not a or not a.startswith("Bearer "): raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid: raise HTTPException(401,"Invalid or expired token")
    return uid

@router.post("",status_code=201)
def request(payload:Request,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    task = task_store.get(payload.task_id)
    if task:
        if task.get("owner_id") not in (None, uid):
            raise HTTPException(404, "Task not found")
        if task["status"] != "APPROVAL_REQUIRED":
            raise HTTPException(409, "Task is not waiting for approval")
    item=approval_store.request(payload.task_id,payload.action,payload.reason,payload.risk,uid)
    event_bus.publish("APPROVAL_REQUIRED",item)
    audit_log.append("APPROVAL_REQUESTED",uid,item)
    return item

@router.post("/{approval_id}/resolve")
def resolve(approval_id:str,payload:Resolve,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    existing = approval_store.get(approval_id, owner_id=uid)
    if not existing:
        raise HTTPException(404, "Approval not found")
    if existing["status"] != "PENDING":
        raise HTTPException(409, "Approval already resolved")
    item=approval_store.resolve(approval_id,uid,payload.approve)
    if not item:
        raise HTTPException(409, "Approval already resolved")
    # Link approval resolution to the task lifecycle when the referenced task exists.
    task = task_store.get(item["task_id"])
    if task and task["status"] == "APPROVAL_REQUIRED":
        try:
            updated = task_store.update(
                item["task_id"], "APPROVED" if payload.approve else "FAILED"
            )
            event_bus.publish("TASK_APPROVED" if payload.approve else "TASK_FAILED", updated)
        except ValueError as exc:
            raise HTTPException(409, str(exc))
    event_bus.publish("APPROVAL_GRANTED" if payload.approve else "APPROVAL_REJECTED",item)
    audit_log.append("APPROVAL_RESOLVED",uid,item)
    return item

@router.get("/{approval_id}")
def get(approval_id:str,authorization:str|None=Header(default=None)):
    auth(authorization)
    item=approval_store.get(approval_id, owner_id=auth(authorization))
    if not item: raise HTTPException(404,"Approval not found")
    return item
