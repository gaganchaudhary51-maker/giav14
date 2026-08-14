from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.collaboration.protocol import send
from app.collaboration.bus import collaboration_bus

router=APIRouter(prefix="/collaboration",tags=["collaboration"])

class MessageRequest(BaseModel):
    sender:str=Field(min_length=1,max_length=100)
    recipient:str=Field(min_length=1,max_length=100)
    message_type:str=Field(default="TASK",min_length=1,max_length=50)
    content:str=Field(min_length=1,max_length=10000)
    task_id:str|None=None

def auth(a):
    if not a or not a.startswith("Bearer ") or not verify_token(a[7:]):
        raise HTTPException(401,"Authentication required")

@router.post("/send")
def send_message(payload:MessageRequest,authorization:str|None=Header(default=None)):
    auth(authorization)
    try: return send(payload.sender,payload.recipient,payload.content,payload.task_id,payload.message_type)
    except ValueError as e: raise HTTPException(400,str(e))

@router.get("/inbox/{recipient}")
def inbox(recipient:str,authorization:str|None=Header(default=None)):
    auth(authorization)
    return {"items":collaboration_bus.inbox(recipient)}

@router.get("/conversation")
def conversation(participants:str,authorization:str|None=Header(default=None)):
    auth(authorization)
    return {"items":collaboration_bus.conversation([x.strip() for x in participants.split(",") if x.strip()])}
