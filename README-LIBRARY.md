# GIA Library

Working library for consolidating GIA v14 with selected Hermes Agent and HRGen AI Studio capabilities.

## Structure
- `files/giav14-main/` — canonical working source tree; each phase updates this copy.
- `files/BUILD-LOG.md` — phase history and verification.
- `files/*-IMPLEMENTATION-REPORT.md` — implementation reports.
- `files/THREE-SOURCE-AUDIT.md` and `files/UNIFIED-ARCHITECTURE-PLAN.md` — initial audit and integration plan.

## Current progress
- P1: responsive frontend/API shell.
- P2: SQLite persistence for projects/users/RAG/project memory.
- P3: guarded task lifecycle and approval gate.
- P4: durable task, approval, and execution records with ownership checks.

Latest backend verification: **93 tests passed**.

## Release status
**Not yet ready to use as a final release.** Frontend production build and browser E2E, backup/restore, Windows smoke testing, broader authorization review, Hermes adapter, selective HRGen RAG/memory integration, and final integration tests remain.

This is a ChatGPT workspace library, not a direct modification of the user's Windows folder. The final consolidated archive will be generated from this library.

## Latest progress: P5
Hermes is connected through an optional, isolated handoff bridge. It is disabled until configured. See `P5-IMPLEMENTATION-REPORT.md` and `docs/HERMES-BRIDGE-CONTRACT.md`. The backend suite currently passes 100 tests; a live bridge and release end-to-end checks are still pending.

## Latest progress: P6
Selected HRGen RAG/memory patterns are now in GIA: overlap-aware chunking, versioned sources, tags, summaries, and importance-aware recall. Backend tests: 104 passed. See `P6-IMPLEMENTATION-REPORT.md` for scope and release gates.

## Latest progress: P7
Release hardening, Knowledge/Memory UI updates, and Hermes bridge status UI are complete. Backend suite: 110 passed. See `P7-IMPLEMENTATION-REPORT.md` and `RUN-GIA-VERIFY.md`. The package is still pending frontend production build, live Hermes acceptance, and backup/restore/end-to-end checks.


## Final readiness
See `FINAL-READINESS.md`. The current package is not yet certified Ready to Use: frontend production build, live Hermes handoff, browser E2E, and backup/restore remain explicit release gates. The packaged source itself passed all 110 backend tests after extraction.


## Latest progress: P11
A simple Windows startup entry point is included as `START-GIA.bat`. It checks prerequisites, prepares missing local dependencies, launches backend and frontend on `127.0.0.1`, waits for `/api/health`, and then opens the browser. See `P11-STARTUP-GUIDE.md` and `P11-STARTUP-IMPLEMENTATION-REPORT.md`.
Backend tests: 110 passed. Windows startup acceptance and frontend production build are still pending; release remains NOT READY TO USE.


## Latest progress: P12 — agent readiness audit
The 12 registry profiles are documented, but independent executable readiness is not yet proven. The audit identified three overlapping routing/agent-selection paths and an execution mechanism that records allowlisted results rather than itself proving tool execution. See `P12-AGENT-READINESS-REPORT.md`. Backend suite: 110 passed in 4.20s.

**Personal boundary:** P12 did not modify existing personal chat behavior, old RAG data, memory records, personal stories/context, or their boundaries.
\n\n## Latest progress: P13 — agent routing ID unification\nCanonical agent-ID resolution and legacy alias mapping have been added. Authenticated alias/resolve endpoints and a canonical team field are available while legacy response fields remain intact for compatibility. Backend suite: **115 passed in 3.79s**. Personal chat, old RAG, memory records, stories/context, and boundaries were not changed. This does not prove twelve live autonomous agents; see `P13-AGENT-ROUTING-UNIFICATION-REPORT.md`. Release remains not certified.\n

## Latest progress: P14
Agent execution evidence was audited and regression tests were added for the 12-profile registry, alias integrity, routing normalization, and execution action policy. Backend suite: **120 passed**. Profiles/routing are present; live independent execution by all twelve agents is not yet verified. Personal chat, old RAG, memory and stories were left unchanged. See `P14-AGENT-EXECUTION-VERIFICATION-REPORT.md`.


## P15 — Agent Provider Adapter
See `P15-AGENT-PROVIDER-ADAPTER-REPORT.md`. The model-only provider adapter is opt-in and disabled by default. It does not attach personal RAG/memory or invoke tools. Backend tests: 126 passed; live provider call and Windows/UI acceptance remain pending. Personal chat/RAG/memory were not modified.
\n## Universal Agent Pods & Multi-Channel Studio\nSee `UNIVERSAL-AGENT-PODS-STUDIO-REPORT.md` for the new Studio UI, ten pod profiles, tenant-scoped configuration, optional integrations, tests, and outstanding live-provider acceptance gates. Existing project and folder names are preserved.\n