# P12 — 12-Agent Readiness Audit

**Status: AUDIT COMPLETE — 12 profiles are registered; 12 independently executable agents are NOT verified.**  
**Scope boundary:** This cycle audited agent registry, orchestration, execution gates, tests, and documentation only. It did not modify existing personal chat, RAG, memory, story/context, retrieval, or privacy-boundary code.

## Executive result

- `backend/app/agents/registry.py` declares the requested 12 profiles.
- Authenticated `GET /api/agents` lists profile metadata; `POST /api/agents/assemble` selects profiles by domain/capability.
- `backend/app/core/agent_team.py` separately assembles a team using a different set of internal names, including `project_manager`, `rag_engineer`, `ai_engineer`, `code_analyzer`, and `debugger`. This is not aligned to the public twelve-profile registry.
- `backend/app/services/agent_router.py` is a third keyword router and includes `builder`, which is not one of the twelve public profiles.
- `backend/app/execution/runner.py` persists allowlisted action records (READ_FILE, LIST_FILES, RUN_TESTS, RUN_BUILD, LINT, FORMAT). It explicitly documents that it records tool results, not arbitrary shell runs. This is not an agent-specific model/tool runtime and does not prove an agent actually performed the action.
- The current code therefore provides **agent profile metadata + team-selection/routing scaffolding + a guarded execution-record mechanism**, not evidence of twelve autonomous agents with configured models, tools, health checks, and independently verified outputs.

## Readiness matrix

Status meanings: **PARTIAL** = a profile and some related routing/skills or app capability exist, but agent-specific execution is unproven. **BLOCKED** = profile metadata exists, but no dedicated executable runtime/tool configuration was found in the audited paths.

| # | Profile | Evidence found | Status | To verify/complete |
|---:|---|---|---|---|
| 1 | Planner (`planner`) | Registry profile; task creation has team assembly/model-tier routing | PARTIAL | Dedicated planner execution, plan quality acceptance, output provenance |
| 2 | Architect (`architect`) | Registry profile; appears in `agent_team.assemble()` for build-like requests | PARTIAL | Agent-specific runtime/tool invocation and architecture acceptance test |
| 3 | UI/UX (`ui`) | Registry profile; `ui_ux` domain skills listed | PARTIAL | Actual design tool invocation and UI artifact acceptance |
| 4 | Frontend (`frontend`) | Registry profile; frontend domain skills listed | PARTIAL | Agent-driven code edits/build execution and test evidence |
| 5 | Backend (`backend`) | Registry profile; backend domain skills listed | PARTIAL | Agent-driven API changes and integration acceptance |
| 6 | Database (`database`) | Registry profile; database domain skills listed | PARTIAL | Agent-driven schema/migration operation and rollback test |
| 7 | Research (`research`) | Registry profile; team assembly can select research | PARTIAL | Configured research provider/tool, citations, and repeatable result test |
| 8 | QA (`qa`) | Registry profile; team assembly includes QA on build/change signals; execution allowlist includes RUN_TESTS | PARTIAL | Agent itself running tests and publishing actual tool output/evidence |
| 9 | Security (`security`) | Registry profile; sensitive task assembly and guarded execution patterns exist | PARTIAL | Dedicated security analysis execution and acceptance/security regression suite |
| 10 | DevOps (`devops`) | Registry profile; team assembly can select DevOps for deploy/release signals | PARTIAL | Isolated build/release toolchain, environment checks, approval and rollback acceptance |
| 11 | Analytics (`analytics`) | Registry profile; analytics domain skills listed | PARTIAL | Actual data connector/analysis tool execution and numeric-output validation |
| 12 | Voice (`voice`) | Registry profile advertises STT/TTS/conversation; frontend browser SpeechRecognition and speechSynthesis are present per P10 audit | PARTIAL | Target-browser microphone permission, real voice round-trip, recording/transcription workflow acceptance |

No profile is marked PASS because the audit did not find evidence of a per-agent execution health check plus independently verified tool/model execution. This is an evidence classification, not a claim that every feature is absent.

## Shared blockers and inconsistencies

1. **Three overlapping routing concepts:** public `AgentRegistry`, `app.core.agent_team`, and `app.services.agent_router` use different identifiers and responsibilities.
2. **No unified agent runtime proven:** no audited per-agent model configuration, tool binding, heartbeat/health result, or run record linking an agent to actual tool output.
3. **Execution record semantics:** the execution API accepts an `output` string from the caller and records it as EXECUTED after allowlist/state/ownership checks. This is useful governance scaffolding, but by itself does not execute a tool or authenticate the truth of that output.
4. **UI gap:** the Agents page lists profiles; per-agent run/health/configuration acceptance remains outstanding.
5. **Sensitive operations:** execution runner blocks production deploy and unrestricted shell; do not bypass this as part of agent enablement.

## Verification performed

- Ran backend suite from `backend/`: `python -m pytest -q tests`
- Result: **110 passed in 4.20 seconds**.
- This verifies the current backend regression suite only. It does not prove each agent independently works, the Windows startup script runs, frontend production build passes, or the UI/voice/Hermes flows pass end-to-end.

## Scope guard — personal chat, RAG, and memory

Per user instruction, P12 did **not** change existing personal chat behavior, old RAG data, memory records, personal stories/context, or their boundaries. No migration, deletion, reset, rewrite, or re-index was performed on those components.

## Next implementation priorities

1. Define one canonical agent ID/schema and map legacy routing names to it without breaking existing task behavior.
2. Add a unified agent-run record that distinguishes `SELECTED`, `STARTED`, `SUCCEEDED`, `FAILED`, and `BLOCKED`, with tool/action evidence and owner/task linkage.
3. Add explicit per-agent health/config status and fail closed when required model/tool configuration is absent.
4. Execute agent-specific acceptance tests in a local running instance; mark each profile PASS only with evidence.
5. Keep Windows runtime, frontend build, browser E2E, voice round-trip, Hermes live handoff, and database backup/restore as separate release gates.

**Release decision remains: NOT READY TO USE / NOT PRODUCTION-CERTIFIED.**
