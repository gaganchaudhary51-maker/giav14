# HRGEN Universal Monorepo — Voice Integration Slice

This is a corrected, isolated integration slice inside the canonical GIA v14 worktree. It does not migrate, seed, reset, or rewrite existing personal chats, RAG, or memory.

## Local setup (Python 3.11–3.13 recommended)

```bash
cd hrgen_universal_monorepo
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp .env.example .env  # Windows: copy .env.example .env; fill only credentials you actually have
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Health: `GET http://127.0.0.1:8000/health`
Webhook: `POST http://127.0.0.1:8000/api/voice/webhook` (multipart form; see `/docs`).

Without API keys, health and transcript-only validation can be exercised, but provider-backed generation is intentionally unavailable and returns a clear service error. No real telephone call is placed by this webhook. The HUD's demo toggle is not a telephony dialer.

## Docker Compose

```bash
docker compose up --build
```

The backend runs in the container. Configure provider credentials in a local `.env` file; never commit it. The Kokoro endpoint is configurable and external by default. This compose file does not claim to provision a working TTS server automatically.

## Safety notes
- Configure `VOICE_WEBHOOK_TOKEN` before exposing the webhook. The endpoint checks a bearer token when configured; production deployments should require it.
- Do not pass real personal/health data until access controls, retention, consent, and jurisdictional requirements are reviewed.
- PostgreSQL schema in `governance/database_schema.sql` is a reference migration, not automatically applied.
- RLS policy assumes trusted server-side code sets `app.current_tenant_id` within each transaction. Do not let clients set tenant context.
- Latency and cost figures are not measured by this package.


## Async scheduled pods

Swarn Auditor and Lucas Growth interval jobs are implemented as opt-in asynchronous
callback jobs. They are **disabled by default**. To enable them, configure
`POD_SCHEDULER_ENABLED=true`, `POD_JOB_WEBHOOK_URL`, and `POD_JOB_WEBHOOK_TOKEN`
in the local `.env`. The callback must accept a JSON POST containing `job_id`,
`pod_role`, `triggered_at`, `idempotency_key`, and `prompt`, and return a 2xx
response. Requests include bearer authentication and an `Idempotency-Key` header.
Intervals are clamped to at least 60 seconds. Jobs do not execute GIA agents
directly; they delegate to the explicitly configured callback, so an actual
worker endpoint must be provisioned and tested before claiming scheduled pod
execution. No personal memory/RAG or tools are attached by this scheduler.

For production, set `APP_ENV=production` and configure `VOICE_WEBHOOK_TOKEN`.
Docker Compose binds port 8000 to loopback by default rather than exposing the
voice webhook on every host interface.
