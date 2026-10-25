"""P6 regression tests for versioned RAG and metadata-aware memory."""
from app.rag.store import RAGStore
from app.memory.store import MemoryStore
from app.memory import hrr


def test_rag_reindex_versions_previous_content_and_searches_current_only(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    store = RAGStore()
    store.index("u1", "p1", "requirements.md", "Alpha requirement about customer permissions", tags=["security"])
    store.index("u1", "p1", "requirements.md", "Beta requirement about analytics dashboards", tags=["analytics"])

    current = store.search("u1", "p1", "analytics")
    assert current and any("analytics" in item["text"].lower() for item in current)
    assert not store.search("u1", "p1", "permissions")
    history = store.version_history("u1", "p1", "requirements.md")
    assert [item["version"] for item in history] == [1, 2]
    assert history[-1]["current"] is True
    assert store.list_documents("u1", "p1")[0]["version"] == 2


def test_rag_chunks_overlap_and_keep_content(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    store = RAGStore()
    text = "First sentence. " + ("durable memory and semantic retrieval " * 80)
    chunks = store.index("u1", "p1", "long.txt", text)
    assert len(chunks) > 1
    assert all(len(item["text"]) <= store.CHUNK_MAX_CHARS + 5 for item in chunks)
    assert all(item["text"] for item in chunks)


def test_memory_tags_importance_and_persistence(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    first = MemoryStore()
    created = first.add("u1", "p1", "decision", "Keep backups before migrations",
                        tags=["database", "safety"], importance=5, summary="Back up before migration")
    second = MemoryStore()
    results = second.search("u1", "p1", "unrelated wording", tags=["safety"])
    assert any(item["id"] == created["id"] for item in results)
    item = next(item for item in results if item["id"] == created["id"])
    assert item["importance"] == 5
    assert item["summary"] == "Back up before migration"
    assert item["tags"] == ["database", "safety"]


def test_memory_adds_local_hrr_vector_without_exposing_it(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    store = MemoryStore()
    created = store.add("u1", "p1", "decision", "Use SQLite project memory vectors",
                        tags=["rag", "memory"], importance=4)
    results = store.search("u1", "p1", "SQLite project memory vectors")
    assert results and results[0]["id"] == created["id"]
    assert "hrr_vector" not in created and "hrr_vector" not in results[0]
    if hrr.available():
        assert store._vectors[created["id"]].startswith(b"HRR1")


def test_memory_recall_is_scoped_by_user_and_project(tmp_path, monkeypatch):
    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    store = MemoryStore()
    store.add("u1", "p1", "note", "project-specific secret plan", tags=["private"])
    assert store.search("u2", "p1", "secret") == []
    assert store.search("u1", "p2", "secret") == []


def test_rag_version_and_tags_api_contract():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.auth.security import issue_token
    from uuid import uuid4

    client = TestClient(app)
    headers = {"Authorization": f"Bearer {issue_token('p6-api-owner')}"}
    project_id = f"p6-versioned-api-project-{uuid4()}"
    first = client.post("/api/rag/index", headers=headers, json={
        "project_id": project_id, "source": "architecture.md",
        "text": "Architecture alpha document", "tags": ["architecture", "alpha"],
    })
    second = client.post("/api/rag/index", headers=headers, json={
        "project_id": project_id, "source": "architecture.md",
        "text": "Architecture beta document", "tags": ["architecture", "beta"],
    })
    assert first.status_code == second.status_code == 201
    docs = client.get(f"/api/rag/documents?project_id={project_id}", headers=headers).json()["documents"]
    assert docs[0]["version"] == 2
    history = client.get(
        f"/api/rag/history?project_id={project_id}&source=architecture.md", headers=headers
    ).json()["versions"]
    assert [item["version"] for item in history] == [1, 2]


def test_memory_metadata_api_contract():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.auth.security import issue_token
    from uuid import uuid4

    client = TestClient(app)
    headers = {"Authorization": f"Bearer {issue_token('p6-memory-api-owner')}"}
    project_id = f"p6-memory-api-project-{uuid4()}"
    created = client.post("/api/memory", headers=headers, json={
        "project_id": project_id, "kind": "decision",
        "text": "Always back up before schema migration",
        "summary": "Back up before migration",
        "tags": ["database", "safety"], "importance": 5,
    })
    assert created.status_code == 201
    assert created.json()["importance"] == 5
    found = client.post("/api/memory/search", headers=headers, json={
        "project_id": project_id, "query": "schema", "limit": 5, "tags": ["safety"],
    }).json()["items"]
    assert any(item["id"] == created.json()["id"] for item in found)


def test_memory_store_migrates_legacy_sqlite_schema_without_losing_rows(tmp_path, monkeypatch):
    import sqlite3
    import json

    monkeypatch.setenv("GIA_DATA_DIR", str(tmp_path))
    db_path = tmp_path / "gia.sqlite3"
    with sqlite3.connect(db_path) as db:
        db.execute("""CREATE TABLE memories (
            id TEXT PRIMARY KEY, user_id TEXT NOT NULL, project_id TEXT NOT NULL,
            kind TEXT NOT NULL, text TEXT NOT NULL, created_at TEXT NOT NULL
        )""")
        db.execute(
            "INSERT INTO memories(id,user_id,project_id,kind,text,created_at) VALUES(?,?,?,?,?,?)",
            ("legacy-memory", "legacy-user", "legacy-project", "note",
             "Keep legacy memory available", "2026-01-01T00:00:00+00:00"),
        )
    migrated = MemoryStore()
    found = migrated.search("legacy-user", "legacy-project", "legacy")
    assert any(item["id"] == "legacy-memory" for item in found)
    row = next(item for item in found if item["id"] == "legacy-memory")
    assert row["tags"] == []
    assert row["importance"] == 1
    assert "hrr_vector" not in row
    if hrr.available():
        with sqlite3.connect(db_path) as db:
            assert db.execute("SELECT hrr_vector FROM memories WHERE id='legacy-memory'").fetchone()[0]
