from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def auth(email):
    user_store.clear();r=client.post("/api/auth/signup",json={"email":email,"password":"StrongPass123!","name":"AI"})
    return {"Authorization":f"Bearer {r.json().get("token")}"}
def test_learning_quarantine_and_promotion_gate():
    h=auth("learn-a@example.com")
    r=client.post("/api/learning/learn",headers=h,json={"agent":"frontend_engineer","domain":"frontend","lesson":"Use targeted API state updates","evidence":"test evidence","tests_passed":False})
    assert r.status_code==200 and r.json()["status"]=="QUARANTINED"
    r=client.post("/api/learning/learn",headers=h,json={"agent":"frontend_engineer","domain":"frontend","lesson":"Use typed API contracts","evidence":"pytest passed","tests_passed":True})
    assert r.status_code==200 and r.json()["status"]=="PROMOTED"
def test_team_skills_are_domain_specific():
    h=auth("skills-a@example.com")
    r=client.post("/api/skills/team",headers=h,json={"task":"build a CRM with MongoDB and secure deployment"})
    assert r.status_code==200
    x=r.json()["skills"]
    assert "frontend_engineer" in x and "database_engineer" in x and "security" in x
    assert "react-typescript" in x["frontend_engineer"]
