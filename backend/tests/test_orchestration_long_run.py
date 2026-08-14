from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
client=TestClient(app)
def token():
    user_store.clear()
    return client.post("/api/auth/signup",json={"email":"longrun@example.com","password":"StrongPass123!","name":"LongRun"}).json()["token"]
def test_agent_registry_and_assembly():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/agents/assemble",headers=h,json={"domains":["ui_ux","backend_database"]})
    assert r.status_code==200
    ids={x["id"] for x in r.json()["agents"]}
    assert {"ui","database"} <= ids
def test_task_graph_dependencies():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/orchestration/graph",headers=h,json={"task_id":"build1","nodes":[
      {"name":"UI","agent_id":"ui"},{"name":"API","agent_id":"backend"},
      {"name":"QA","agent_id":"qa","depends_on":[]} ]})
    assert r.status_code==200 and len(r.json()["nodes"])==3
    nodes=r.json()["nodes"]; first=nodes[0]["id"]
    client.post(f"/api/orchestration/node/{first}/COMPLETED",headers=h)
    assert client.get("/api/orchestration/graph/build1",headers=h).status_code==200
def test_live_events():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/events/publish",headers=h,json={"event_type":"AGENT_STARTED","payload":{"agent":"ui"}})
    assert r.status_code==200
    r=client.get("/api/events/recent",headers=h)
    assert r.status_code==200 and any(e["event_type"]=="AGENT_STARTED" for e in r.json()["events"])
def test_unified_commander():
    h={"Authorization":f"Bearer {token()}"}
    r=client.post("/api/commander/dispatch",headers=h,json={"text":"Build a mobile CRM dashboard with MongoDB and tests"})
    assert r.status_code==200
    b=r.json()
    assert "ui_ux" in b["domains"] and "backend_database" in b["domains"]
    assert b["model"] in {"medium","premium"}
    assert len(b["agents"])>=3
