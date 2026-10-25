from __future__ import annotations

from datetime import datetime, timezone
import json
from threading import RLock
from uuid import uuid4

from app.db.sqlite import connect


class ConversationStore:
    """Durable conversation threads isolated by signed-in owner and project."""

    def __init__(self):
        self._lock = RLock()
        with connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS conversation_threads (
                    id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    messages_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_conversation_owner_project ON conversation_threads(owner_id, project_id, updated_at)")

    @staticmethod
    def _decode(row):
        if not row:
            return None
        return {
            "id": row["id"],
            "owner_id": row["owner_id"],
            "project_id": row["project_id"],
            "title": row["title"],
            "messages": json.loads(row["messages_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def create(self, owner_id: str, project_id: str, title: str = "New chat"):
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": str(uuid4()), "owner_id": owner_id, "project_id": project_id,
            "title": title[:120] or "New chat", "messages": [],
            "created_at": now, "updated_at": now,
        }
        with self._lock, connect() as db:
            db.execute(
                "INSERT INTO conversation_threads(id,owner_id,project_id,title,messages_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (item["id"], owner_id, project_id, item["title"], "[]", now, now),
            )
        return item

    def get(self, thread_id: str, owner_id: str):
        with connect() as db:
            row = db.execute(
                "SELECT * FROM conversation_threads WHERE id=? AND owner_id=?",
                (thread_id, owner_id),
            ).fetchone()
        return self._decode(row)

    def list_for_owner(self, owner_id: str, project_id: str | None = None, limit: int = 40):
        with connect() as db:
            if project_id:
                rows = db.execute(
                    "SELECT * FROM conversation_threads WHERE owner_id=? AND project_id=? ORDER BY updated_at DESC LIMIT ?",
                    (owner_id, project_id, max(1, min(limit, 100))),
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM conversation_threads WHERE owner_id=? ORDER BY updated_at DESC LIMIT ?",
                    (owner_id, max(1, min(limit, 100))),
                ).fetchall()
        return [self._decode(row) for row in rows]

    def append_turn(self, thread_id: str, owner_id: str, user_text: str, assistant_text: str):
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, connect() as db:
            row = db.execute(
                "SELECT * FROM conversation_threads WHERE id=? AND owner_id=?",
                (thread_id, owner_id),
            ).fetchone()
            if not row:
                return None
            messages = json.loads(row["messages_json"])
            messages.extend([
                {"role": "user", "content": user_text, "created_at": now},
                {"role": "assistant", "content": assistant_text, "created_at": now},
            ])
            title = row["title"]
            if title == "New chat":
                title = " ".join(user_text.split())[:80] or "New chat"
            db.execute(
                "UPDATE conversation_threads SET title=?,messages_json=?,updated_at=? WHERE id=? AND owner_id=?",
                (title, json.dumps(messages, ensure_ascii=False), now, thread_id, owner_id),
            )
            updated = db.execute(
                "SELECT * FROM conversation_threads WHERE id=? AND owner_id=?",
                (thread_id, owner_id),
            ).fetchone()
        return self._decode(updated)

    def clear(self):
        with self._lock, connect() as db:
            db.execute("DELETE FROM conversation_threads")


conversation_store = ConversationStore()
