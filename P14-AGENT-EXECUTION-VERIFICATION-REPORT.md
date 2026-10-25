# P14 — Agent Execution & Verification

**Result: REGISTRY AND ROUTING REGRESSION CHECKS PASS; LIVE AGENT EXECUTION NOT VERIFIED.**  
**Personal-data scope:** This phase did not modify personal chat, RAG data, memory records, stories, prompts, or their storage boundaries. No migration, reset, re-index, or rewrite was performed.

## What was inspected
- Public registry: `backend/app/agents/registry.py`
- Agent catalog/alias API: `backend/app/routes/agents.py`
- Keyword routing: `backend/app/services/agent_router.py`
- Legacy team selection: `backend/app/core/agent_team.py`
- Orchestration graph and runner: `backend/app/routes/orchestration.py`, `backend/app/orchestration/`
- Execution records: `backend/app/execution/runner.py`, `backend/app/routes/execution.py`
- Model tier selector: `backend/app/core/model_router.py`

## Twelve-agent evidence matrix

| Canonical agent | Profile registered | Selection/routing evidence | Live model/tool execution |
|---|---|---|---|
| Planner | Yes | Legacy default label can normalize to `planner`; orchestration graph accepts registered IDs | Not verified |
| Architect | Yes | Profile and legacy builder/AI aliases normalize to `architect` | Not verified |
| UI/UX | Yes | Keyword and legacy routing labels map to `ui` | Not verified |
| Frontend | Yes | Keyword and legacy routing labels map to `frontend` | Not verified |
| Backend | Yes | Keyword and legacy routing labels map to `backend` | Not verified |
| Database | Yes | Keyword and legacy routing labels map to `database` | Not verified |
| Research | Yes | Keyword and legacy routing labels map to `research` | Not verified |
| QA | Yes | Keyword router can select QA; legacy QA labels normalize | Not verified |
| Security | Yes | Keyword router can select security; legacy security labels normalize | Not verified |
| DevOps | Yes | Keyword and legacy routing labels map to `devops` | Not verified |
| Analytics | Yes | Profile exists; legacy domain router can select analytics on research/analysis/market signals | Not verified |
| Voice | Yes | Profile exists; legacy domain router can select AI agent for voice-related requests, but that is not proof of a voice agent runtime | Not verified |

**Interpretation:** the 12 named profiles and their selection/normalization paths exist. They are not yet proven to be 12 independent workers with configured model providers and specialized tools.

## Important implementation finding
- `backend/app/core/model_router.py` chooses a model *tier* (`fast`, `standard`, or `premium`); this function alone does not call a model provider.
- `backend/app/execution/runner.py` persists an allowlisted action and the supplied output. Its docstring explicitly says it records results rather than running arbitrary shell commands. A `RUN_TESTS`/`RUN_BUILD` record therefore is not, by itself, proof a command actually ran.
- Orchestration graph endpoints track node states and evidence, but state transitions are not equivalent to a live agent independently completing work.
- The keyword router, legacy domain router, canonical registry and orchestration graph still coexist. Full unification is not claimed.
- `READ_FILE`, `LIST_FILES`, `RUN_TESTS`, `RUN_BUILD`, `LINT`, and `FORMAT` are listed as allowed action names; destructive/secret/unrestricted-shell actions are blocked by the execution-record layer.

## Tests
- Added `backend/tests/test_p14_agent_execution_readiness.py` with checks for the 12 unique profiles, alias target integrity, canonical keyword routing, legacy-label normalization, and the execution allowlist/blocked actions.
- Command: `python -m pytest -q tests` from `backend/`
- Result: **120 passed in 3.74 seconds**.

These are backend unit/regression tests, not live provider, browser, Windows startup, or agent task-completion tests.

## Remaining gates
1. Define and configure a real execution adapter per agent (model/provider, permitted tools, timeout/cancellation, and error reporting).
2. Add safe integration tests that invoke the configured adapter and capture real execution evidence.
3. Verify agent-node ownership checks in orchestration state transitions; current `transition` route authenticates a user but does not visibly bind the node to that user's task.
4. Run frontend production build and browser E2E on the target Windows setup.
5. Run live voice round-trip and optional authenticated Hermes handoff tests.

**Release decision: NOT READY TO USE / NOT PRODUCTION-CERTIFIED.** No claim is made that all 12 agents are live or fully autonomous.
