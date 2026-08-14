from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"verify@example.com","password":"StrongPass123!","name":"Verify"}).json()["token"]
def test_verified_requires_evidence():
    h={"Authorization":f"Bearer {token()}"}
    v=client.post("/api/verification",headers=h,json={"task_id":"t1"});assert v.status_code==201
    vid=v.json()["id"]
    assert client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"PLANNED"}).status_code==200
    assert client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"EXECUTING"}).status_code==200
    assert client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"EXECUTED"}).status_code==200
    assert client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"VERIFYING"}).status_code==200
    r=client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"VERIFIED"})
    assert r.status_code==409
    r=client.post(f"/api/verification/{vid}/transition",headers=h,json={"state":"VERIFIED","evidence":[{"test":"pytest","passed":63}]})
    assert r.status_code==200 and r.json()["state"]=="VERIFIED"
def test_model_budget_escalates():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/models/budget",headers=h,json={"task_type":"debug","complexity":"simple","failure_count":2})
    assert r.status_code==200 and r.json()["tier"]=="premium"
def test_model_budget_fast_path():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/models/budget",headers=h,json={"task_type":"classify","complexity":"simple","failure_count":0})
    assert r.status_code==200 and r.json()["tier"]=="fast"
