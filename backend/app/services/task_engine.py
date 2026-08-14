from uuid import uuid4
from .planner import create_plan
from ..core.models import Task, now_iso

class TaskEngine:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def create(self, project_id: str, request: str) -> Task:
        plan = create_plan(request)
        task = Task(id=str(uuid4()), project_id=project_id, request=request,
                    status="APPROVAL_REQUIRED" if plan["approval_required"] else "PLANNED",
                    plan=plan["steps"], agents=plan["agents"])
        self.tasks[task.id] = task
        return task

    def approve(self, task_id: str) -> Task:
        task = self.tasks[task_id]
        task.status = "APPROVED"
        task.updated_at = now_iso()
        return task

    def list(self, project_id: str) -> list[Task]:
        return [t for t in self.tasks.values() if t.project_id == project_id]
