"""P4 regression tests for durable lifecycle stores and tenant boundaries."""
from app.tasks.store import TaskStore
from app.approvals.store import ApprovalStore
from app.execution.runner import ExecutionEngine


def test_task_survives_store_recreation():
    first = TaskStore()
    task = first.create("P4 durable task", "standard", ["qa"], False, owner_id="p4-user")
    second = TaskStore()
    assert second.get(task["id"], owner_id="p4-user")["text"] == "P4 durable task"
    assert second.get(task["id"], owner_id="another-user") is None


def test_approval_survives_store_recreation_and_is_owner_scoped():
    first = ApprovalStore()
    approval = first.request("task-p4", "RUN_BUILD", "verify build", "LOW", "p4-user")
    second = ApprovalStore()
    assert second.get(approval["id"], owner_id="p4-user")["status"] == "PENDING"
    assert second.get(approval["id"], owner_id="another-user") is None
    assert second.resolve(approval["id"], "p4-user", True)["status"] == "APPROVED"
    assert ApprovalStore().get(approval["id"])["status"] == "APPROVED"


def test_execution_survives_store_recreation():
    first = ExecutionEngine()
    item = first.execute("task-p4", "RUN_TESTS", "89 passed", owner_id="p4-user")
    second = ExecutionEngine()
    assert any(x["id"] == item["id"] for x in second.list_for_task("task-p4", owner_id="p4-user"))
    assert second.list_for_task("task-p4", owner_id="another-user") == []


def test_task_api_blocks_cross_owner_read_and_mutation():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.user_store import user_store

    client = TestClient(app)
    user_store.clear()
    first = client.post("/api/auth/signup", json={
        "email":"p4-owner@example.com","password":"StrongPass123!","name":"Owner"
    }).json()["token"]
    first_headers = {"Authorization": f"Bearer {first}"}
    task = client.post("/api/tasks", headers=first_headers, json={"text":"Owner private task"}).json()
    second = client.post("/api/auth/signup", json={
        "email":"p4-other@example.com","password":"StrongPass123!","name":"Other"
    }).json()["token"]
    second_headers = {"Authorization": f"Bearer {second}"}

    assert client.get(f"/api/tasks/{task['id']}", headers=second_headers).status_code == 404
    assert client.post(f"/api/tasks/{task['id']}/status?status=EXECUTING",
                       headers=second_headers).status_code == 404
