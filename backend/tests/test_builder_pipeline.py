from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"buildpipe@example.com","password":"StrongPass123!","name":"Build"}).json()["token"]
def project(h):
    return client.post("/api/projects",headers=h,json={"name":"CRM","description":"builder"}).json()["id"]
def test_non_sensitive_builder_requires_real_execution_tool_separately():
    h={"Authorization":f"Bearer {token()}"}; pid=project(h)
    r=client.post("/api/builder/crud",headers=h,json={"project_id":pid,"entity":"Customer","fields":["name","email"]})
    assert r.status_code==200
    job=r.json()["job"]; assert job["status"]=="PLANNED"
    r=client.post(f"/api/builder/{job['id']}/execute",headers=h)
    assert r.status_code==200 and r.json()["status"]=="VERIFIED"
def test_sensitive_builder_is_approval_gated():
    h={"Authorization":f"Bearer {token()}"}; pid=project(h)
    r=client.post("/api/builder/crud",headers=h,json={"project_id":pid,"entity":"Customer","sensitive":True})
    assert r.status_code==200
    job=r.json()["job"]; assert job["status"]=="APPROVAL_REQUIRED"
    r=client.post(f"/api/builder/{job['id']}/execute",headers=h)
    assert r.status_code==403
