"""Durable task repository and guarded lifecycle state machine."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
import json

from app.db.sqlite import connect

TASK_TRANSITIONS = {
    "PLANNED": {"APPROVAL_REQUIRED", "EXECUTING", "FAILED"},
    "APPROVAL_REQUIRED": {"APPROVED", "FAILED"},
    "APPROVED": {"EXECUTING", "FAILED"},
    "EXECUTING": {"EXECUTED", "VERIFYING", "FAILED"},
    "EXECUTED": {"VERIFYING", "VERIFIED", "FAILED"},
    "VERIFYING": {"VERIFIED", "FAILED"},
    "VERIFIED": {"ROLLED_BACK"},
    "FAILED": {"APPROVAL_REQUIRED", "EXECUTING", "ROLLED_BACK"},
    "ROLLED_BACK": set(),
}

@dataclass
class Task:
    id: str
    text: str
    status: str
    model_tier: str
    team: list[str]
    approval_required: bool
    created_at: str
    owner_id: str | None = None

class TaskStore:
    def __init__(self):
        self._lock = RLock()
        with connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    owner_id TEXT,
                    data_json TEXT NOT NULL
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner_id)")

    def create(self, text, model_tier, team, approval_required, owner_id=None):
        with self._lock:
            status = "APPROVAL_REQUIRED" if approval_required else "PLANNED"
            task = Task(str(uuid4()), text, status, model_tier, team, approval_required,
                        datetime.now(timezone.utc).isoformat(), owner_id)
            data = asdict(task)
            with connect() as db:
                db.execute("INSERT INTO tasks(id,owner_id,data_json) VALUES(?,?,?)",
                           (task.id, owner_id, json.dumps(data)))
            return data

    def get(self, task_id, owner_id=None):
        with self._lock, connect() as db:
            row = db.execute("SELECT owner_id,data_json FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not row or (owner_id is not None and row["owner_id"] != owner_id):
                return None
            return json.loads(row["data_json"])

    def list_for_owner(self, owner_id):
        with self._lock, connect() as db:
            rows = db.execute("SELECT data_json FROM tasks WHERE owner_id=? ORDER BY rowid DESC",
                              (owner_id,)).fetchall()
            return [json.loads(row["data_json"]) for row in rows]

    def update(self, task_id, status, owner_id=None):
        with self._lock, connect() as db:
            row = db.execute("SELECT owner_id,data_json FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not row or (owner_id is not None and row["owner_id"] != owner_id):
                return None
            data = json.loads(row["data_json"])
            if status == data["status"]:
                return data
            allowed = TASK_TRANSITIONS.get(data["status"], set())
            if status not in allowed:
                raise ValueError(f"Invalid task transition: {data['status']} -> {status}")
            if status == "APPROVED":
                data["approval_required"] = False
            data["status"] = status
            db.execute("UPDATE tasks SET data_json=? WHERE id=?", (json.dumps(data), task_id))
            return data

    def clear(self):
        with self._lock, connect() as db:
            db.execute("DELETE FROM tasks")

task_store = TaskStore()
