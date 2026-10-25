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


def test_unconfigured_chat_returns_setup_guidance_without_creating_empty_thread(monkeypatch):
    client = TestClient(app)
    owner = "live-chat-provider-unconfigured"
    project = _workspace(owner)

    def provider_unavailable(*args, **kwargs):
        raise RuntimeError("provider_disabled")

    monkeypatch.setattr(provider_adapter, "invoke", provider_unavailable)
    headers = {"Authorization": f"Bearer {issue_token(owner)}"}
    response = client.post("/api/conversation/chat", headers=headers,
                           json={"project_id": project["id"], "text": "Please reply"})

    assert response.status_code == 503
    assert response.json()["detail"]["reason"] == "provider_disabled"
    assert "Settings > Configure provider" in response.json()["detail"]["message"]
    threads = client.get("/api/conversation/threads", headers=headers)
    assert threads.status_code == 200
    assert threads.json()["threads"] == []


def test_local_ollama_failure_explains_start_and_model_pull(monkeypatch):
    client = TestClient(app)
    owner = "live-chat-local-ollama"
    project = _workspace(owner)
    monkeypatch.setenv("GIA_AGENT_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("GIA_AGENT_BASE_URL", "http://127.0.0.1:11434/v1")
    monkeypatch.setenv("GIA_AGENT_MODEL", "qwen3:1.7b")
    monkeypatch.setenv("GIA_AGENT_API_KEY", "ollama")

    def provider_unavailable(*args, **kwargs):
        raise RuntimeError("provider_connection_failed")

    monkeypatch.setattr(provider_adapter, "invoke", provider_unavailable)
    headers = {"Authorization": f"Bearer {issue_token(owner)}"}
    response = client.post("/api/conversation/chat", headers=headers,
                           json={"project_id": project["id"], "text": "Hello GIA"})

    assert response.status_code == 503
    assert "Start Ollama" in response.json()["detail"]["message"]
    assert "ollama pull qwen3:1.7b" in response.json()["detail"]["message"]
    threads = client.get("/api/conversation/threads", headers=headers)
    assert threads.json()["threads"] == []
