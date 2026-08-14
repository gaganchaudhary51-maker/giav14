from threading import Lock
from app.tasks.store import task_store
from app.events.bus import event_bus
from app.commander.router import dispatch
from app.models.router import route_task,escalate
class OrchestrationRunner:
    def __init__(self): self._lock=Lock(); self._failures={}
    def start(self,task_id):
        with self._lock:
            task=task_store.get(task_id)
            if not task: raise KeyError("Task not found")
            if task["approval_required"]:
                task_store.update(task_id,"APPROVAL_REQUIRED")
                event_bus.publish("APPROVAL_REQUIRED",{"task_id":task_id})
                return task_store.get(task_id)
            task_store.update(task_id,"EXECUTING")
            event_bus.publish("TASK_EXECUTING",{"task_id":task_id,"team":task["team"]})
            return task_store.get(task_id)
    def complete(self,task_id,verified=False,evidence=None):
        with self._lock:
            if not task_store.get(task_id): raise KeyError("Task not found")
            task_store.update(task_id,"EXECUTED");event_bus.publish("TASK_EXECUTED",{"task_id":task_id})
            if verified and evidence:
                task_store.update(task_id,"VERIFYING");event_bus.publish("TASK_VERIFYING",{"task_id":task_id})
                task_store.update(task_id,"VERIFIED");event_bus.publish("TASK_VERIFIED",{"task_id":task_id,"evidence":evidence})
            return task_store.get(task_id)
    def fail_and_escalate(self,task_id,risk="LOW"):
        with self._lock:
            task=task_store.get(task_id)
            if not task:raise KeyError("Task not found")
            n=self._failures.get(task_id,0)+1;self._failures[task_id]=n
            decision=escalate(route_task(task["text"],risk,n),n,risk)
            task_store.update(task_id,"FAILED")
            event_bus.publish("TASK_FAILED",{"task_id":task_id,"failure_count":n,"next_model":decision.tier})
            return {"task":task_store.get(task_id),"decision":decision.__dict__}
runner=OrchestrationRunner()
