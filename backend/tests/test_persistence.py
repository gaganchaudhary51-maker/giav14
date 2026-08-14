from fastapi.testclient import TestClient
from app.main import app
from app.repositories.project_repository import store

client = TestClient(app)

def test_persistence_endpoint():
    r = client.get("/api/system/persistence")
    assert r.status_code == 200
    assert r.json()["backend"] in {"mongodb", "memory-fallback"}

def test_project_repository_boundary():
    store.clear()
    auth = client.post("/api/auth/signup", json={"email": "persistence@example.com", "password": "StrongPass123!", "name": "Persistence"}).json()["token"]
    r = client.post("/api/projects", headers={"Authorization": f"Bearer {auth}"}, json={"name": "Persistence CRM", "description": "test"})
    assert r.status_code == 201
    project_id = r.json()["id"]
    items = client.get("/api/projects", headers={"Authorization": f"Bearer {auth}"}).json()["projects"]
    assert any(p["id"] == project_id for p in items)
