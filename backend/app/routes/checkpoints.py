from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.checkpoints.store import checkpoint_store
from app.projects.store import project_store
from app.audit.log import audit_log
router=APIRouter(prefix="/checkpoints",tags=["checkpoints"])
class Create(BaseModel):
    project_id:str=Field(min_length=1,max_length=200); label:str=Field(min_length=1,max_length=200); state:dict
def auth(a):
    if not a or not a.startswith("Bearer "):raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid:raise HTTPException(401,"Invalid or expired token")
    return uid
@router.post("",status_code=201)
def create(payload:Create,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    project=project_store.get(payload.project_id,uid)
    # Preserve the legacy evidence-only checkpoint API for external task IDs.
    # Real project checkpoints remain owner-scoped and can perform actual file restore.
    item=checkpoint_store.create(payload.project_id,payload.label,payload.state,uid)
    audit_log.append("CHECKPOINT_CREATED",uid,item);return item
@router.get("/{project_id}")
def list_checkpoints(project_id:str,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    return {"items":checkpoint_store.list(project_id,uid)}
@router.post("/{checkpoint_id}/rollback")
def rollback(checkpoint_id:str,authorization:str|None=Header(default=None)):
    uid=auth(authorization);item=checkpoint_store.get(checkpoint_id,uid)
    if not item:raise HTTPException(404,"Checkpoint not found")
    project=project_store.get(item["project_id"],uid)
    state=item["state"];files=state.get("files")
    if project and isinstance(files,dict):
        project_store.replace_files(item["project_id"],uid,files)
        audit_log.append("ROLLBACK_COMPLETED",uid,item)
        return {"status":"ROLLED_BACK","checkpoint":item}
    # Evidence-only checkpoint: preserve the historical contract; nothing is mutated.
    audit_log.append("ROLLBACK_REQUESTED",uid,item)
    return {"status":"ROLLBACK_READY","checkpoint":item}
