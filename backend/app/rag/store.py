from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4
import re
import math
import json

from app.db.sqlite import connect


@dataclass
class Chunk:
    id: str
    user_id: str
    project_id: str
    source: str
    text: str
    terms: list[str]
    created_at: str


class RAGStore:
    """Project-scoped durable RAG chunks with source version history and overlap."""

    CHUNK_MAX_CHARS = 1000
    CHUNK_OVERLAP_CHARS = 100

    def __init__(self):
        self._items: dict[str, Chunk] = {}
        self._lock = Lock()
        with connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    text TEXT NOT NULL,
                    terms_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_rag_scope ON rag_chunks(user_id, project_id)")
            db.execute("""
                CREATE TABLE IF NOT EXISTS rag_documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    full_text TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, project_id, source)
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS rag_document_versions (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    full_text TEXT NOT NULL,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    UNIQUE(document_id, version)
                )
            """)
            rows = db.execute("SELECT * FROM rag_chunks").fetchall()
        for row in rows:
            chunk = Chunk(row["id"], row["user_id"], row["project_id"], row["source"],
                          row["text"], json.loads(row["terms_json"]), row["created_at"])
            self._items[chunk.id] = chunk

    def _terms(self, text):
        return [x for x in re.findall(r"[a-zA-Z0-9_]{2,}|[\u0900-\u097f]{2,}", text.lower())
                if x not in {"the", "and", "for", "with", "this", "that"}]

    @classmethod
    def chunk_text(cls, text, max_chars=None, overlap=None):
        """Split text into readable chunks with a small overlap, inspired by HRGen RAG."""
        clean = (text or "").strip()
        max_chars = max(100, int(max_chars or cls.CHUNK_MAX_CHARS))
        overlap = max(0, min(int(overlap if overlap is not None else cls.CHUNK_OVERLAP_CHARS), max_chars // 3))
        if not clean:
            return []
        if len(clean) <= max_chars:
            return [clean]
        chunks = []
        start = 0
        while start < len(clean):
            end = min(len(clean), start + max_chars)
            if end < len(clean):
                # Prefer a nearby paragraph/sentence/word boundary without tiny chunks.
                floor = start + int(max_chars * 0.65)
                candidates = [
                    clean.rfind("\n\n", floor, end),
                    clean.rfind("\n", floor, end),
                    clean.rfind(". ", floor, end),
                    clean.rfind(" ", floor, end),
                ]
                boundary = max(candidates)
                if boundary > start:
                    end = boundary + (2 if clean[boundary:boundary + 2] == ". " else 1)
            piece = clean[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(clean):
                break
            start = max(start + 1, end - overlap)
        return chunks

    def index(self, user_id, project_id, source, text, chunk_size=None, overlap=None, tags=None):
        clean = (text or "").strip()
        source = (source or "").strip()
        if not clean or not source:
            return []
        tags = list(dict.fromkeys(str(t).strip()[:80] for t in (tags or []) if str(t).strip()))[:20]
        pieces = self.chunk_text(clean, chunk_size, overlap)
        now = datetime.now(timezone.utc).isoformat()
        out = []
        with self._lock, connect() as db:
            doc = db.execute(
                "SELECT * FROM rag_documents WHERE user_id=? AND project_id=? AND source=?",
                (user_id, project_id, source),
            ).fetchone()
            # Keep the in-process cache consistent with the current-version index.
            stale_ids = [key for key, item in self._items.items()
                         if item.user_id == user_id and item.project_id == project_id and item.source == source]
            for key in stale_ids:
                del self._items[key]
            if doc:
                next_version = int(doc["version"]) + 1
                db.execute(
                    """INSERT OR IGNORE INTO rag_document_versions
                       (id,document_id,user_id,project_id,source,version,full_text,tags_json,created_at)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (str(uuid4()), doc["id"], user_id, project_id, source, doc["version"],
                     doc["full_text"], doc["tags_json"], doc["updated_at"]),
                )
                db.execute("DELETE FROM rag_chunks WHERE user_id=? AND project_id=? AND source=?",
                           (user_id, project_id, source))
                db.execute(
                    "UPDATE rag_documents SET full_text=?,version=?,tags_json=?,updated_at=? WHERE id=?",
                    (clean, next_version, json.dumps(tags, ensure_ascii=False), now, doc["id"]),
                )
                document_id = doc["id"]
            else:
                db.execute("DELETE FROM rag_chunks WHERE user_id=? AND project_id=? AND source=?",
                           (user_id, project_id, source))
                document_id = str(uuid4())
                next_version = 1
                db.execute(
                    """INSERT INTO rag_documents
                       (id,user_id,project_id,source,full_text,version,tags_json,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (document_id, user_id, project_id, source, clean, next_version,
                     json.dumps(tags, ensure_ascii=False), now, now),
                )
            for piece in pieces:
                c = Chunk(str(uuid4()), user_id, project_id, source, piece,
                          self._terms(piece), now)
                self._items[c.id] = c
                db.execute(
                    "INSERT INTO rag_chunks(id,user_id,project_id,source,text,terms_json,created_at) VALUES(?,?,?,?,?,?,?)",
                    (c.id, c.user_id, c.project_id, c.source, c.text, json.dumps(c.terms), c.created_at),
                )
                out.append(asdict(c))
        return out

    def search(self, user_id, project_id, query, limit=5):
        q = self._terms(query)
        if not q:
            return []
        with self._lock:
            items = [c for c in self._items.values()
                     if c.user_id == user_id and c.project_id == project_id]
        scored = []
        for c in items:
            counts = {t: c.terms.count(t) for t in set(c.terms)}
            score = sum(1 + math.log1p(counts.get(t, 0)) for t in q if counts.get(t, 0))
            if score:
                scored.append((score, c))
        scored.sort(key=lambda x: (-x[0], x[1].created_at))
        results = []
        for score, c in scored[:max(1, min(int(limit), 20))]:
            item = asdict(c)
            item["score"] = round(score, 4)
            results.append(item)
        return results

    def list_documents(self, user_id, project_id):
        with self._lock, connect() as db:
            rows = db.execute(
                """SELECT id,source,version,tags_json,length(full_text) AS character_count,
                          created_at,updated_at
                   FROM rag_documents WHERE user_id=? AND project_id=? ORDER BY updated_at DESC""",
                (user_id, project_id),
            ).fetchall()
        return [{
            "id": r["id"], "source": r["source"], "version": r["version"],
            "tags": json.loads(r["tags_json"]), "character_count": r["character_count"],
            "created_at": r["created_at"], "updated_at": r["updated_at"],
        } for r in rows]

    def version_history(self, user_id, project_id, source):
        with self._lock, connect() as db:
            doc = db.execute(
                "SELECT id,version,full_text,tags_json,created_at,updated_at FROM rag_documents WHERE user_id=? AND project_id=? AND source=?",
                (user_id, project_id, source),
            ).fetchone()
            if not doc:
                return []
            rows = db.execute(
                """SELECT version,full_text,tags_json,created_at FROM rag_document_versions
                   WHERE document_id=? AND user_id=? AND project_id=? ORDER BY version""",
                (doc["id"], user_id, project_id),
            ).fetchall()
        history = [{
            "version": r["version"], "character_count": len(r["full_text"]),
            "tags": json.loads(r["tags_json"]), "created_at": r["created_at"],
        } for r in rows]
        history.append({
            "version": doc["version"], "character_count": len(doc["full_text"]),
            "tags": json.loads(doc["tags_json"]), "created_at": doc["updated_at"], "current": True,
        })
        return history

    def clear_project(self, user_id, project_id):
        with self._lock, connect() as db:
            ids = [k for k, v in self._items.items()
                   if v.user_id == user_id and v.project_id == project_id]
            for key in ids:
                del self._items[key]
            db.execute("DELETE FROM rag_chunks WHERE user_id=? AND project_id=?", (user_id, project_id))
            db.execute("DELETE FROM rag_document_versions WHERE user_id=? AND project_id=?", (user_id, project_id))
            db.execute("DELETE FROM rag_documents WHERE user_id=? AND project_id=?", (user_id, project_id))
            return len(ids)


rag_store = RAGStore()
