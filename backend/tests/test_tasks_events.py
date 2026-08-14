from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def auth():
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":"task@example.com","password":"StrongPass123!","name":"Task"})
    return r.json()["token"]

def test_task_lifecycle_and_events():
    token=auth(); h={"Authorization":f"Bearer {token}"}
    r=client.post("/api/tasks",headers=h,json={"text":"Build a CRM"})
    assert r.status_code==201
    task=r.json()
    assert task["status"]=="PLANNED"
    assert "qa" in task["team"]
    r=client.post(f"/api/tasks/{task['id']}/status?status=EXECUTING",headers=h)
    assert r.status_code==200
    assert r.json()["status"]=="EXECUTING"
    ev=client.get("/api/events/recent",headers=h)
    assert ev.status_code==200
    assert any(x["type"]=="TASK_CREATED" for x in ev.json()["items"])

def test_sensitive_task_requires_approval():
    token=auth(); h={"Authorization":f"Bearer {token}"}
    r=client.post("/api/tasks",headers=h,json={"text":"deploy to production"})
    assert r.status_code==201
    assert r.json()["approval_required"] is True
