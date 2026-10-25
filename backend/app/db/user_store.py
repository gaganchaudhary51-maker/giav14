from typing import Any
import json
import os

from app.auth.security import hash_password, verify_password
from app.db.sqlite import connect


class UserStore:
    """User repository: MongoDB when configured, durable SQLite otherwise."""

    def __init__(self):
        self._memory: dict[str, dict[str, Any]] = {}
        self._collection = None
        uri = os.getenv("MONGO_URL")
        if uri:
            try:
                from pymongo import MongoClient
                client = MongoClient(uri, serverSelectionTimeoutMS=800)
                client.admin.command("ping")
                self._collection = client[os.getenv("MONGO_DB", "gia")]["users"]
            except Exception:
                self._collection = None
        if self._collection is None:
            with connect() as db:
                db.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        email TEXT NOT NULL UNIQUE,
                        data_json TEXT NOT NULL
                    )
                """)
                db.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

    def find_by_email(self, email: str):
        if self._collection is not None:
            return self._collection.find_one({"email": email}, {"_id": 0})
        with connect() as db:
            row = db.execute("SELECT data_json FROM users WHERE email=?", (email,)).fetchone()
        return json.loads(row["data_json"]) if row else None

    def find(self, user_id: str):
        if self._collection is not None:
            return self._collection.find_one({"id": user_id}, {"_id": 0})
        with connect() as db:
            row = db.execute("SELECT data_json FROM users WHERE id=?", (user_id,)).fetchone()
        return json.loads(row["data_json"]) if row else None

    def create(self, user: dict):
        if self._collection is not None:
            self._collection.insert_one(user.copy())
        else:
            with connect() as db:
                db.execute("INSERT INTO users(id,email,data_json) VALUES(?,?,?)",
                           (user["id"], user["email"], json.dumps(user)))
        return user

    def clear(self):
        if self._collection is not None:
            self._collection.delete_many({})
        else:
            with connect() as db:
                db.execute("DELETE FROM users")
        self._memory.clear()


user_store = UserStore()
