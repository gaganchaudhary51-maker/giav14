from typing import Any
from app.auth.security import hash_password, verify_password
from app.db.store import ProjectStore

class UserStore:
    def __init__(self):
        self._memory: dict[str, dict[str, Any]] = {}
        self._collection = None
        uri = __import__("os").getenv("MONGO_URL")
        if uri:
            try:
                from pymongo import MongoClient
                client = MongoClient(uri, serverSelectionTimeoutMS=800)
                client.admin.command("ping")
                self._collection = client[__import__("os").getenv("MONGO_DB", "gia")]["users"]
            except Exception:
                self._collection = None

    def find_by_email(self, email: str):
        if self._collection is not None:
            return self._collection.find_one({"email": email}, {"_id": 0})
        return next((u for u in self._memory.values() if u["email"] == email), None)

    def find(self, user_id: str):
        if self._collection is not None:
            return self._collection.find_one({"id": user_id}, {"_id": 0})
        return self._memory.get(user_id)

    def create(self, user: dict):
        if self._collection is not None:
            self._collection.insert_one(user.copy())
        else:
            self._memory[user["id"]] = user.copy()
        return user

    def clear(self):
        if self._collection is not None:
            self._collection.delete_many({})
        self._memory.clear()

user_store = UserStore()
