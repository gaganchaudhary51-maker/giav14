from fastapi.testclient import TestClient
from app.main import app
from app.db.user_store import user_store
import tempfile, pathlib

client=TestClient(app)

def token():
    user_store.clear()
    r=client.post("/api/auth/signup",json={"email":"sandbox@example.com","password":"StrongPass123!","name":"Sandbox"})
    return r.json()["token"]

def test_allowed_python_command():
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d,"check.py").write_text("print('sandbox-ok')",encoding="utf-8")
        r=client.post("/api/sandbox/run",headers={"Authorization":f"Bearer {token()}"},
                      json={"command":["python","check.py"],"cwd":d})
        assert r.status_code==200
        assert r.json()["result"]["returncode"]==0
        assert "sandbox-ok" in r.json()["result"]["stdout"]

def test_disallowed_command():
    with tempfile.TemporaryDirectory() as d:
        r=client.post("/api/sandbox/run",headers={"Authorization":f"Bearer {token()}"},
                      json={"command":["rm","-rf","."],"cwd":d})
        assert r.status_code==403
