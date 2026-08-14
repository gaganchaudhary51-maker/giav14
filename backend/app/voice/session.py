from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4
@dataclass
class VoiceSession:
    id:str; user_id:str; project_id:str|None; provider:str; mode:str; state:str; transcript:list; created_at:str
class VoiceSessionStore:
    def __init__(self):self._items={};self._lock=Lock()
    def create(self,user_id,project_id=None,provider="browser",mode="hands-free"):
        x=VoiceSession(str(uuid4()),user_id,project_id,provider,mode,"IDLE",[],datetime.now(timezone.utc).isoformat())
        with self._lock:self._items[x.id]=x
        return asdict(x)
    def get(self,sid,user_id):
        with self._lock:
            x=self._items.get(sid)
            return asdict(x) if x and x.user_id==user_id else None
    def transition(self,sid,user_id,state,text=None):
        with self._lock:
            x=self._items.get(sid)
            if not x or x.user_id!=user_id:return None
            x.state=state
            if text is not None:x.transcript.append({"role":"user","text":text,"at":datetime.now(timezone.utc).isoformat()})
            return asdict(x)
voice_sessions=VoiceSessionStore()
