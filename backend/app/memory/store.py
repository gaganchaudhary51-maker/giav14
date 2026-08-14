from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

@dataclass
class Memory:
    id:str
    user_id:str
    project_id:str
    kind:str
    text:str
    created_at:str

class MemoryStore:
    def __init__(self):
        self._items={}
        self._lock=Lock()

    def add(self,user_id,project_id,kind,text):
        with self._lock:
            m=Memory(str(uuid4()),user_id,project_id,kind,text,
                     datetime.now(timezone.utc).isoformat())
            self._items[m.id]=m
            return asdict(m)

    def search(self,user_id,project_id,query,limit=10):
        terms=[x for x in query.lower().split() if x]
        with self._lock:
            items=[m for m in self._items.values()
                   if m.user_id==user_id and m.project_id==project_id]
        scored=[]
        for m in items:
            score=sum(1 for t in terms if t in m.text.lower())
            if score: scored.append((score,m))
        scored.sort(key=lambda x:(-x[0],x[1].created_at))
        return [asdict(m) for _,m in scored[:limit]]

memory_store=MemoryStore()
