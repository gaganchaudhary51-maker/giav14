from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def setup():
    user_store.clear()
    token = client.post("/api/auth/signup", json={
        "email":"exec@example.com","password":"StrongPass123!","name":"Exec"
    }).json()["token"]
    h={"Authorization":f"Bearer {token}"}
    task = client.post("/api/tasks", headers=h, json={"text":"Run test suite"}).json()
    started = client.post(f"/api/tasks/{task['id']}/status?status=EXECUTING", headers=h)
    assert started.status_code == 200
    return h, task

def test_allowlisted_execution():
    h, task = setup()
    r=client.post("/api/execution",headers=h,json={
        "task_id":task["id"],"action":"RUN_TESTS","output":"49 passed"
    })
    assert r.status_code==200 and r.json()["status"]=="EXECUTED"
    # Execution record survives repository re-instantiation (new process equivalent).
    from app.execution.runner import ExecutionEngine
    assert len(ExecutionEngine().list_for_task(task["id"])) == 1

def test_blocked_sensitive_action():
    h, task = setup()
    r=client.post("/api/execution",headers=h,json={
        "task_id":task["id"],"action":"PRODUCTION_DEPLOY"
    })
    assert r.status_code==403

def test_unknown_action_rejected():
    h, task = setup()
    r=client.post("/api/execution",headers=h,json={
        "task_id":task["id"],"action":"RUN_ANYTHING"
    })
    assert r.status_code==400

def test_execution_requires_task_owned_by_user():
    h, task = setup()
    user_store.clear()
    other = client.post("/api/auth/signup", json={
        "email":"other-exec@example.com","password":"StrongPass123!","name":"Other"
    }).json()["token"]
    r=client.post("/api/execution",headers={"Authorization":f"Bearer {other}"},json={
        "task_id":task["id"],"action":"RUN_TESTS"
    })
    assert r.status_code==404
