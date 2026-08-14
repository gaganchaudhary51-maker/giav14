from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.memory.global_store import global_knowledge

router=APIRouter(prefix="/memory/global",tags=["global-memory"])

class SearchRequest(BaseModel):
    query:str=Field(min_length=1,max_length=1000)
    limit:int=Field(default=10,ge=1,le=20)

@router.post("/search")
def search(payload:SearchRequest,authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401,"Authentication required")
    return {"scope":"global-technical","items":global_knowledge.search(payload.query,payload.limit)}
