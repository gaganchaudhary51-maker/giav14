from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4
import json
import re
import math

from app.db.sqlite import connect
from app.memory import hrr

_HRR_DIM = hrr.DIM


@dataclass
class Memory:
    id: str
    user_id: str
    project_id: str
    kind: str
    text: str
    created_at: str
    tags: list[str]
    importance: int
    summary: str


class MemoryStore:
    """Durable, tenant/project-scoped memory with tags and importance-aware recall."""

    def __init__(self):
        self._items: dict[str, Memory] = {}
        self._vectors: dict[str, bytes] = {}
        self._lock = Lock()
        with connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    importance INTEGER NOT NULL DEFAULT 1,
                    summary TEXT NOT NULL DEFAULT '',
                    hrr_vector BLOB
                )
            """)
            columns = {row["name"] for row in db.execute("PRAGMA table_info(memories)").fetchall()}
            if "tags_json" not in columns:
                db.execute("ALTER TABLE memories ADD COLUMN tags_json TEXT NOT NULL DEFAULT '[]'")
            if "importance" not in columns:
                db.execute("ALTER TABLE memories ADD COLUMN importance INTEGER NOT NULL DEFAULT 1")
            if "summary" not in columns:
                db.execute("ALTER TABLE memories ADD COLUMN summary TEXT NOT NULL DEFAULT ''")
            if "hrr_vector" not in columns:
                db.execute("ALTER TABLE memories ADD COLUMN hrr_vector BLOB")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memory_scope ON memories(user_id, project_id)")
            rows = db.execute("SELECT * FROM memories").fetchall()
        for row in rows:
            item = Memory(row["id"], row["user_id"], row["project_id"], row["kind"],
                          row["text"], row["created_at"], json.loads(row["tags_json"] or "[]"),
                          int(row["importance"] or 1), row["summary"] or row["text"][:280])
            self._items[item.id] = item
            if row["hrr_vector"]:
                self._vectors[item.id] = row["hrr_vector"]

    def add(self, user_id, project_id, kind, text, tags=None, importance=1, summary=None):
        clean_text = str(text or "").strip()
        if not clean_text:
            raise ValueError("Memory text is required")
        safe_tags = list(dict.fromkeys(str(t).strip()[:80] for t in (tags or []) if str(t).strip()))[:20]
        safe_importance = max(1, min(5, int(importance or 1)))
        short_summary = str(summary or clean_text).strip()[:280]
        vector_blob = None
        if hrr.available():
            try:
                searchable = " ".join((clean_text[:10000], short_summary, kind, " ".join(safe_tags)))
                vector_blob = hrr.to_bytes(hrr.encode_text(searchable, _HRR_DIM), _HRR_DIM)
            except (TypeError, ValueError, RuntimeError):
                vector_blob = None
        with self._lock, connect() as db:
            m = Memory(str(uuid4()), user_id, project_id, kind, clean_text[:10000],
                       datetime.now(timezone.utc).isoformat(), safe_tags, safe_importance, short_summary)
            self._items[m.id] = m
            db.execute(
                """INSERT INTO memories
                   (id,user_id,project_id,kind,text,created_at,tags_json,importance,summary,hrr_vector)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (m.id, m.user_id, m.project_id, m.kind, m.text, m.created_at,
                 json.dumps(m.tags, ensure_ascii=False), m.importance, m.summary, vector_blob),
            )
            if vector_blob:
                self._vectors[m.id] = vector_blob
            return asdict(m)

    @staticmethod
    def _terms(text):
        return [x for x in re.findall(r"[a-zA-Z0-9_]{2,}|[\u0900-\u097f]{2,}", str(text or "").lower())]

    def search(self, user_id, project_id, query, limit=10, tags=None):
        terms = self._terms(query)
        requested_tags = {str(t).lower() for t in (tags or [])}
        with self._lock:
            items = [m for m in self._items.values()
                     if m.user_id == user_id and m.project_id == project_id]
        scored = []
        now = datetime.now(timezone.utc)
        query_vector = hrr.encode_text(query, _HRR_DIM) if hrr.available() and str(query or "").strip() else None
        legacy_vectors = {}
        for m in items:
            haystack = self._terms(" ".join([m.text, m.summary, m.kind, " ".join(m.tags)]))
            counts = {term: haystack.count(term) for term in set(haystack)}
            lexical = sum(1 + math.log1p(counts.get(term, 0)) for term in set(terms) if counts.get(term, 0))
            vector_signal = 0.0
            if query_vector is not None:
                with self._lock:
                    memory_vector = self._vectors.get(m.id)
                if memory_vector is None:
                    try:
                        searchable = " ".join((m.text, m.summary, m.kind, " ".join(m.tags)))
                        memory_vector = hrr.to_bytes(hrr.encode_text(searchable, _HRR_DIM), _HRR_DIM)
                        legacy_vectors[m.id] = memory_vector
                    except (TypeError, ValueError, RuntimeError):
                        memory_vector = None
                if memory_vector:
                    try:
                        vector_signal = max(
                            0.0, hrr.similarity(query_vector, hrr.from_bytes(memory_vector, _HRR_DIM))
                        )
                    except (TypeError, ValueError, RuntimeError):
                        vector_signal = 0.0
            tag_match = bool(requested_tags.intersection(t.lower() for t in m.tags))
            if requested_tags and not tag_match and not lexical and vector_signal < 0.05:
                continue
            try:
                age_days = max(0.0, (now - datetime.fromisoformat(m.created_at)).total_seconds() / 86400)
            except (ValueError, TypeError):
                age_days = 365
            recency = 0.25 / (1 + age_days / 30)
            score = lexical + vector_signal + (1.5 if tag_match else 0) + (m.importance * 0.2) + recency
            if score > 0:
                scored.append((score, m))
        if legacy_vectors:
            with self._lock, connect() as db:
                for memory_id, blob in legacy_vectors.items():
                    db.execute(
                        "UPDATE memories SET hrr_vector=? WHERE id=? AND user_id=? AND project_id=? AND hrr_vector IS NULL",
                        (blob, memory_id, user_id, project_id),
                    )
                    self._vectors[memory_id] = blob
        scored.sort(key=lambda pair: (-pair[0], pair[1].created_at))
        return [asdict(m) for _, m in scored[:max(1, min(int(limit), 20))]]


memory_store = MemoryStore()
