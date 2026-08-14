from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.verification.state import verification_store
from app.audit.log import audit_log
router=APIRouter(prefix="/verification",tags=["verification"])
class Create(BaseModel): task_id:str=Field(min_length=1,max_length=200)
class Transition(BaseModel):
    state:str=Field(min_length=1,max_length=30)
    evidence:list[object]=Field(default_factory=list,max_length=50)
def auth(a):
    if not a or not a.startswith("Bearer "):raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid:raise HTTPException(401,"Invalid or expired token")
    return uid
@router.post("",status_code=201)
def create(p:Create,authorization:str|None=Header(default=None)):
    uid=auth(authorization);out=verification_store.create(p.task_id)
    audit_log.append("VERIFICATION_CREATED",uid,out);return out
@router.post("/{verification_id}/transition")
def transition(verification_id:str,p:Transition,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    try:out=verification_store.transition(verification_id,p.state,p.evidence)
    except ValueError as e:raise HTTPException(409,str(e))
    if not out:raise HTTPException(404,"Verification record not found")
    audit_log.append("VERIFICATION_STATE_CHANGED",uid,out);return out
@router.get("/{verification_id}")
def get(verification_id:str,authorization:str|None=Header(default=None)):
    auth(authorization);out=verification_store.get(verification_id)
    if not out:raise HTTPException(404,"Verification record not found")
    return out
