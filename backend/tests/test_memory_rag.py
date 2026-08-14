from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def signup(email):
    user_store.clear()
    return client.post("/api/auth/signup",json={
        "email":email,"password":"StrongPass123!","name":"Memory"
    }).json()["token"]

def test_project_scoped_memory_retrieval():
    token=signup("memory@example.com")
    h={"Authorization":f"Bearer {token}"}
    assert client.post("/api/memory",headers=h,json={
        "project_id":"crm","kind":"decision","text":"CRM uses MongoDB and FastAPI"
    }).status_code==201
    client.post("/api/memory",headers=h,json={
        "project_id":"other","kind":"note","text":"MongoDB unrelated project"
    })
    r=client.post("/api/memory/search",headers=h,json={
        "project_id":"crm","query":"MongoDB","limit":5
    })
    assert r.status_code==200
    assert len(r.json()["items"])==1
    assert r.json()["items"][0]["project_id"]=="crm"

def test_user_isolation():
    t1=signup("a@example.com")
    h1={"Authorization":f"Bearer {t1}"}
    client.post("/api/memory",headers=h1,json={"project_id":"crm","text":"secret architecture"})
    t2=signup("b@example.com")
    h2={"Authorization":f"Bearer {t2}"}
    r=client.post("/api/memory/search",headers=h2,json={"project_id":"crm","query":"secret"})
    assert r.status_code==200
    assert r.json()["items"]==[]
