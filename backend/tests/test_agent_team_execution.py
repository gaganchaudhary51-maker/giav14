import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth.security import issue_token
from app.tasks.store import task_store
from app.agents import provider_adapter


client = TestClient(app)


def _executing_task(owner="agent-team-test"):
    task = task_store.create("test agent team", "standard", ["backend"], False, owner_id=owner)
    task_store.update(task["id"], "EXECUTING", owner_id=owner)
    return task


def test_agent_team_endpoint_requires_authentication():
    response = client.post("/api/agents/run", json={
        "task_id": "nope", "agent_ids": ["backend"], "prompt": "test"
    })
    assert response.status_code == 401


def test_agent_team_endpoint_checks_task_ownership():
    task = _executing_task("owner-a")
    response = client.post("/api/agents/run", headers={
        "Authorization": "Bearer " + issue_token("owner-b")
    }, json={"task_id": task["id"], "agent_ids": ["backend"], "prompt": "test"})
    assert response.status_code == 404


def test_agent_team_endpoint_requires_executing_task():
    task = task_store.create("not executing", "standard", ["backend"], False, owner_id="owner-c")
    response = client.post("/api/agents/run", headers={
        "Authorization": "Bearer " + issue_token("owner-c")
    }, json={"task_id": task["id"], "agent_ids": ["backend"], "prompt": "test"})
    assert response.status_code == 409


def test_agent_team_runs_canonicalized_agents_and_reports_partial_failures(monkeypatch):
    task = _executing_task("owner-d")
    def fake_invoke(agent_id, prompt):
        if agent_id == "qa":
            raise RuntimeError("provider_connection_failed")
        return {"agent_id": agent_id, "provider": "mock", "model": "test-model",
                "status": "COMPLETED", "output": "ok",
                "personal_memory_attached": False, "tools_invoked": []}
    monkeypatch.setattr(provider_adapter, "invoke", fake_invoke)
    response = client.post("/api/agents/run", headers={
        "Authorization": "Bearer " + issue_token("owner-d")
    }, json={"task_id": task["id"], "agent_ids": ["backend_engineer", "qa"], "prompt": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PARTIAL"
    assert data["completed_count"] == 1
    assert [r["agent_id"] for r in data["results"]] == ["backend", "qa"]
    assert data["results"][1]["status"] == "FAILED"
    assert data["personal_memory_attached"] is False
    assert data["tool_execution_enabled"] is False


def test_agent_team_rejects_unknown_agents_before_any_provider_call(monkeypatch):
    task = _executing_task("owner-e")
    calls = []
    monkeypatch.setattr(provider_adapter, "invoke", lambda *args: calls.append(args))
    response = client.post("/api/agents/run", headers={
        "Authorization": "Bearer " + issue_token("owner-e")
    }, json={"task_id": task["id"], "agent_ids": ["backend", "not-real"], "prompt": "test"})
    assert response.status_code == 400
    assert calls == []
