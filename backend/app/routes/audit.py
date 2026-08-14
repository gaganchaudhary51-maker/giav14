from fastapi import APIRouter, Header, HTTPException
from app.auth.security import verify_token
from app.audit.log import audit_log
import json

router=APIRouter(prefix="/audit",tags=["audit"])

@router.post("/record")
def record(event_type:str, payload:str="", authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")
    return audit_log.append(event_type,"user",{"payload":payload})

@router.get("/recent")
def recent(limit:int=50, authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")
    if not audit_log.path.exists(): return {"items":[]}
    lines=audit_log.path.read_text(encoding="utf-8").splitlines()[-min(max(limit,1),100):]
    return {"items":[json.loads(x) for x in lines]}
