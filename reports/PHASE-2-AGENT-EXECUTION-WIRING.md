# Phase 2 — Agent Execution Wiring

## Implemented
- Added authenticated `POST /api/agents/run` endpoint for 1–5 explicit agent IDs.
- Requires the task to belong to the caller and be in `EXECUTING` state.
- Canonicalizes legacy agent names and rejects unknown IDs before provider calls.
- Invokes the existing opt-in OpenAI-compatible provider sequentially.
- Returns per-agent `COMPLETED` / `FAILED` results and overall `COMPLETED` / `PARTIAL` / `FAILED` status.
- Audit-logs each member success or failure without logging prompt text or output content.
- Explicitly reports that personal memory is not attached and tool execution is disabled.
- Does not modify RAG or memory stores, and does not add autonomous tool access.

## Verification
- Backend suite: **140 passed**.
- New endpoint tests cover authentication, task ownership, task lifecycle guard, canonical aliases, partial provider failures, and rejection of unknown IDs.
- Provider behavior in these new tests is mocked. This is not proof of a live model provider connection.
- External provider calls remain disabled by default; configure provider environment variables explicitly to enable.
- Frontend production build, Windows launcher, live voice/telephony, WhatsApp, and Supabase remain unverified.

## API example
`POST /api/agents/run`

Body:
```json
{
  "task_id": "an-existing-task-id",
  "agent_ids": ["backend", "qa"],
  "prompt": "Review the task and return a concise implementation plan."
}
```

Requires `Authorization: Bearer <token>` and the task must be owned by the authenticated user and already `EXECUTING`.

## Safety boundaries
- Existing personal RAG/memory content is not imported, reset, seeded, or rewritten by this change.
- Provider calls receive only the explicitly supplied prompt.
- No tools are invoked by the provider adapter.
