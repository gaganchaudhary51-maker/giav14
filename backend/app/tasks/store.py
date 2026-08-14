from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

@dataclass
class Task:
    id: str
    text: str
    status: str
    model_tier: str
    team: list[str]
    approval_required: bool
    created_at: str

class TaskStore:
    def __init__(self):
        self._items={}
        self._lock=Lock()

    def create(self, text, model_tier, team, approval_required):
        with self._lock:
            task=Task(str(uuid4()),text,"PLANNED",model_tier,team,approval_required,
                      datetime.now(timezone.utc).isoformat())
            self._items[task.id]=task
            return asdict(task)

    def get(self, task_id):
        with self._lock:
            task=self._items.get(task_id)
            return asdict(task) if task else None

    def update(self, task_id, status):
        with self._lock:
            task=self._items.get(task_id)
            if not task: return None
            task.status=status
            return asdict(task)

task_store=TaskStore()
