from typing import Any
import os

class ProjectStore:
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

    def list(self):
        if self._collection is not None:
            return list(self._collection.find({}, {"_id": 0}))
        return list(self._memory.values())

    def create(self, project):
        if self._collection is not None:
            self._collection.insert_one(project.copy())
        else:
            self._memory[project["id"]] = project.copy()
        return project

    def clear(self):
        if self._collection is not None:
            self._collection.delete_many({})
        self._memory.clear()
