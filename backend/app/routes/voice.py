from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.voice.session import voice_sessions
from app.voice.providers import provider_status,route
from app.audit.log import audit_log
router=APIRouter(prefix="/voice",tags=["voice"])
class Start(BaseModel):
    project_id:str|None=None;provider:str="browser";mode:str="hands-free"
class State(BaseModel):
    state:str=Field(pattern="^(IDLE|LISTENING|THINKING|PLANNING|EXECUTING|WAITING_FOR_APPROVAL|SPEAKING|VERIFYING|ERROR)$")
class Transcript(BaseModel):
    text:str=Field(min_length=1,max_length=10000)
class RouteRequest(BaseModel):
    kind:str=Field(pattern="^(stt|tts)$")
    preferred:str|None=None
def auth(a):
    if not a or not a.startswith("Bearer "):raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid:raise HTTPException(401,"Invalid or expired token")
    return uid
@router.get("/providers")
def providers(authorization:str|None=Header(default=None)):
    auth(authorization);return provider_status()
@router.post("/route")
def provider_route(p:RouteRequest,authorization:str|None=Header(default=None)):
    auth(authorization);return route(p.kind,p.preferred)
@router.post("/sessions",status_code=201)
def start(p:Start,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    allowed={"browser","browser-web-speech","whisper-local","piper-local","free-stt-provider","free-tts-provider","cheap-stt-provider","cheap-tts-provider"}
    if p.provider not in allowed: raise HTTPException(400,"Unsupported voice provider")
    x=voice_sessions.create(uid,p.project_id,p.provider,p.mode)
    audit_log.append("VOICE_SESSION_CREATED",uid,x);return x
@router.get("/sessions/{session_id}")
def get(session_id:str,authorization:str|None=Header(default=None)):
    uid=auth(authorization);x=voice_sessions.get(session_id,uid)
    if not x:raise HTTPException(404,"Voice session not found")
    return x
@router.post("/sessions/{session_id}/state")
def state(session_id:str,p:State,authorization:str|None=Header(default=None)):
    uid=auth(authorization);x=voice_sessions.transition(session_id,uid,p.state)
    if not x:raise HTTPException(404,"Voice session not found")
    audit_log.append("VOICE_STATE_CHANGED",uid,{"session_id":session_id,"state":p.state});return x
@router.post("/sessions/{session_id}/transcript")
def transcript(session_id:str,p:Transcript,authorization:str|None=Header(default=None)):
    uid=auth(authorization);x=voice_sessions.transition(session_id,uid,"THINKING",p.text)
    if not x:raise HTTPException(404,"Voice session not found")
    audit_log.append("VOICE_TRANSCRIPT_RECEIVED",uid,{"session_id":session_id,"chars":len(p.text)});return x
