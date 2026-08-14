from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"router@example.com","password":"StrongPass123!","name":"Router"}).json()["token"]

def test_routine_routes_fast():
    r=client.post("/api/models/route",headers={"Authorization":f"Bearer {token()}"},
                  json={"text":"summarize this note"})
    assert r.status_code==200 and r.json()["tier"]=="fast"

def test_engineering_routes_medium():
    r=client.post("/api/models/route",headers={"Authorization":f"Bearer {token()}"},
                  json={"text":"debug the database API"})
    assert r.status_code==200 and r.json()["tier"]=="medium"

def test_repeated_failure_escalates():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/models/escalate",headers=h,json={"text":"simple task","failure_count":2})
    assert r.status_code==200 and r.json()["to"]=="premium"

def test_high_risk_routes_premium():
    r=client.post("/api/models/route",headers={"Authorization":f"Bearer {token()}"},
                  json={"text":"deploy production","risk":"HIGH"})
    assert r.status_code==200 and r.json()["tier"]=="premium"

def test_context_is_budgeted():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/models/context",headers=h,json={
        "task":"fix login","files":["a"*1000,"b"*1000,"c"*1000],
        "memories":["m"*1000,"n"*1000],"char_budget":2500})
    assert r.status_code==200
    assert r.json()["estimated_chars"]<=2600
