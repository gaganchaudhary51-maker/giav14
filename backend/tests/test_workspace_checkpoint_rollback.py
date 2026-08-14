from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def auth():
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":"rollback@example.com","password":"StrongPass123!","name":"Rollback"})
    return {"Authorization":f"Bearer {r.json()['token']}"}
def test_edit_creates_checkpoint_and_rollback_restores():
    h=auth()
    p=client.post("/api/projects",headers=h,json={"name":"RollbackApp","description":""}).json()
    pid=p["id"]
    r=client.post(f"/api/workspace/{pid}/edit",headers=h,json={"changes":{"src/app.py":"v1"}})
    assert r.status_code==200 and r.json()["checkpoint_id"]
    r=client.post(f"/api/workspace/{pid}/edit",headers=h,json={"changes":{"src/app.py":"v2","src/new.py":"new"}})
    assert r.status_code==200
    cp=r.json()["checkpoint_id"]
    r=client.post(f"/api/checkpoints/{cp}/rollback",headers=h)
    assert r.status_code==200 and r.json()["status"]=="ROLLED_BACK"
    listed=client.get(f"/api/projects/{pid}",headers=h).json()
    assert listed["files"]=={"src/app.py":"v1"}
def test_checkpoint_is_tenant_scoped():
    h=auth()
    p=client.post("/api/projects",headers=h,json={"name":"Private","description":""}).json()
    c=client.post("/api/checkpoints",headers=h,json={"project_id":p["id"],"label":"x","state":{"files":{}}})
    assert c.status_code==201
