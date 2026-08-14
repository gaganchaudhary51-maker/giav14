from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.execution.runner import execution_engine
from app.audit.log import audit_log

router=APIRouter(prefix="/execution",tags=["execution"])
class Execute(BaseModel):
    task_id:str=Field(min_length=1,max_length=200)
    action:str=Field(min_length=1,max_length=100)
    output:str=Field(default="",max_length=10000)

def auth(a):
    if not a or not a.startswith("Bearer ") or not verify_token(a[7:]):
        raise HTTPException(401,"Authentication required")

@router.post("")
def execute(payload:Execute,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    try: item=execution_engine.execute(payload.task_id,payload.action,payload.output)
    except PermissionError as e: raise HTTPException(403,str(e))
    except ValueError as e: raise HTTPException(400,str(e))
    audit_log.append("TOOL_EXECUTED",uid,item)
    return item
