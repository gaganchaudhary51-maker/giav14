"""Durable approval records with single-resolution semantics."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
import json
from app.db.sqlite import connect

@dataclass
class Approval:
    id: str
    task_id: str
    action: str
    reason: str
    risk: str
    status: str
    requested_by: str
    approved_by: str | None
    created_at: str
    resolved_at: str | None

class ApprovalStore:
    def __init__(self):
        self._lock = RLock()
        with connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY, requested_by TEXT NOT NULL, data_json TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_approvals_owner ON approvals(requested_by)")

    def request(self, task_id, action, reason, risk, requested_by):
        with self._lock:
            a = Approval(str(uuid4()), task_id, action, reason, risk, "PENDING",
                         requested_by, None, datetime.now(timezone.utc).isoformat(), None)
            data = asdict(a)
            with connect() as db:
                db.execute("INSERT INTO approvals(id,requested_by,data_json) VALUES(?,?,?)",
                           (a.id, requested_by, json.dumps(data)))
            return data

    def get(self, approval_id, owner_id=None):
        with self._lock, connect() as db:
            row = db.execute("SELECT requested_by,data_json FROM approvals WHERE id=?",
                             (approval_id,)).fetchone()
            if not row or (owner_id is not None and row["requested_by"] != owner_id):
                return None
            return json.loads(row["data_json"])

    def resolve(self, approval_id, approved_by, approve):
        with self._lock, connect() as db:
            row = db.execute("SELECT data_json FROM approvals WHERE id=?", (approval_id,)).fetchone()
            if not row:
                return None
            data = json.loads(row["data_json"])
            if data["status"] != "PENDING":
                return None
            data["status"] = "APPROVED" if approve else "REJECTED"
            data["approved_by"] = approved_by
            data["resolved_at"] = datetime.now(timezone.utc).isoformat()
            db.execute("UPDATE approvals SET data_json=? WHERE id=?", (json.dumps(data), approval_id))
            return data

    def clear(self):
        with self._lock, connect() as db:
            db.execute("DELETE FROM approvals")

approval_store = ApprovalStore()
