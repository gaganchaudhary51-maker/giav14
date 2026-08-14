from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.projects.store import project_store
from app.workspace.diff import calculate_diff,apply_changes
from app.checkpoints.store import checkpoint_store
from app.audit.log import audit_log
router=APIRouter(prefix="/workspace",tags=["workspace"])
class Edit(BaseModel):
    changes:dict[str,str]=Field(min_length=1,max_length=100)
def auth(a):
    if not a or not a.startswith("Bearer "):raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid:raise HTTPException(401,"Invalid or expired token")
    return uid
@router.post("/{project_id}/edit")
def edit(project_id:str,p:Edit,authorization:str|None=Header(default=None)):
    uid=auth(authorization);old=project_store.get(project_id,uid)
    if not old:raise HTTPException(404,"Project not found")
    try:new=apply_changes(old["files"],p.changes)
    except ValueError as e:raise HTTPException(400,str(e))
    checkpoint=checkpoint_store.create(project_id,"pre-edit",{"files":old["files"],"stack":old["stack"]},uid)
    diffs={k:calculate_diff(old["files"].get(k,""),v,k) for k,v in p.changes.items()}
    project_store.write_files(project_id,uid,p.changes)
    audit_log.append("WORKSPACE_EDITED",uid,{"project_id":project_id,"files":list(p.changes),"checkpoint_id":checkpoint["id"]})
    return {"project_id":project_id,"changed_files":list(p.changes),"diffs":diffs,"checkpoint_id":checkpoint["id"],"status":"EDITED"}
