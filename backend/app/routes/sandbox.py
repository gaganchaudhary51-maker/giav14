from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.sandbox.runner import run, SandboxError
import os

router=APIRouter(prefix="/sandbox",tags=["sandbox"])

class RunRequest(BaseModel):
    command:list[str]=Field(min_length=1,max_length=8)
    cwd:str=Field(min_length=1,max_length=500)

@router.post("/run")
def sandbox_run(payload:RunRequest, authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")
    try:
        return {"status":"executed","result":run(payload.command,payload.cwd,workspace_root=os.getenv("GIA_SANDBOX_ROOT"))}
    except SandboxError as exc:
        raise HTTPException(403,str(exc))
