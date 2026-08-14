from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

@dataclass
class Message:
    id:str
    sender:str
    recipient:str
    message_type:str
    content:str
    task_id:str|None
    created_at:str
    status:str

class CollaborationBus:
    def __init__(self):
        self._messages=[]
        self._lock=Lock()

    def send(self,sender,recipient,message_type,content,task_id=None):
        m=Message(str(uuid4()),sender,recipient,message_type,content,task_id,
                  datetime.now(timezone.utc).isoformat(),"DELIVERED")
        with self._lock: self._messages.append(m)
        return asdict(m)

    def inbox(self,recipient,limit=50):
        with self._lock:
            items=[asdict(m) for m in self._messages if m.recipient in (recipient,"*")]
        return items[-min(max(limit,1),100):]

    def conversation(self,participants,limit=100):
        p=set(participants)
        with self._lock:
            items=[asdict(m) for m in self._messages if m.sender in p and m.recipient in p]
        return items[-min(max(limit,1),200):]

collaboration_bus=CollaborationBus()
