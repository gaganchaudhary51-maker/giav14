from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4
@dataclass
class Lesson:
    id:str;agent:str;domain:str;lesson:str;evidence:str;tests_passed:bool;status:str;state:str;created_at:str
class LearningEngine:
    def __init__(self):self._items={};self._lock=Lock()
    def add(self,agent,domain,lesson,evidence,tests_passed):
        ok=bool(tests_passed);state="VALIDATED" if ok else "REJECTED";status="PROMOTED" if ok else "QUARANTINED"
        x=Lesson(str(uuid4()),agent,domain,lesson,evidence,ok,status,state,datetime.now(timezone.utc).isoformat())
        with self._lock:self._items[x.id]=x
        return asdict(x)
    def recent(self,agent=None,domain=None):
        with self._lock:xs=list(self._items.values())
        if agent:xs=[x for x in xs if x.agent==agent]
        if domain:xs=[x for x in xs if x.domain==domain]
        return [asdict(x) for x in xs[-100:][::-1]]
learning_engine=LearningEngine()
