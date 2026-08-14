from fastapi.testclient import TestClient
from app.main import app
from app.repositories.project_repository import store
import tempfile, os

client=TestClient(app)

def test_crud_checkpoint_creates_evidence():
    with tempfile.TemporaryDirectory() as d:
        old=os.environ.get("GIA_WORKSPACE_ROOT")
        os.environ["GIA_WORKSPACE_ROOT"]=d
        try:
            r=client.post("/api/builder/crud/checkpoint",
                json={"name":"CRM","resources":["customer","lead"]})
            assert r.status_code==200
            body=r.json()
            assert body["status"]=="checkpointed"
            assert body["evidence"]["files_planned"]>0
            assert os.path.exists(body["evidence"]["checkpoint"])
        finally:
            if old is None: os.environ.pop("GIA_WORKSPACE_ROOT",None)
            else: os.environ["GIA_WORKSPACE_ROOT"]=old
