from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.events.store import event_store

router=APIRouter(prefix="/events",tags=["events"])
class Publish(BaseModel):
    event_type:str=Field(min_length=1,max_length=100)
    payload:dict={}
def auth(a):
    if not a or not a.startswith("Bearer ") or not verify_token(a[7:]): raise HTTPException(401,"Authentication required")
@router.post("/publish")
def publish(payload:Publish,authorization:str|None=Header(default=None)):
    auth(authorization); return event_store.publish(payload.event_type,payload.payload)
@router.get("/recent")
def recent(limit:int=100,authorization:str|None=Header(default=None)):
    auth(authorization)
    raw=event_store.recent(limit)
    items=[]
    for e in raw:
        e=dict(e)
        e["type"]=e.get("event_type",e.get("type"))
        items.append(e)
    return {"events":items,"items":items}
