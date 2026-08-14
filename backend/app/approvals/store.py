from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

@dataclass
class Approval:
    id:str
    task_id:str
    action:str
    reason:str
    risk:str
    status:str
    requested_by:str
    approved_by:str|None
    created_at:str
    resolved_at:str|None

class ApprovalStore:
    def __init__(self):
        self._items={}
        self._lock=Lock()

    def request(self,task_id,action,reason,risk,requested_by):
        with self._lock:
            a=Approval(str(uuid4()),task_id,action,reason,risk,"PENDING",
                       requested_by,None,datetime.now(timezone.utc).isoformat(),None)
            self._items[a.id]=a
            return asdict(a)

    def get(self,approval_id):
        with self._lock:
            a=self._items.get(approval_id)
            return asdict(a) if a else None

    def resolve(self,approval_id,approved_by,approve):
        with self._lock:
            a=self._items.get(approval_id)
            if not a: return None
            if a.status!="PENDING": return asdict(a)
            a.status="APPROVED" if approve else "REJECTED"
            a.approved_by=approved_by
            a.resolved_at=datetime.now(timezone.utc).isoformat()
            return asdict(a)

approval_store=ApprovalStore()
