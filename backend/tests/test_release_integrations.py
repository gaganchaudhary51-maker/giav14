"""Release safety tests for provider and messaging integrations."""
import hashlib
import hmac
import json

from fastapi.testclient import TestClient
from app.main import app
from app.auth.security import issue_token

client = TestClient(app)

def headers(uid="release-smoke-user"):
    return {"Authorization": f"Bearer {issue_token(uid)}"}

def test_provider_runtime_status_never_exposes_secrets(monkeypatch):
    monkeypatch.setenv("GIA_AGENT_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("GIA_AGENT_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("GIA_AGENT_MODEL", "smoke-model")
    monkeypatch.setenv("GIA_AGENT_API_KEY", "this-must-not-leak")
    response = client.get("/api/agents/runtime", headers=headers())
    assert response.status_code == 200
    body = response.text
    assert "this-must-not-leak" not in body
    assert response.json()["ready_for_live_calls"] is True

def test_voip_signed_incoming_webhook_accepts_only_valid_hmac(monkeypatch):
    secret = "test-only-secret"
    monkeypatch.setenv("GIA_VOIP_WEBHOOK_SECRET", secret)
    payload = json.dumps({"call_id": "smoke-call-1"}, separators=(",", ":")).encode()
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    ok = client.post("/api/telephony/webhooks/voip/incoming", content=payload,
                     headers={"Content-Type": "application/json",
                              "X-GIA-Webhook-Signature": "sha256=" + signature})
    assert ok.status_code == 200
    assert ok.json()["accepted"] is True
    assert ok.json()["state"] == "RECEIVED"
    assert "no call was answered" in ok.json()["message"]

    bad = client.post("/api/telephony/webhooks/voip/incoming", content=payload,
                      headers={"Content-Type": "application/json",
                               "X-GIA-Webhook-Signature": "sha256=bad"})
    assert bad.status_code == 401

def test_voip_transcript_webhook_does_not_persist_to_personal_memory(monkeypatch):
    secret = "test-only-secret"
    monkeypatch.setenv("GIA_VOIP_WEBHOOK_SECRET", secret)
    payload = json.dumps({"call_id": "smoke-call-2", "text": "test transcript"},
                         separators=(",", ":")).encode()
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    response = client.post("/api/telephony/webhooks/voip/transcript", content=payload,
                           headers={"Content-Type": "application/json",
                                    "X-GIA-Webhook-Signature": signature})
    assert response.status_code == 200
    assert response.json()["persisted"] is False

def test_whatsapp_template_is_render_only_and_requires_auth():
    response = client.post("/api/telephony/whatsapp/template/render", json={
        "template": "Hello {{name}}", "variables": {"name": "Test"},
        "allowed_variables": ["name"]
    })
    assert response.status_code == 401
    response = client.post("/api/telephony/whatsapp/template/render", headers=headers(), json={
        "template": "Hello {{name}}", "variables": {"name": "Test"},
        "allowed_variables": ["name"]
    })
    assert response.status_code == 200
    assert response.json()["provider_sent"] is False

def test_studio_configuration_is_local_when_supabase_unconfigured(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    response = client.put("/api/studio/pods/ritu-reception", headers=headers("local-only-tenant"), json={
        "prompt": "Release smoke test prompt",
        "model": "Puck",
        "channels": ["Web Chat"],
        "enabled": True
    })
    assert response.status_code == 200
    assert response.json()["persistence"] == "sqlite-local"
