from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4
import copy
@dataclass
class Checkpoint:
    id:str; project_id:str; owner_id:str; label:str; state:dict; created_at:str
class CheckpointStore:
    def __init__(self): self._items={}; self._lock=Lock()
    def create(self,project_id,label,state,owner_id=""):
        c=Checkpoint(str(uuid4()),project_id,owner_id,label,copy.deepcopy(state),datetime.now(timezone.utc).isoformat())
        with self._lock:self._items[c.id]=c
        return asdict(c)
    def list(self,project_id,owner_id=""):
        with self._lock:return [asdict(c) for c in self._items.values() if c.project_id==project_id and (not owner_id or c.owner_id==owner_id)]
    def get(self,cid,owner_id=""):
        with self._lock:
            c=self._items.get(cid)
            if not c or (owner_id and c.owner_id!=owner_id):return None
            return copy.deepcopy(asdict(c))
checkpoint_store=CheckpointStore()
