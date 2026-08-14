from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"verify@example.com","password":"StrongPass123!","name":"Verify"}).json()["token"]

def test_verified_requires_evidence_path():
    h={"Authorization":f"Bearer {token()}"}
    v=client.post("/api/verification",headers=h,json={"task_id":"t1"}).json()
    vid=v["id"]
    for state in ["PLANNED","APPROVED","EXECUTING","EXECUTED","VERIFYING"]:
        r=client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":state,"evidence":[state]})
        assert r.status_code==200
    r=client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"VERIFIED","evidence":["pytest: pass","build: pass"]})
    assert r.status_code==200
    body=r.json()
    assert body["state"]=="VERIFIED"
    assert len(body["evidence"])>=7

def test_invalid_transition_rejected():
    h={"Authorization":f"Bearer {token()}"}
    v=client.post("/api/verification",headers=h,json={"task_id":"t2"}).json()
    r=client.post(f"/api/verification/{v['id']}/transition",headers=h,json={"state":"VERIFIED","evidence":["fake"]})
    assert r.status_code==409

def test_verified_is_terminal():
    h={"Authorization":f"Bearer {token()}"}
    v=client.post("/api/verification",headers=h,json={"task_id":"t3"}).json(); vid=v["id"]
    for state in ["PLANNED","APPROVED","EXECUTING","EXECUTED","VERIFYING","VERIFIED"]:
        client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":state})
    r=client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"EXECUTING"})
    assert r.status_code==409
