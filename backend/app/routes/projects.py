from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.projects.store import project_store
from app.builder.crud import normalize_spec,generate_manifest
router=APIRouter(prefix="/projects",tags=["projects"])
class Create(BaseModel):
    name:str=Field(min_length=1,max_length=200); description:str=Field(default="",max_length=5000)
    stack:dict={"frontend":"react-typescript","backend":"fastapi","database":"mongodb"}
class Crud(BaseModel):
    entity:str=Field(min_length=1,max_length=100); fields:list[str]=Field(default_factory=list,max_length=100); roles:list[str]=Field(default_factory=lambda:["admin","user"],max_length=20)
def auth(a):
    if not a or not a.startswith("Bearer "): raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid: raise HTTPException(401,"Invalid or expired token")
    return uid
@router.post("",status_code=201)
def create(p:Create,authorization:str|None=Header(default=None)):
    return project_store.create(auth(authorization),p.name,p.description,p.stack)
@router.get("")
def listing(authorization:str|None=Header(default=None)):
    return {"projects":project_store.list(auth(authorization))}
@router.get("/{project_id}")
def get(project_id:str,authorization:str|None=Header(default=None)):
    p=project_store.get(project_id,auth(authorization))
    if not p: raise HTTPException(404,"Project not found")
    return p
@router.post("/{project_id}/crud-spec")
def crud(project_id:str,p:Crud,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    if not project_store.get(project_id,uid): raise HTTPException(404,"Project not found")
    return generate_manifest(normalize_spec(p.entity,p.fields,p.roles))
