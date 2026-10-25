from fastapi.testclient import TestClient
from app.main import app
from app.agents.registry import agent_registry
from app.services.agent_router import assemble_team, canonical_team
from app.db.user_store import user_store

client = TestClient(app)


def test_legacy_agent_names_resolve_to_canonical_ids():
    assert agent_registry.canonical_id("backend_engineer") == "backend"
    assert agent_registry.canonical_id("UI/UX") == "ui"
    assert agent_registry.canonical_id("planner") == "planner"
    assert agent_registry.canonical_id("not-a-real-agent") is None


def test_resolve_names_deduplicates_and_preserves_order():
    assert agent_registry.resolve_names(
        ["backend_engineer", "backend", "QA/Test Engineer", "unknown"]
    ) == ["backend", "qa"]


def test_keyword_router_can_emit_canonical_team_without_changing_legacy_output():
    legacy = assemble_team("Build a responsive frontend and backend API")
    canonical = canonical_team("Build a responsive frontend and backend API")
    assert any(item.name == "Backend Engineer" for item in legacy)
    assert "backend" in canonical
    assert "qa" in canonical


def test_agent_alias_endpoint_requires_auth_and_returns_registry_contract():
    user_store.clear()
    assert client.get("/api/agents/aliases").status_code == 401
    signup = client.post("/api/auth/signup", json={
        "email": "p13-agent@example.com", "password": "StrongPass123!", "name": "P13"
    })
    assert signup.status_code == 201
    token = signup.json()["token"]
    response = client.get("/api/agents/aliases",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert "planner" in body["canonical_ids"]
    assert body["aliases"]["backend_engineer"] == "backend"


def test_conversation_plan_keeps_legacy_team_and_adds_canonical_team():
    user_store.clear()
    signup = client.post("/api/auth/signup", json={
        "email": "p13-plan@example.com", "password": "StrongPass123!", "name": "P13"
    })
    token = signup.json()["token"]
    response = client.post("/api/conversation/plan",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Build a customer CRM"})
    assert response.status_code == 200
    body = response.json()
    assert "backend_engineer" in body["team"]
    assert "backend" in body["canonical_team"]
