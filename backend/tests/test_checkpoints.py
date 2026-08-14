from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"checkpoint@example.com","password":"StrongPass123!","name":"Checkpoint"}).json()["token"]
def test_checkpoint_and_rollback():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/checkpoints",headers=h,json={"project_id":"crm","label":"known-good","state":{"version":3,"files":["app.py"],"tests":42}})
    assert r.status_code==201
    c=r.json(); assert c["state"]["version"]==3
    assert client.get("/api/checkpoints/crm",headers=h).status_code==200
    r=client.post(f"/api/checkpoints/{c['id']}/rollback",headers=h)
    assert r.status_code==200 and r.json()["status"]=="ROLLBACK_READY"
def test_missing_checkpoint():
    r=client.post("/api/checkpoints/missing/rollback",headers={"Authorization":f"Bearer {token()}"})
    assert r.status_code==404
