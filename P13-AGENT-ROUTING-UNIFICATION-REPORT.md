# P13 — Agent Routing ID Unification

**Status: PARTIAL IMPLEMENTATION — canonical ID resolution added and regression-tested.**  
**Scope guard:** Existing personal chat behavior, old RAG data, memory records, personal stories/context, and their boundaries were not modified. No migration, deletion, reset, rewrite, or re-index was performed.

## What changed
- Added a canonical ID resolver to `backend/app/agents/registry.py`, with legacy-label aliases for the public twelve-agent registry.
- Added authenticated `GET /api/agents/aliases` to expose canonical IDs and known aliases.
- Added authenticated `POST /api/agents/resolve` to normalize a list of agent labels, deduplicate canonical IDs, and report unresolved labels.
- Added `canonical_team()` to the keyword router while retaining the existing `assemble_team()` response for compatibility.
- Added `canonical_team` alongside the existing `team` field in `/api/conversation/plan`. The legacy `team` field is preserved so current clients/tests depending on names such as `backend_engineer` continue to work.
- Added focused regression tests for alias resolution, order/deduplication, authentication, and backward compatibility.

## Verification
- Command: `python -m pytest -q tests` from `backend/`
- Result: **115 passed in 3.79 seconds**.
- This is backend regression evidence only; no claim is made that all 12 agents have live model/tool runtimes or have completed independent real-world tasks.

## Important limitations
- This cycle introduces a common canonical ID contract and compatibility mapping; it does not yet replace every legacy routing implementation with one execution engine.
- Some legacy helper labels are mapped to the nearest public profile for normalization. That mapping is naming/selection compatibility, not proof that the canonical profile has the helper's specialized capability.
- Per-agent model/tool configuration, live tool invocation evidence, agent health checks, browser E2E, Windows startup acceptance, frontend production build, voice round-trip, live Hermes handoff, and backup/restore remain release gates.
- Release remains **NOT READY TO USE / NOT PRODUCTION-CERTIFIED** until those gates pass.

## Files changed
- `backend/app/agents/registry.py`
- `backend/app/routes/agents.py`
- `backend/app/services/agent_router.py`
- `backend/app/routes/conversation.py`
- `backend/tests/test_p13_agent_unification.py`
- `P13-AGENT-ROUTING-UNIFICATION-REPORT.md`
