import importlib
from pathlib import Path


def test_memory_survives_store_recreation(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    from app.memory.store import MemoryStore
    first = MemoryStore()
    created = first.add("u1", "p1", "note", "Persist the onboarding decision")
    second = MemoryStore()
    found = second.search("u1", "p1", "onboarding")
    assert any(item["id"] == created["id"] for item in found)


def test_rag_survives_store_recreation_and_is_scoped(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    from app.rag.store import RAGStore
    first = RAGStore()
    chunks = first.index("u1", "p1", "notes.txt", "SQLite durability survives application restarts")
    assert chunks
    second = RAGStore()
    assert second.search("u1", "p1", "durability")
    assert second.search("u2", "p1", "durability") == []
    assert second.search("u1", "p2", "durability") == []



def test_user_and_project_records_survive_store_recreation(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    from app.db.store import ProjectStore
    from app.db.user_store import UserStore

    projects = ProjectStore()
    projects.create({"id": "p1", "name": "Persistent Project"})
    users = UserStore()
    users.create({"id": "u1", "email": "person@example.test", "password_hash": "hash"})

    assert ProjectStore().list() == [{"id": "p1", "name": "Persistent Project"}]
    recreated_users = UserStore()
    assert recreated_users.find("u1")["email"] == "person@example.test"
    assert recreated_users.find_by_email("person@example.test")["id"] == "u1"
