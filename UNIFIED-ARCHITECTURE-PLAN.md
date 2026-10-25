# Unified GIA Platform — Architecture & Delivery Plan

## Target architecture

### One product, one frontend, one API boundary

- **Frontend:** React + TypeScript + Vite, one canonical route per feature, responsive dark command-center design.
- **Main backend:** GIA v14 FastAPI. It remains the product API for auth, projects, tasks, approvals, audit, memory, RAG and orchestration.
- **Agent runtime:** Hermes runs as a separate, version-pinned Python 3.13 service because its source declares `requires-python >=3.11,<3.14`. Do not install it into the current Python 3.14 venv.
- **RAG/memory logic:** selectively port and test useful HRGen Studio logic behind Python interfaces. Do not embed the whole Node app into FastAPI or share unvalidated JSON files as a database.
- **Canonical storage:** SQLite initially, via repository interfaces and migrations. Move to a server database later only if needed.
- **Adapters:** FastAPI calls Hermes through an authenticated, typed adapter. The frontend never calls Hermes/Studio directly.

## Product navigation

1. Home — single chat/command composer, selected project, last plan/result and activity summary.
2. Projects — create, select, inspect project details and files.
3. Agents & Tasks — registry, task lifecycle, progress, tool activity, cancellation and approval queue.
4. Knowledge — document ingestion, indexing status, retrieval test, source references and deletion.
5. Memory — saved facts, summaries, history, search, privacy scope, export and delete.
6. Activity & Audit — chronological event timeline, task outcome and verification evidence.
7. Settings — provider configuration, system health, workspace preferences, privacy and onboarding replay.

Do not add a separate duplicate chat page for each module. Modules should open their canonical page and may open contextual drawers for related details.

## UI/UX direction

- Dark neutral surfaces with restrained violet/magenta accents, readable typography and high contrast.
- Left navigation is stable; project selector stays in one predictable location.
- Main column contains the current task or feature; activity feed is a secondary panel on wide screens and collapses on smaller screens.
- On first visit, a short intro explains projects, planning and verification, then leads to sign-in. It is stored as a browser preference and can be replayed from Settings.
- Every async action has loading, success, empty and error states.
- Show “planned”, “executing”, “verified” as different states. Never label a plan as completed execution.
- Keep privacy controls and memory scope visible. Warn when storage is not durable.
- Accessibility: keyboard focus, labels, button states, responsive layout and no status communicated by color alone.

## Phases and gates

### P1 — Foundation and UX shell (implemented in this delivery)
- Intro/onboarding; canonical navigation; responsive design; real API connection via Vite proxy.
- Functional initial screens for project selection, agent registry, RAG index/search, memory add/search and system status.
- Do not call RAG/memory persistent yet; clearly warn about in-memory storage.
- Gate: API proxy configuration and backend tests verified; frontend build remains to be re-run after dependency installation.

### P2 — Durable storage and migrations
- Introduce SQLite repositories/migrations for users, projects, sessions, tasks, approvals, events, RAG documents/chunks and memory.
- Scope every record by user/workspace/project.
- Implement safe export/import, backup/restore and migration checks.
- Gate: restart persistence, multi-user isolation, deletion/export and migration tests pass.

### P3 — End-to-end GIA task lifecycle
- Define a typed task state machine: planned → approval required/approved → executing → verifying → verified/failed.
- Connect plan, task creation, execution runner, event stream, cancellation and final result.
- Add explicit approvals for destructive/external actions.
- Gate: a harmless real task runs end-to-end and produces inspectable evidence.

### P4 — RAG and personal memory
- Migrate HRGen Studio retrieval ideas (chunking, source metadata, retrieval scoring) into Python service interfaces.
- Start with SQLite FTS5 for lexical search; add an embedding/vector backend behind an interface after quality tests.
- Add source citations, indexing status, deduplication, deletion and per-user/project isolation.
- Store personal memory with source, timestamp, consent/scope and deletion/export support.
- Gate: exact test facts are retrieved; restart preserves data; cross-user leakage tests pass.

### P5 — Hermes adapter
- Install Hermes in an isolated Python 3.13 environment/service.
- Define typed request/response schema, authentication, timeouts, cancellation and audit records.
- Gate tool permissions, skill allowlist, filesystem scope, network access and secret handling.
- Gate: a harmless allowed tool succeeds; an unapproved tool call is rejected and audited.

