"""Opt-in interval jobs for Swarn Auditor and Lucas Growth.

Jobs POST to an explicitly configured internal callback. This module does not
read personal memory/RAG or assume that an external worker exists.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

POD_JOBS: tuple[dict[str, Any], ...] = (
    {
        "job_id": "swarn-auditor",
        "pod_role": "swarn-auditor",
        "interval_seconds": "swarn_auditor_interval_seconds",
        "prompt": "swarn_auditor_prompt",
    },
    {
        "job_id": "lucas-growth",
        "pod_role": "lucas-growth",
        "interval_seconds": "lucas_growth_interval_seconds",
        "prompt": "lucas_growth_prompt",
    },
)


def _callback_url_is_safe(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
        if parsed.scheme == "https" and parsed.hostname:
            return True
        return parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    except ValueError:
        return False


def scheduler_is_configured() -> bool:
    return bool(
        settings.pod_scheduler_enabled
        and _callback_url_is_safe(settings.pod_job_webhook_url)
        and settings.pod_job_webhook_token.strip()
    )


def build_job_payload(job: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    prompt = str(getattr(settings, job["prompt"])).strip()
    if not prompt:
        raise ValueError(f"Prompt is empty for {job['job_id']}")
    idempotency = hashlib.sha256(f"{job['job_id']}:{timestamp}".encode("utf-8")).hexdigest()
    return {
        "job_id": job["job_id"],
        "pod_role": job["pod_role"],
        "triggered_at": timestamp,
        "idempotency_key": idempotency,
        "prompt": prompt,
        "personal_memory_attached": False,
        "tools_invoked": [],
    }


async def run_job(job: dict[str, Any], client: httpx.AsyncClient | None = None) -> None:
    if not scheduler_is_configured():
        logger.warning("Scheduled pod job skipped: scheduler is disabled or callback credentials are missing")
        return
    payload = build_job_payload(job)
    headers = {
        "Authorization": f"Bearer {settings.pod_job_webhook_token}",
        "Idempotency-Key": payload["idempotency_key"],
        "Content-Type": "application/json",
    }
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0))
    try:
        response = await client.post(settings.pod_job_webhook_url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info("Scheduled pod job accepted: %s status=%s", job["job_id"], response.status_code)
    except httpx.HTTPError:
        logger.exception("Scheduled pod job failed: %s", job["job_id"])
    finally:
        if owns_client:
            await client.aclose()


async def _job_loop(job: dict[str, Any], stop: asyncio.Event) -> None:
    interval = max(60, int(getattr(settings, job["interval_seconds"])))
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            await run_job(job)


async def start_pod_scheduler() -> tuple[asyncio.Event, list[asyncio.Task[None]]]:
    stop = asyncio.Event()
    if not settings.pod_scheduler_enabled:
        logger.info("Pod scheduler disabled; no scheduled jobs started")
        return stop, []
    if not _callback_url_is_safe(settings.pod_job_webhook_url) or not settings.pod_job_webhook_token.strip():
        logger.error("Pod scheduler requested but callback URL is unsafe/unset or token is missing; no jobs started")
        return stop, []
    tasks = [asyncio.create_task(_job_loop(job, stop), name=f"pod-job:{job['job_id']}") for job in POD_JOBS]
    logger.info("Pod scheduler started with jobs: %s", ", ".join(job["job_id"] for job in POD_JOBS))
    return stop, tasks


async def stop_pod_scheduler(stop: asyncio.Event, tasks: list[asyncio.Task[None]]) -> None:
    stop.set()
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
