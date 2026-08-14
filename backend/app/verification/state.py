from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4

_ALLOWED={
"REQUESTED":{"PLANNED","FAILED"},
"PLANNED":{"APPROVAL_REQUIRED","APPROVED","EXECUTING","FAILED"},
"APPROVAL_REQUIRED":{"APPROVED","FAILED"},
"APPROVED":{"EXECUTING","FAILED"},
"EXECUTING":{"EXECUTED","FAILED"},
"EXECUTED":{"VERIFYING","FAILED"},
"VERIFYING":{"VERIFIED","FAILED"},
"VERIFIED":{"RELEASED","FAILED"},
"RELEASED":set(),
"FAILED":{"ROLLED_BACK"},
"ROLLED_BACK":set()
}
@dataclass
class VerificationRecord:
    id:str; task_id:str; state:str; evidence:list; created_at:str; updated_at:str
class VerificationStore:
    def __init__(self): self._items={}; self._lock=Lock()
    def create(self,task_id):
        now=datetime.now(timezone.utc).isoformat()
        v=VerificationRecord(str(uuid4()),task_id,"REQUESTED",[],now,now)
        with self._lock:self._items[v.id]=v
        return asdict(v)
    def transition(self,vid,state,evidence=None):
        with self._lock:
            v=self._items.get(vid)
            if not v:return None
            if state not in _ALLOWED.get(v.state,set()):
                raise ValueError(f"Invalid verification transition {v.state}->{state}")
            if state in {"VERIFIED","RELEASED"} and not evidence and not v.evidence:
                raise ValueError("Evidence required before VERIFIED/RELEASED")
            if evidence:v.evidence.extend(evidence)
            v.state=state;v.updated_at=datetime.now(timezone.utc).isoformat()
            return asdict(v)
    def get(self,vid):
        with self._lock:
            v=self._items.get(vid);return asdict(v) if v else None
verification_store=VerificationStore()
