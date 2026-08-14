from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def auth(email):
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":email,"password":"StrongPass123!","name":"Runner"})
    return {"Authorization":f"Bearer {r.json()['token']}"}
def make(h,text):
    return client.post("/api/tasks",headers=h,json={"text":text}).json()
def test_safe_task_start_complete_verify():
    h=auth("runner1@example.com");t=make(h,"Build CRM API")
    assert t["status"]=="PLANNED"
    r=client.post("/api/orchestration/start",headers=h,json={"task_id":t["id"]});assert r.status_code==200
    assert r.json()["status"]=="EXECUTING"
    r=client.post("/api/orchestration/complete",headers=h,json={"task_id":t["id"],"evidence":[{"test":"pytest","passed":68}]})
    assert r.status_code==200 and r.json()["status"]=="VERIFIED"
def test_sensitive_task_is_approval_gated():
    h=auth("runner2@example.com");t=make(h,"Deploy to production")
    r=client.post("/api/orchestration/start",headers=h,json={"task_id":t["id"]})
    assert r.status_code==200 and r.json()["status"]=="APPROVAL_REQUIRED"
def test_failure_escalates():
    h=auth("runner3@example.com");t=make(h,"Fix database migration bug")
    r=client.post("/api/orchestration/fail",headers=h,json={"task_id":t["id"],"risk":"LOW"})
    assert r.status_code==200 and r.json()["decision"]["tier"] in {"medium","premium"}
