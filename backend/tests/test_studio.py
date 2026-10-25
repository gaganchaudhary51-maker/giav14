from fastapi.testclient import TestClient
from app.main import app
from app.auth.security import issue_token

client = TestClient(app)

def headers(uid="studio-test-user"):
    return {"Authorization": f"Bearer {issue_token(uid)}"}

def test_studio_lists_ten_pods_and_catalog():
    response = client.get("/api/studio/pods", headers=headers())
    assert response.status_code == 200
    body = response.json()
    assert len(body["pods"]) == 10
    assert body["models"] == ["Kore", "Fenrir", "Zephyr", "Puck"]
    assert body["privacy"]["memory_untouched"] is True

def test_studio_pod_configuration_is_tenant_scoped():
    uid = "studio-tenant-a"
    response = client.put("/api/studio/pods/ritu-reception", headers=headers(uid), json={
        "prompt": "Tenant A receptionist prompt",
        "model": "Kore",
        "channels": ["Voice Call", "Web Chat"],
        "enabled": True
    })
    assert response.status_code == 200
    assert response.json()["pod"]["prompt"] == "Tenant A receptionist prompt"
    other = client.get("/api/studio/pods", headers=headers("studio-tenant-b"))
    pod = next(p for p in other.json()["pods"] if p["id"] == "ritu-reception")
    assert pod["prompt"] != "Tenant A receptionist prompt"

def test_studio_unknown_pod_rejected():
    response = client.put("/api/studio/pods/not-a-pod", headers=headers(), json={
        "prompt": "x", "model": "Puck", "channels": ["Web Chat"], "enabled": True
    })
    assert response.status_code == 404

def test_evolution_requires_provider_and_does_not_silently_change_prompt(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post("/api/agent/evolve", headers=headers(), json={
        "pod_id": "ritu-reception", "failure_logs": ["example failure"], "aht_seconds": 35
    })
    assert response.status_code == 503
    assert "No prompt was changed" in response.json()["detail"]

def test_studio_endpoints_require_auth():
    assert client.get("/api/studio/pods").status_code == 401


def test_call_center_demo_is_explicitly_demo():
    response = client.get("/api/studio/call-center/demo", headers=headers())
    assert response.status_code == 200
    assert response.json()["mode"] == "demo"
    assert "no live telephony" in response.json()["note"]

def test_whatsapp_template_render_only_and_allowlist():
    response = client.post("/api/telephony/whatsapp/template/render", headers=headers(), json={
        "template": "Hi {{name}}, booking {{booking_id}}",
        "variables": {"name": "Asha", "booking_id": "B-123"},
        "allowed_variables": ["name", "booking_id"]
    })
    assert response.status_code == 200
    assert response.json()["rendered"] == "Hi Asha, booking B-123"
    assert response.json()["provider_sent"] is False

def test_whatsapp_template_rejects_unallowlisted_variable():
    response = client.post("/api/telephony/whatsapp/template/render", headers=headers(), json={
        "template": "Hi {{name}}", "variables": {"name": "Asha"}, "allowed_variables": []
    })
    assert response.status_code == 400

def test_voip_webhook_closed_without_secret(monkeypatch):
    monkeypatch.delenv("GIA_VOIP_WEBHOOK_SECRET", raising=False)
    response = client.post("/api/telephony/webhooks/voip/incoming", json={"call_id": "test-call"})
    assert response.status_code == 503
