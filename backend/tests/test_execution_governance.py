from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"exec@example.com","password":"StrongPass123!","name":"Exec"}).json()["token"]
def test_allowlisted_execution():
    r=client.post("/api/execution",headers={"Authorization":f"Bearer {token()}"},json={"task_id":"t1","action":"RUN_TESTS","output":"49 passed"})
    assert r.status_code==200 and r.json()["status"]=="EXECUTED"
def test_blocked_sensitive_action():
    r=client.post("/api/execution",headers={"Authorization":f"Bearer {token()}"},json={"task_id":"t2","action":"PRODUCTION_DEPLOY"})
    assert r.status_code==403
def test_unknown_action_rejected():
    r=client.post("/api/execution",headers={"Authorization":f"Bearer {token()}"},json={"task_id":"t3","action":"RUN_ANYTHING"})
    assert r.status_code==400
