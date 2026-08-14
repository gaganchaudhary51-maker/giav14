from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def auth(email):
    user_store.clear();r=client.post("/api/auth/signup",json={"email":email,"password":"StrongPass123!","name":"Voice"})
    return {"Authorization":f"Bearer {r.json()['token']}"}
def test_voice_browser_session_and_states():
    h=auth("voice@example.com")
    r=client.get("/api/voice/providers",headers=h)
    assert r.status_code==200 and r.json()["stt"]["browser"] is True and r.json()["unlimited_free"] is False
    r=client.post("/api/voice/sessions",headers=h,json={"provider":"browser","mode":"hands-free"})
    assert r.status_code==201
    sid=r.json()["id"]
    r=client.post(f"/api/voice/sessions/{sid}/state",headers=h,json={"state":"LISTENING"})
    assert r.status_code==200 and r.json()["state"]=="LISTENING"
    r=client.post(f"/api/voice/sessions/{sid}/transcript",headers=h,json={"text":"Build my CRM"})
    assert r.status_code==200 and r.json()["state"]=="THINKING"
def test_voice_session_isolation():
    h1=auth("voice-a@example.com");r=client.post("/api/voice/sessions",headers=h1,json={});sid=r.json()["id"]
    h2=auth("voice-b@example.com")
    assert client.get(f"/api/voice/sessions/{sid}",headers=h2).status_code==404
