from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def auth(email):
    user_store.clear();r=client.post("/api/auth/signup",json={"email":email,"password":"StrongPass123!","name":"Router"})
    return {"Authorization":f"Bearer {r.json()['token']}"}
def test_free_first_and_no_unlimited_claim():
    h=auth("router@example.com")
    r=client.get("/api/voice/providers",headers=h)
    assert r.status_code==200
    x=r.json()
    assert x["policy"]["free_first"] is True
    assert x["policy"]["cheap_auto_switch"] is True
    assert x["policy"]["unlimited_free_claim"] is False
    assert x["stt"]["selected"]["tier"]=="free"
    assert x["tts"]["selected"]["tier"]=="free"
def test_route_endpoint():
    h=auth("router2@example.com")
    r=client.post("/api/voice/route",headers=h,json={"kind":"stt"})
    assert r.status_code==200 and r.json()["selected"]["tier"]=="free"
