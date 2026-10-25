# P15 — Opt-in Agent Provider Adapter

**Status: adapter implemented and unit-tested; live provider call not verified.**  
**Personal-data boundary:** No old personal chat, RAG corpus, memory record, story, index, or storage boundary was read, migrated, reset, rewritten, or re-indexed. The new adapter only sends the explicit `prompt` in the request. It does not retrieve or attach personal memory. No tools are invoked by the model adapter.

## What changed
- Added `backend/app/agents/provider_adapter.py`, a standard-library OpenAI-compatible chat-completions adapter.
- Provider calls are disabled by default and require explicit environment configuration: `GIA_AGENT_PROVIDER_ENABLED=true`, `GIA_AGENT_BASE_URL`, `GIA_AGENT_MODEL`, and `GIA_AGENT_API_KEY`.
- Remote endpoints must use HTTPS; HTTP is permitted only for localhost/loopback.
- Added authenticated `GET /api/agents/runtime` to report readiness without exposing the API key.
- Added authenticated `POST /api/agents/{agent_id}/invoke`. It requires a task owned by the caller and task state `EXECUTING`. It accepts only a bounded explicit prompt; it does not auto-attach task history, RAG, or memory.
- Model-only invocation is audited with task/agent/model metadata, excluding prompt text and credentials.
- Added adapter configuration examples to `.env.example`; no real credentials were added.

## Verification
- Command: `python -m pytest -q tests` from `backend/`
- Result: **126 passed in 3.93 seconds**.
- New tests cover disabled-by-default behavior, explicit opt-in, HTTPS/loopback validation, mocked provider response, no-memory/no-tools contract, unknown agents, prompt bounds, and fail-closed configuration.
- The provider invocation test uses a mocked HTTP response. No real provider endpoint or credential was available, so no live provider call is claimed.

## Important limits
- This is a model-only adapter, not a full autonomous agent runtime. It does not grant browser, filesystem, shell, database, or other tools to agents.
- All 12 profiles can be addressed through the adapter, but role-specialized tool execution, independent completion evidence, voice round-trip, live Hermes handoff, Windows startup acceptance, frontend production build, browser E2E, and backup/restore remain open.
- Keep provider disabled until you intentionally configure a trusted endpoint. If a remote provider is configured, the explicit prompt you send to the invoke endpoint is sent to that provider. Personal RAG/memory is not automatically included.
- Release remains **NOT READY TO USE / NOT PRODUCTION-CERTIFIED**.

## Files changed
- `backend/app/agents/provider_adapter.py`
- `backend/app/routes/agents.py`
- `backend/tests/test_p15_agent_provider_adapter.py`
- `.env.example`
- `P15-AGENT-PROVIDER-ADAPTER-REPORT.md`
- `BUILD-LOG.md`
- `FINAL-READINESS.md`
- `README-LIBRARY.md`
