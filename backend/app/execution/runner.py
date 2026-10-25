"""Durable allowlisted execution records; this module records tool results, not arbitrary shell runs."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
import json
from app.db.sqlite import connect

ALLOWED_ACTIONS={"READ_FILE","LIST_FILES","RUN_TESTS","RUN_BUILD","LINT","FORMAT"}
BLOCKED_ACTIONS={"DELETE","DROP_DATABASE","SECRET_READ","PRODUCTION_DEPLOY","UNRESTRICTED_SHELL"}

@dataclass
class Execution:
    id: str
    task_id: str
    action: str
    status: str
    output: str
    created_at: str
    owner_id: str | None = None

class ExecutionEngine:
    def __init__(self):
        self._lock = RLock()
        with connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY, task_id TEXT NOT NULL, owner_id TEXT, data_json TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_executions_task ON executions(task_id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_executions_owner ON executions(owner_id)")

    def execute(self, task_id, action, output="", owner_id=None):
        action = action.upper()
        if action in BLOCKED_ACTIONS:
            raise PermissionError("Action requires dedicated approval workflow")
        if action not in ALLOWED_ACTIONS:
            raise ValueError("Action is not allowlisted")
        with self._lock:
            e = Execution(str(uuid4()), task_id, action, "EXECUTED", output,
                          datetime.now(timezone.utc).isoformat(), owner_id)
            data = asdict(e)
            with connect() as db:
                db.execute("INSERT INTO executions(id,task_id,owner_id,data_json) VALUES(?,?,?,?)",
                           (e.id, task_id, owner_id, json.dumps(data)))
            return data

    def list_for_task(self, task_id, owner_id=None):
        with self._lock, connect() as db:
            rows = db.execute("SELECT owner_id,data_json FROM executions WHERE task_id=? ORDER BY rowid",
                              (task_id,)).fetchall()
            return [json.loads(r["data_json"]) for r in rows
                    if owner_id is None or r["owner_id"] == owner_id]

    def clear(self):
        with self._lock, connect() as db:
            db.execute("DELETE FROM executions")

execution_engine = ExecutionEngine()
