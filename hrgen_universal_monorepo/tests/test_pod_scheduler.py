from datetime import datetime, timezone

import pytest

from backend.services import pod_scheduler
from backend.services.pod_scheduler import POD_JOBS, build_job_payload, scheduler_is_configured


def test_scheduled_job_payload_is_explicit_and_excludes_personal_memory():
    job = POD_JOBS[0]
    payload = build_job_payload(job, datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert payload["job_id"] == "swarn-auditor"
    assert payload["pod_role"] == "swarn-auditor"
    assert payload["personal_memory_attached"] is False
    assert payload["tools_invoked"] == []
    assert payload["idempotency_key"]


def test_scheduler_requires_enabled_flag_url_and_token(monkeypatch):
    monkeypatch.setattr(pod_scheduler.settings, "pod_scheduler_enabled", True)
    monkeypatch.setattr(pod_scheduler.settings, "pod_job_webhook_url", "https://internal.example/jobs")
    monkeypatch.setattr(pod_scheduler.settings, "pod_job_webhook_token", "")
    assert scheduler_is_configured() is False
    monkeypatch.setattr(pod_scheduler.settings, "pod_job_webhook_token", "test-secret")
    assert scheduler_is_configured() is True


@pytest.mark.asyncio
async def test_run_job_skips_when_not_configured(monkeypatch):
    monkeypatch.setattr(pod_scheduler.settings, "pod_scheduler_enabled", False)
    monkeypatch.setattr(pod_scheduler.settings, "pod_job_webhook_url", "")
    monkeypatch.setattr(pod_scheduler.settings, "pod_job_webhook_token", "")
    await pod_scheduler.run_job(POD_JOBS[0])


def test_scheduler_rejects_non_tls_remote_callback(monkeypatch):
    monkeypatch.setattr(pod_scheduler.settings, "pod_scheduler_enabled", True)
    monkeypatch.setattr(pod_scheduler.settings, "pod_job_webhook_url", "http://remote.example/jobs")
    monkeypatch.setattr(pod_scheduler.settings, "pod_job_webhook_token", "test-secret")
    assert scheduler_is_configured() is False


@pytest.mark.asyncio
async def test_production_voice_webhook_fails_closed_without_token(monkeypatch):
    from fastapi import HTTPException
    from backend.security import verify_voice_webhook_auth

    with pytest.raises(HTTPException) as error:
        verify_voice_webhook_auth(None, "", "production")
    assert error.value.status_code == 503
