from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def token(email="approval@example.com"):
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":email,"password":"StrongPass123!","name":"Approval"}).json()["token"]

def test_approval_request_resolve_and_audit():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/approvals",headers=h,json={
        "task_id":"t-sensitive","action":"production deploy",
        "reason":"release verified build","risk":"HIGH"})
    assert r.status_code==201
    a=r.json()
    assert a["status"]=="PENDING"
    r=client.post(f"/api/approvals/{a['id']}/resolve",headers=h,json={"approve":True})
    assert r.status_code==200
    assert r.json()["status"]=="APPROVED"
    r=client.get(f"/api/approvals/{a['id']}",headers=h)
    assert r.json()["status"]=="APPROVED"

def test_approval_cannot_be_resolved_twice():
    h={"Authorization":f"Bearer {token('approval2@example.com')}"}
    a=client.post("/api/approvals",headers=h,json={
        "task_id":"t2","action":"delete data","reason":"cleanup","risk":"HIGH"}).json()
    client.post(f"/api/approvals/{a['id']}/resolve",headers=h,json={"approve":False})
    r=client.post(f"/api/approvals/{a['id']}/resolve",headers=h,json={"approve":True})
    assert r.status_code==200
    assert r.json()["status"]=="REJECTED"

def test_approval_requires_auth():
    r=client.post("/api/approvals",json={
        "task_id":"t","action":"deploy","reason":"x","risk":"HIGH"})
    assert r.status_code==401
