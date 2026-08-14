from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
from app.audit.log import AuditLog
from app.builder.integrity import manifest
import tempfile, pathlib, os

client=TestClient(app)

def auth():
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":"audit@example.com","password":"StrongPass123!","name":"Audit"})
    return r.json()["token"]

def test_audit_hash_chain():
    with tempfile.TemporaryDirectory() as d:
        log=AuditLog()
        log.path=pathlib.Path(d)/"audit.jsonl"
        a=log.append("TEST","system",{"n":1})
        b=log.append("TEST","system",{"n":2})
        assert a["previous_hash"]=="GENESIS"
        assert b["previous_hash"]==a["hash"]
        assert len(a["hash"])==64

def test_audit_api():
    token=auth(); h={"Authorization":f"Bearer {token}"}
    r=client.post("/api/audit/record",headers=h,params={"event_type":"TEST","payload":"ok"})
    assert r.status_code==200
    r=client.get("/api/audit/recent",headers=h)
    assert r.status_code==200
    assert any(x["event_type"]=="TEST" for x in r.json()["items"])

def test_integrity_manifest():
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d)/"a.txt"; p.write_text("hello",encoding="utf-8")
        m=manifest(d)
        assert "a.txt" in m["files"]
        assert len(m["files"]["a.txt"])==64
