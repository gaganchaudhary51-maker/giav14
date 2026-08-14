from fastapi.testclient import TestClient
from app.main import app
from app.builder.spec import AppSpec
from app.builder.crud_plan import build_crud_plan

client = TestClient(app)

def test_crud_plan_contains_real_stack_and_operations():
    plan = build_crud_plan(AppSpec(name="CRM", resources=["customer", "lead"]))
    assert plan["stack"]["backend"] == "fastapi"
    assert plan["stack"]["database"] == "mongodb"
    assert "create" in plan["operations"]
    assert "customers" in plan["mongodb_collections"]
    assert "leads" in plan["mongodb_collections"]

def test_builder_endpoint():
    r = client.post("/api/builder/crud/plan", json={"name":"CRM","resources":["customer"]})
    assert r.status_code == 200
    assert r.json()["status"] == "planned"
    assert r.json()["plan"]["resources"] == ["customer"]
