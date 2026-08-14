from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
from app.diagnostics.engine import diagnose, repair_plan

client=TestClient(app)

def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"learn@example.com","password":"StrongPass123!","name":"Learn"}).json()["token"]

def test_validated_learning_is_persisted():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/learning/learn",headers=h,json={"agent":"ui_agent","domain":"ui_ux","lesson":"Use compact mobile navigation","evidence":"mobile regression passed","tests_passed":True})
    assert r.status_code==200 and r.json()["state"]=="VALIDATED"

def test_failed_learning_is_rejected():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/learning/learn",headers=h,json={"agent":"qa_agent","domain":"qa","lesson":"unverified change","evidence":"test failed","tests_passed":False})
    assert r.status_code==200 and r.json()["state"]=="REJECTED"

def test_update_policy_is_governed():
    r=client.get("/api/learning/policy",headers={"Authorization":f"Bearer {token()}"})
    assert r.status_code==200 and r.json()["automatic_code_write"] is False and r.json()["requires_tests"] is True

def test_diagnosis_and_repair_plan():
    d=diagnose("builder",ValueError("bad schema"),"trace evidence"); p=repair_plan(d)
    assert d["severity"]=="ERROR" and p["status"]=="PROPOSED" and "run regression tests" in p["steps"]
