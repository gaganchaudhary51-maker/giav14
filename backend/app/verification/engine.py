from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

STATES={"REQUESTED","PLANNED","APPROVAL_REQUIRED","APPROVED","EXECUTING",
        "EXECUTED","VERIFYING","VERIFIED","FAILED","DIAGNOSING","REPAIRING",
        "RETESTING","ROLLED_BACK"}

TRANSITIONS={
 "REQUESTED":{"PLANNED","FAILED"},
 "PLANNED":{"APPROVAL_REQUIRED","APPROVED","EXECUTING","FAILED"},
 "APPROVAL_REQUIRED":{"APPROVED","FAILED"},
 "APPROVED":{"EXECUTING","FAILED"},
 "EXECUTING":{"EXECUTED","FAILED"},
 "EXECUTED":{"VERIFYING","FAILED"},
 "VERIFYING":{"VERIFIED","DIAGNOSING","FAILED"},
 "DIAGNOSING":{"REPAIRING","FAILED"},
 "REPAIRING":{"RETESTING","FAILED"},
 "RETESTING":{"VERIFIED","DIAGNOSING","FAILED"},
 "VERIFIED":set(),
 "FAILED":{"DIAGNOSING","ROLLED_BACK"},
 "ROLLED_BACK":set(),
}

@dataclass
class Verification:
    id:str; task_id:str; state:str; evidence:list; updated_at:str

class VerificationEngine:
    def __init__(self):
        self._items={}; self._lock=Lock()

    def create(self,task_id):
        v=Verification(str(uuid4()),task_id,"REQUESTED",[],datetime.now(timezone.utc).isoformat())
        with self._lock: self._items[v.id]=v
        return asdict(v)

    def transition(self,verification_id,state,evidence=None):
        with self._lock:
            v=self._items.get(verification_id)
            if not v: return None
            if state not in STATES or state not in TRANSITIONS[v.state]:
                raise ValueError(f"Invalid transition {v.state} -> {state}")
            v.state=state
            if evidence: v.evidence.extend(evidence)
            v.updated_at=datetime.now(timezone.utc).isoformat()
            return asdict(v)

    def get(self,verification_id):
        with self._lock:
            v=self._items.get(verification_id)
            return asdict(v) if v else None

verification_engine=VerificationEngine()
