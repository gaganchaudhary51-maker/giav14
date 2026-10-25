from fastapi.testclient import TestClient

from app.main import app
from app.auth.security import issue_token
from app.projects.store import project_store
from app.agents import provider_adapter


def _workspace(owner: str):
    return project_store.create(owner, "Conversation workspace", "", {})


def test_live_conversation_persists_turns_and_scopes_them_to_owner(monkeypatch):
    client = TestClient(app)
    owner = "live-chat-owner-a"
    project = _workspace(owner)
    captured = []

    def fake_invoke(agent_id, prompt, conversation_history=None, **kwargs):
        captured.append((agent_id, prompt, conversation_history or [], kwargs))
        return {"agent_id": agent_id, "output": f"Answer {len(captured)}", "provider": "test"}

    monkeypatch.setattr(provider_adapter, "invoke", fake_invoke)
    headers = {"Authorization": f"Bearer {issue_token(owner)}"}
    first = client.post("/api/conversation/chat", headers=headers,
                        json={"project_id": project["id"], "text": "Check this bug"})
    assert first.status_code == 200, first.text
    data = first.json()
    assert data["answer"] == "Answer 1"
    assert data["agent_id"] == "qa"
    assert data["tool_execution_enabled"] is False
    assert len(data["messages"]) == 2

    second = client.post("/api/conversation/chat", headers=headers,
                         json={"project_id": project["id"], "conversation_id": data["conversation_id"],
                               "text": "What should I verify next?"})
    assert second.status_code == 200, second.text
    assert len(captured[1][2]) == 2
    assert len(second.json()["messages"]) == 4

    listed = client.get("/api/conversation/threads", headers=headers,
                        params={"project_id": project["id"]})
    assert listed.status_code == 200
    assert listed.json()["threads"][0]["id"] == data["conversation_id"]

    other_headers = {"Authorization": f"Bearer {issue_token('live-chat-owner-b')}"}
    hidden = client.get(f"/api/conversation/threads/{data['conversation_id']}", headers=other_headers)
    assert hidden.status_code == 404


def test_live_conversation_requires_owned_workspace(monkeypatch):
    client = TestClient(app)
    owner = "live-chat-owner-c"
    project = _workspace(owner)
    response = client.post(
        "/api/conversation/chat",
        headers={"Authorization": f"Bearer {issue_token('live-chat-owner-d')}"},
        json={"project_id": project["id"], "text": "hello"},
    )
    assert response.status_code == 404
