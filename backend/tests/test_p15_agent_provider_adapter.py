"""P15 tests for opt-in model adapter and personal-memory isolation."""
import json

import pytest

from app.agents import provider_adapter as adapter


def test_provider_disabled_by_default_and_reports_no_memory_attachment(monkeypatch):
    for key in ("GIA_AGENT_PROVIDER_ENABLED", "GIA_AGENT_BASE_URL", "GIA_AGENT_MODEL", "GIA_AGENT_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    status = adapter.runtime_status()
    assert status["enabled"] is False
    assert status["configured"] is False
    assert status["ready_for_live_calls"] is False
    assert status["personal_memory_attached"] is False
    assert status["tool_execution_enabled"] is False
    assert len(status["agent_ids"]) == 12


def test_provider_configuration_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("GIA_AGENT_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("GIA_AGENT_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("GIA_AGENT_MODEL", "model-test")
    monkeypatch.setenv("GIA_AGENT_API_KEY", "test-only")
    status = adapter.runtime_status()
    assert status["ready_for_live_calls"] is True
    assert "api_key" not in status
    assert "test-only" not in json.dumps(status)


def test_local_ollama_profile_uses_longer_cold_start_timeout(monkeypatch):
    monkeypatch.setenv("GIA_AGENT_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("GIA_AGENT_BASE_URL", "http://127.0.0.1:11434/v1")
    monkeypatch.setenv("GIA_AGENT_MODEL", "qwen3:1.7b")
    monkeypatch.setenv("GIA_AGENT_API_KEY", "ollama")

    config = adapter.get_config()

    assert config.enabled is True
    assert config.timeout_seconds == 180.0


def test_non_loopback_http_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("GIA_AGENT_PROVIDER_ENABLED", "1")
    monkeypatch.setenv("GIA_AGENT_BASE_URL", "http://llm.example/v1")
    monkeypatch.setenv("GIA_AGENT_MODEL", "model-test")
    monkeypatch.setenv("GIA_AGENT_API_KEY", "test-only")
    assert adapter.runtime_status()["reason"] == "base_url_must_use_https_or_loopback"


def test_invocation_uses_only_explicit_prompt_and_no_tools_or_memory(monkeypatch):
    monkeypatch.setenv("GIA_AGENT_PROVIDER_ENABLED", "1")
    monkeypatch.setenv("GIA_AGENT_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("GIA_AGENT_MODEL", "model-test")
    monkeypatch.setenv("GIA_AGENT_API_KEY", "test-only")

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({"choices": [{"message": {"content": "mocked output"}}]}).encode()

    captured = {}
    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data.decode())
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(adapter.urllib.request, "urlopen", fake_urlopen)
    result = adapter.invoke("backend", "Build a health endpoint")
    assert result["status"] == "COMPLETED"
    assert result["output"] == "mocked output"
    assert result["personal_memory_attached"] is False
    assert result["tools_invoked"] == []
    assert captured["body"]["messages"][-1]["content"] == "Build a health endpoint"
    assert "personal memory" in captured["body"]["messages"][0]["content"]
    assert "tools" in captured["body"]["messages"][0]["content"]
    assert "unit-testing" in captured["body"]["messages"][0]["content"]
    assert "tenant-isolation" in captured["body"]["messages"][0]["content"]
    assert "tool-use" not in captured["body"]["messages"][0]["content"]
    assert "root cause" in captured["body"]["messages"][0]["content"]
    assert "regression check" in captured["body"]["messages"][0]["content"]


def test_invoke_rejects_unknown_agent_and_invalid_prompt(monkeypatch):
    with pytest.raises(ValueError, match="Unknown agent"):
        adapter.invoke("unknown-agent", "hello")
    with pytest.raises(ValueError, match="Prompt"):
        adapter.invoke("backend", "  ")
    with pytest.raises(ValueError, match="Prompt"):
        adapter.invoke("backend", "x" * 12001)


def test_invoke_fails_closed_when_provider_is_not_configured(monkeypatch):
    monkeypatch.delenv("GIA_AGENT_PROVIDER_ENABLED", raising=False)
    with pytest.raises(RuntimeError, match="provider_disabled"):
        adapter.invoke("backend", "hello")
