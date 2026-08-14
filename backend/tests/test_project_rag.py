from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def signup(email):
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":email,"password":"StrongPass123!","name":"RAG"})
    token=r.json()["token"]
    return {"Authorization":f"Bearer {token}"}
def test_rag_index_search_and_isolation():
    h=signup("rag-a@example.com")
    r=client.post("/api/rag/index",headers=h,json={"project_id":"p1","source":"req.md","text":"customer CRM dashboard authentication roles permissions"})
    assert r.status_code==201 and r.json()["indexed"]>0
    r=client.post("/api/rag/search",headers=h,json={"project_id":"p1","query":"CRM authentication","limit":5})
    assert r.status_code==200 and r.json()["items"]
    r=client.post("/api/rag/search",headers=h,json={"project_id":"p2","query":"CRM authentication","limit":5})
    assert r.status_code==200 and r.json()["items"]==[]
def test_memory_search_keeps_items_contract_and_adds_documents():
    h=signup("rag-b@example.com")
    client.post("/api/memory",headers=h,json={"project_id":"p1","kind":"decision","text":"Use MongoDB for CRM"})
    r=client.post("/api/memory/search",headers=h,json={"project_id":"p1","query":"MongoDB CRM","limit":5})
    assert r.status_code==200 and r.json()["items"]
    assert "documents" in r.json()
