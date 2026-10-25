from typing import Any
import json
import os

from app.db.sqlite import connect


class ProjectStore:
    """Project repository: MongoDB when configured, durable SQLite otherwise."""

    def __init__(self):
        self._memory: dict[str, dict[str, Any]] = {}
        self._collection = None
        uri = os.getenv("MONGO_URL")
        if uri:
            try:
                from pymongo import MongoClient
                client = MongoClient(uri, serverSelectionTimeoutMS=800)
                client.admin.command("ping")
                self._collection = client[os.getenv("MONGO_DB", "gia")]["projects"]
            except Exception:
                self._collection = None
        if self._collection is None:
            with connect() as db:
                db.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id TEXT PRIMARY KEY,
                        data_json TEXT NOT NULL
                    )
                """)

    def list(self):
        if self._collection is not None:
            return list(self._collection.find({}, {"_id": 0}))
        with connect() as db:
            rows = db.execute("SELECT data_json FROM projects ORDER BY rowid").fetchall()
        return [json.loads(row["data_json"]) for row in rows]

    def create(self, project):
        if self._collection is not None:
            self._collection.insert_one(project.copy())
        else:
            with connect() as db:
                db.execute("INSERT INTO projects(id,data_json) VALUES(?,?)",
                           (project["id"], json.dumps(project)))
        return project

    def clear(self):
        if self._collection is not None:
            self._collection.delete_many({})
        else:
            with connect() as db:
                db.execute("DELETE FROM projects")
        self._memory.clear()
