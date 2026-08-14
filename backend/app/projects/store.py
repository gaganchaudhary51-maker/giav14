from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4
import copy

@dataclass
class Project:
    id:str; owner_id:str; name:str; description:str; stack:dict; status:str; files:dict; created_at:str; updated_at:str

class ProjectStore:
    def __init__(self): self._items={}; self._lock=Lock()
    def create(self,owner_id,name,description,stack):
        now=datetime.now(timezone.utc).isoformat()
        p=Project(str(uuid4()),owner_id,name,description,copy.deepcopy(stack),"ACTIVE",{},now,now)
        with self._lock:self._items[p.id]=p
        return asdict(p)
    def get(self,pid,owner_id):
        with self._lock:
            p=self._items.get(pid)
            if not p or p.owner_id!=owner_id:return None
            return asdict(p)
    def list(self,owner_id):
        with self._lock:return [asdict(p) for p in self._items.values() if p.owner_id==owner_id]
    def replace_files(self,pid,owner_id,files):
        with self._lock:
            p=self._items.get(pid)
            if not p or p.owner_id!=owner_id:return None
            p.files=copy.deepcopy(files);p.updated_at=datetime.now(timezone.utc).isoformat()
            return asdict(p)

    def write_files(self,pid,owner_id,changes):
        with self._lock:
            p=self._items.get(pid)
            if not p or p.owner_id!=owner_id:return None
            p.files.update(copy.deepcopy(changes)); p.updated_at=datetime.now(timezone.utc).isoformat()
            return asdict(p)
project_store=ProjectStore()
