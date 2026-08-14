from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.rag.store import rag_store
from app.audit.log import audit_log
router=APIRouter(prefix="/rag",tags=["rag"])
class IndexRequest(BaseModel):
    project_id:str=Field(min_length=1,max_length=200); source:str=Field(min_length=1,max_length=500); text:str=Field(min_length=1,max_length=200000)
class SearchRequest(BaseModel):
    project_id:str=Field(min_length=1,max_length=200); query:str=Field(min_length=1,max_length=2000); limit:int=Field(default=5,ge=1,le=20)
def auth(a):
    if not a or not a.startswith("Bearer "):raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid:raise HTTPException(401,"Invalid or expired token")
    return uid
@router.post("/index",status_code=201)
def index(p:IndexRequest,authorization:str|None=Header(default=None)):
    uid=auth(authorization); chunks=rag_store.index(uid,p.project_id,p.source,p.text)
    audit_log.append("RAG_INDEXED",uid,{"project_id":p.project_id,"source":p.source,"chunks":len(chunks)})
    return {"indexed":len(chunks),"source":p.source,"project_id":p.project_id}
@router.post("/search")
def search(p:SearchRequest,authorization:str|None=Header(default=None)):
    uid=auth(authorization); return {"items":rag_store.search(uid,p.project_id,p.query,p.limit)}
@router.delete("/{project_id}")
def clear(project_id:str,authorization:str|None=Header(default=None)):
    uid=auth(authorization); return {"deleted":rag_store.clear_project(uid,project_id)}
