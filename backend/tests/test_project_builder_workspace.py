from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"builder@example.com","password":"StrongPass123!","name":"Builder"}).json()["token"]
def test_project_isolation_and_crud_spec():
    h={"Authorization":f"Bearer {token()}"}
    p=client.post("/api/projects",headers=h,json={"name":"CRM","description":"customer system"}); assert p.status_code==201
    pid=p.json()["id"]
    r=client.post(f"/api/projects/{pid}/crud-spec",headers=h,json={"entity":"Customer","fields":["name","email","status"]})
    assert r.status_code==200 and r.json()["template"]=="authenticated-crud-saas"
    assert "frontend/src/pages/customer/List.tsx" in r.json()["files"]
    assert r.json()["status"]=="SPEC_GENERATED_NOT_EXECUTED"
def test_real_workspace_edit_and_diff():
    h={"Authorization":f"Bearer {token()}"}
    p=client.post("/api/projects",headers=h,json={"name":"P","description":""}).json()
    r=client.post(f"/api/workspace/{p['id']}/edit",headers=h,json={"changes":{"README.md":"hello\nworld\n"}})
    assert r.status_code==200 and r.json()["status"]=="EDITED"
    assert "hello" in r.json()["diffs"]["README.md"]
def test_unsafe_path_rejected():
    h={"Authorization":f"Bearer {token()}"}
    p=client.post("/api/projects",headers=h,json={"name":"P","description":""}).json()
    r=client.post(f"/api/workspace/{p['id']}/edit",headers=h,json={"changes":{"../secret":"x"}})
    assert r.status_code==400