### P6 — Unified release
- End-to-end tests from UI to FastAPI to storage/agent adapter.
- Production reverse proxy for `/api`, secure secret management, backup/restore drill, security scan and accessibility pass.
- Release only when every feature is backed by a test or an explicit “not configured” state.

## Audit-derived integration decisions

### GIA v14
- Existing FastAPI API and frontend are the primary foundation.
- The submitted backend suite passed 80 tests.
- RAG and memory stores are in-memory today; project/user stores can also fall back to in-memory when MongoDB is not configured.
- The conversation plan endpoint plans but does not guarantee execution.
- Existing frontend pages were mostly a generic placeholder view; P1 makes core screens distinct.

### Hermes Agent
- Keep as a separate runtime and integrate through an adapter.
- Its declared Python range is `>=3.11,<3.14`; Python 3.14 is outside that supported range.
- Do not copy its entire UI or expose its tools directly to the browser.

### HRGen AI Studio
- Reuse selectively reviewed RAG/memory ideas, not the whole application shell.
- Its archive contains populated `.env` files / credential-like values. Rotate them and never distribute those files.
- Its Node launcher/configuration and data paths are not automatically compatible with the GIA v14 Windows path.
- Keep Studio data separate until a reviewed migration has verified record counts and user/workspace ownership.

## Non-negotiable rules

- No destructive migration without a backup and rollback.
- No fabricated success indicators; expose actual API status.
- No automatic import of private memories from another project.
- No real secrets in source archives.
- No claim of production readiness until persistence, auth isolation and end-to-end execution tests pass.


## Implementation progress update (2026-10-21)

- **P1 complete in working copy:** frontend shell, relative API base, Vite proxy, responsive UI, and source audit.
- **P2 complete in working copy:** SQLite persistence for projects, users, RAG chunks, and project memories; MongoDB remains supported.
- **Latest backend verification:** 83 tests passed using an isolated temporary `GIA_DATA_DIR`.
- **P3 next:** durable task/execution/approval/event state, owner-scoped task access, explicit legal state transitions, and reliable audit/event correlation.
- **P4/P5:** Hermes adapter and selective HRGen RAG/memory integration remain planned; they are not represented as already merged.


## Current implementation status (2026-10-21)
- P1 frontend/API shell is implemented; production build and browser E2E verification are still required.
- P2 SQLite fallback is implemented for projects, users, RAG chunks, and project-scoped memories.
- P3 task lifecycle hardening is implemented: central transition rules, approval gating for sensitive tasks, guarded server-managed states, and duplicate approval protection.
- Latest backend suite: 88 passed.
- Remaining: durable task/approval/execution persistence, ownership-scoped authorization, execution-to-task evidence binding, Hermes adapter, selected HRGen RAG/memory integration, and release verification.
\n\n## Delivery status update (P4)\n- P1–P4 implementation work is represented in `files/giav14-main/`.\n- P4 task, approval, and execution records are durable in SQLite; owner checks are in task, execution, and orchestration entry points.\n- Backend test suite currently passes: 92 tests.\n- Remaining before a Ready-to-use release: frontend production build and browser E2E, backup/restore and Windows smoke tests, full authorization audit, Hermes adapter, selective HRGen RAG/memory port, and complete integration verification.\n

## P5 update — Hermes bridge
The GIA-side adapter is implemented behind an opt-in service boundary. A separate bridge must meet `docs/HERMES-BRIDGE-CONTRACT.md`; no Hermes runtime code or HRGen secrets are embedded. Next: selectively port HRGen RAG/memory behavior, then run full release verification.


## P6 update — RAG and memory
Selected HRGen patterns have been ported into GIA-native SQLite stores with project/user scoping. Semantic embedding retrieval is intentionally not enabled yet; the current lexical path stays deterministic and offline-friendly until a provider can be configured and tested. Remaining: frontend build, live Hermes bridge, end-to-end release tests, backup/restore, Windows smoke test.


## P7 update — release hardening
Signup now uses least privilege and production refuses weak/default signing secrets. Knowledge and Memory screens now reflect SQLite persistence and source version history. The automated Windows release-check script has been updated. Release remains gated on the frontend production build, live Hermes bridge, backup/restore, and end-to-end smoke testing.
