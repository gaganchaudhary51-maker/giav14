from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime, timezone
import json, os, uuid

from app.auth.security import verify_token
from app.projects.store import project_store
from app.builder.crud import normalize_spec, generate_manifest
from app.builder.spec import AppSpec
from app.builder.crud_plan import build_crud_plan
from app.builder.pipeline import build_pipeline
from app.approvals.store import approval_store
from app.audit.log import audit_log

router=APIRouter(prefix="/builder",tags=["builder"])

class LegacyPlan(BaseModel):
    name:str=Field(min_length=1,max_length=200)
    resources:list[str]=Field(default_factory=list,max_length=100)

class Create(BaseModel):
    project_id:str=Field(min_length=1,max_length=200)
    entity:str=Field(min_length=1,max_length=100)
    fields:list[str]=Field(default_factory=list,max_length=100)
    roles:list[str]=Field(default_factory=list,max_length=20)
    sensitive:bool=False

def auth(a):
    if not a or not a.startswith("Bearer "):
        raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid: raise HTTPException(401,"Invalid or expired token")
    return uid

# Legacy planning endpoint: specification only, no execution.
@router.post("/crud/plan")
def crud_plan(payload:LegacyPlan):
    plan=build_crud_plan(AppSpec(name=payload.name,resources=payload.resources))
    return {"status":"planned","plan":plan}

# Legacy checkpoint endpoint: creates a filesystem evidence checkpoint of the plan only.
@router.post("/crud/checkpoint")
def crud_checkpoint(payload:LegacyPlan):
    plan=build_crud_plan(AppSpec(name=payload.name,resources=payload.resources))
    root=Path(os.getenv("GIA_WORKSPACE_ROOT","/tmp/gia-workspace"))
    checkpoint=root/"checkpoints"/f"{uuid.uuid4().hex}.json"
    checkpoint.parent.mkdir(parents=True,exist_ok=True)
    evidence={
        "files_planned":len(plan["planned_files"]),
        "operations":plan["operations"],
        "checkpoint":str(checkpoint),
        "created_at":datetime.now(timezone.utc).isoformat()
    }
    checkpoint.write_text(json.dumps({"plan":plan,"evidence":evidence},indent=2),encoding="utf-8")
    return {"status":"checkpointed","evidence":evidence}

# Governed authenticated builder pipeline.
@router.post("/crud")
def create(payload:Create,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    if not project_store.get(payload.project_id,uid):
        raise HTTPException(404,"Project not found")
    spec=normalize_spec(payload.entity,payload.fields,payload.roles or ["admin","user"])
    manifest=generate_manifest(spec)
    plan=[{"step":"GENERATE_FRONTEND","status":"PLANNED"},
          {"step":"GENERATE_BACKEND","status":"PLANNED"},
          {"step":"GENERATE_DATABASE","status":"PLANNED"},
          {"step":"TEST","status":"PLANNED"}]
    job=build_pipeline.create(payload.project_id,manifest,plan,payload.sensitive)
    if payload.sensitive:
        approval=approval_store.request(job["id"],"execute builder job",
                                         "Sensitive builder execution","HIGH",uid)
        build_pipeline.transition(job["id"],"APPROVAL_REQUIRED")
        audit_log.append("BUILDER_APPROVAL_REQUIRED",uid,{"job":job,"approval":approval})
        return {"job":build_pipeline.get(job["id"]),"approval":approval}
    return {"job":job,"status":"PLANNED"}

@router.post("/{job_id}/execute")
def execute(job_id:str,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    job=build_pipeline.get(job_id)
    if not job: raise HTTPException(404,"Build job not found")
    if job["status"]=="APPROVAL_REQUIRED": raise HTTPException(403,"Approval required before execution")
    if job["status"]!="PLANNED": raise HTTPException(409,"Build job is not executable")
    build_pipeline.transition(job_id,"EXECUTING")
    try:
        out=build_pipeline.execute(job_id,uid)
    except ValueError as e:
        build_pipeline.transition(job_id,"FAILED")
        raise HTTPException(400,str(e))
    audit_log.append("BUILDER_VERIFIED",uid,out)
    return out
