from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client = TestClient(app)

def test_signup_login_me_and_plan():
    user_store.clear()
    signup = client.post("/api/auth/signup", json={
        "email": "gagan@example.com", "password": "StrongPass123!", "name": "Gagan"
    })
    assert signup.status_code == 201
    token = signup.json()["token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "gagan@example.com"
    plan = client.post("/api/conversation/plan",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Build a customer CRM"})
    assert plan.status_code == 200
    assert "backend_engineer" in plan.json()["team"]
    assert plan.json()["model_tier"] in {"fast","standard","premium"}

def test_invalid_login():
    user_store.clear()
    client.post("/api/auth/signup", json={
        "email": "x@example.com", "password": "StrongPass123!", "name": "X"
    })
    r=client.post("/api/auth/login", json={"email":"x@example.com","password":"wrong"})
    assert r.status_code == 401
