from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4

@dataclass
class Event:
    id:str; event_type:str; payload:dict; created_at:str

class EventStore:
    def __init__(self): self.items=[]; self.lock=Lock()
    def publish(self,event_type,payload):
        e=Event(str(uuid4()),event_type,payload,datetime.now(timezone.utc).isoformat())
        with self.lock: self.items.append(e)
        return asdict(e)
    def recent(self,limit=100):
        with self.lock: return [asdict(e) for e in self.items[-min(max(limit,1),200):]]
event_store=EventStore()
