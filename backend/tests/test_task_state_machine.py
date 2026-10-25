import pytest

from app.tasks.store import TaskStore


def test_task_state_machine_rejects_skipping_required_states():
    store = TaskStore()
    task = store.create("Build a web app", "standard", ["builder"], False)

    with pytest.raises(ValueError, match="Invalid task transition"):
        store.update(task["id"], "VERIFIED")

    assert store.get(task["id"])["status"] == "PLANNED"


def test_sensitive_task_starts_waiting_for_approval():
    store = TaskStore()
    task = store.create("Deploy to production", "premium", ["ops"], True)

    assert task["status"] == "APPROVAL_REQUIRED"
    with pytest.raises(ValueError, match="Invalid task transition"):
        store.update(task["id"], "EXECUTING")


def test_approved_task_can_execute_and_verify():
    store = TaskStore()
    task = store.create("Deploy to production", "premium", ["ops"], True)
    store.update(task["id"], "APPROVED")
    store.update(task["id"], "EXECUTING")
    store.update(task["id"], "EXECUTED")
    store.update(task["id"], "VERIFYING")
    verified = store.update(task["id"], "VERIFIED")

    assert verified["status"] == "VERIFIED"


def test_terminal_rollback_state_cannot_restart():
    store = TaskStore()
    task = store.create("Build a web app", "standard", ["builder"], False)
    store.update(task["id"], "EXECUTING")
    store.update(task["id"], "FAILED")
    store.update(task["id"], "ROLLED_BACK")

    with pytest.raises(ValueError, match="Invalid task transition"):
        store.update(task["id"], "EXECUTING")


def test_api_cannot_mark_approval_as_granted_directly():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.user_store import user_store

    client = TestClient(app)
    user_store.clear()
    token = client.post("/api/auth/signup", json={
        "email": "state-machine@example.com",
        "password": "StrongPass123!",
        "name": "State Machine",
    }).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    task = client.post("/api/tasks", headers=headers, json={
        "text": "Deploy to production"
    }).json()

    response = client.post(
        f"/api/tasks/{task['id']}/status?status=APPROVED", headers=headers
    )
    assert response.status_code == 400
    assert client.get(f"/api/tasks/{task['id']}", headers=headers).json()["status"] == "APPROVAL_REQUIRED"
