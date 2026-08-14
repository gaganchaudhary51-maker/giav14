from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={
        "email":"skills@example.com","password":"StrongPass123!","name":"Skills"
    }).json()["token"]

def test_ui_has_five_domain_references():
    r=client.post("/api/skills/domain",headers={"Authorization":f"Bearer {token()}"},
                  json={"domain":"ui_ux"})
    assert r.status_code==200
    assert len(r.json()["skills"])==5
    assert any(x["reference"]=="Figma AI" for x in r.json()["skills"])

def test_each_domain_has_five():
    h={"Authorization":f"Bearer {token()}"}
    domains=client.get("/api/skills/domains",headers=h).json()["domains"]
    assert len(domains)>=8
    for d in domains:
        r=client.post("/api/skills/domain",headers=h,json={"domain":d})
        assert r.status_code==200
        assert len(r.json()["skills"])==5
