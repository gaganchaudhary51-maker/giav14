from fastapi.testclient import TestClient
from app.main import app
from app.projects.store import project_store
from app.db.user_store import user_store
client=TestClient(app)
def auth(email):
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":email,"password":"StrongPass123!","name":"Builder"})
    return {"Authorization":f"Bearer {r.json()['token']}"}, r.json()["user"]["id"]
def test_real_crud_generation_writes_files_and_verifies():
    h,uid=auth("builder-real@example.com")
    p=client.post("/api/projects",headers=h,json={"name":"CRM","description":"test"})
    assert p.status_code==201
    pid=p.json()["id"]
    r=client.post("/api/builder/crud",headers=h,json={"project_id":pid,"entity":"Customer","fields":["name","email"],"roles":["admin","user"]})
    assert r.status_code==200 and r.json()["status"]=="PLANNED"
    jid=r.json()["job"]["id"]
    r=client.post(f"/api/builder/{jid}/execute",headers=h)
    assert r.status_code==200 and r.json()["status"]=="VERIFIED"
    files=project_store.get(pid,uid)["files"]
    assert "backend/app/api/customer.py" in files
    assert "frontend/src/pages/customer/List.tsx" in files
    assert len(r.json()["evidence"][0]["generated_files"])==6
