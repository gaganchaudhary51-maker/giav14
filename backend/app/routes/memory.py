from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.memory.store import memory_store
from app.rag.retriever import retrieve

router=APIRouter(prefix="/memory",tags=["memory"])

class MemoryRequest(BaseModel):
    project_id:str=Field(min_length=1,max_length=200)
    kind:str=Field(default="note",min_length=1,max_length=50)
    text:str=Field(min_length=1,max_length=10000)

class SearchRequest(BaseModel):
    project_id:str=Field(min_length=1,max_length=200)
    query:str=Field(min_length=1,max_length=1000)
    limit:int=Field(default=5,ge=1,le=20)

def user_id(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401,"Authentication required")
    uid=verify_token(authorization[7:])
    if not uid: raise HTTPException(401,"Invalid or expired token")
    return uid

@router.post("",status_code=201)
def add(payload:MemoryRequest,authorization:str|None=Header(default=None)):
    return memory_store.add(user_id(authorization),payload.project_id,payload.kind,payload.text)

@router.post("/search")
def search(payload:SearchRequest,authorization:str|None=Header(default=None)):
    result=retrieve(user_id(authorization),payload.project_id,payload.query,payload.limit)
    return {"items":result["memories"],"documents":result["documents"]}
