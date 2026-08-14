from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def token():
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":"global@example.com","password":"StrongPass123!","name":"Global"})
    return r.json()["token"]

def test_global_memory_contains_legacy_gia_knowledge():
    r=client.post("/api/memory/global/search",headers={"Authorization":f"Bearer {token()}"},
                  json={"query":"GIA AI Studio event bus agent memory","limit":10})
    assert r.status_code==200
    text=" ".join(x.get("text","") for x in r.json()["items"])
    assert "event bus" in text.lower()
    assert "agent memory" in text.lower()

def test_global_memory_contains_universal_project_manager():
    r=client.post("/api/memory/global/search",headers={"Authorization":f"Bearer {token()}"},
                  json={"query":"project isolation rollback evidence","limit":10})
    assert r.status_code==200
    text=" ".join(x.get("text","") for x in r.json()["items"])
    assert "project-isolated" in text.lower() or "rollback" in text.lower()

def test_global_memory_requires_auth():
    r=client.post("/api/memory/global/search",json={"query":"GIA","limit":5})
    assert r.status_code==401
