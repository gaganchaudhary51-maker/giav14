from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store

client=TestClient(app)

def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"collab@example.com","password":"StrongPass123!","name":"Collab"}).json()["token"]

def test_gia_gini_two_way_collaboration():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/collaboration/send",headers=h,json={
        "sender":"gia","recipient":"gini","message_type":"TASK",
        "content":"Review the architecture and return risks","task_id":"t1"})
    assert r.status_code==200
    r=client.post("/api/collaboration/send",headers=h,json={
        "sender":"gini","recipient":"gia","message_type":"RESULT",
        "content":"Architecture review complete; no blocking issue found","task_id":"t1"})
    assert r.status_code==200
    r=client.get("/api/collaboration/inbox/gia",headers=h)
    assert len(r.json()["items"])>=1
    assert any(x["sender"]=="gini" for x in r.json()["items"])

def test_worker_handoff_and_broadcast():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/collaboration/send",headers=h,json={
        "sender":"agent:ui","recipient":"agent:qa","message_type":"HANDOFF",
        "content":"UI implementation ready for regression test","task_id":"t2"})
    assert r.status_code==200
    r=client.post("/api/collaboration/send",headers=h,json={
        "sender":"gia","recipient":"*","message_type":"TASK",
        "content":"Run project-wide verification","task_id":"t2"})
    assert r.status_code==200
    r=client.get("/api/collaboration/conversation?participants=gia,agent:ui,agent:qa",headers=h)
    assert r.status_code==200
    assert len(r.json()["items"])>=1

def test_unknown_actor_rejected():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/collaboration/send",headers=h,json={
        "sender":"unknown","recipient":"gia","content":"x"})
    assert r.status_code==400
