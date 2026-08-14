from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

ALLOWED_ACTIONS={"READ_FILE","LIST_FILES","RUN_TESTS","RUN_BUILD","LINT","FORMAT"}
BLOCKED_ACTIONS={"DELETE","DROP_DATABASE","SECRET_READ","PRODUCTION_DEPLOY","UNRESTRICTED_SHELL"}

@dataclass
class Execution:
    id:str; task_id:str; action:str; status:str; output:str; created_at:str

class ExecutionEngine:
    def __init__(self):
        self._items={}; self._lock=Lock()

    def execute(self,task_id,action,output=""):
        if action in BLOCKED_ACTIONS:
            raise PermissionError("Action requires dedicated approval workflow")
        if action not in ALLOWED_ACTIONS:
            raise ValueError("Action is not allowlisted")
        e=Execution(str(uuid4()),task_id,action,"EXECUTED",output,
                    datetime.now(timezone.utc).isoformat())
        with self._lock: self._items[e.id]=e
        return asdict(e)

execution_engine=ExecutionEngine()
