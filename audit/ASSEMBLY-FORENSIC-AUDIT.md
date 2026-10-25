# GIA / Hermes / Studio Assembly Audit

> Historical forensic audit. Its original Hermes-service recommendation was superseded by the user's later direction. The final build keeps GIA's own agents, SQLite RAG/memory, and local HRR memory; it does not run Hermes.

Audit date: 2026-10-24  
Scope: `giav14-main`, `GIA-hermes-agent-main`, and `GIA-v14-CANONICAL-WORKTREE-SINGLE (8).zip` in `C:\Users\pc\Desktop\GIA_JARVIS_AI`.

## Decision

**Take the extracted GIA v14 candidate as the final product shell. Keep the existing Hermes source folder separate and run Hermes as a separate service behind GIA's authenticated adapter.** The ZIP is not a full merge of both existing folders. It is a GIA/Studio-oriented product tree with selected Studio work and a Hermes integration boundary. Do not replace either original folder with the ZIP.

## What was compared

The original ZIP SHA-256 is `A75DB284C18D6E37DB509375DB081919A48AC4BCB09AA977A3263CE30D58DC8C`. Its internal manifest lists 237 file hashes; all 237 matched the archive at baseline (238 archive entries total).

For the file-level source comparison, dependency/cache folders (`.git`, virtual environments, `node_modules`, `__pycache__`, `.pytest_cache`, and `dist`) were excluded. The source comparison of current `giav14-main` (151 files) against the ZIP's `giav14-main` tree (231 files) found; standalone source-tree metadata such as `frontend/tsconfig.tsbuildinfo` was retained:

| Result | Count | Meaning |
|---|---:|---|
| Same relative path and same SHA-256 | 117 | These current GIA files match the ZIP exactly. |
| Same relative path, different SHA-256 | 32 | The ZIP has different contents for existing GIA paths. |
| Current GIA only | 2 | `GIA-VERIFY-20261021-065747.txt`, `frontend/tsconfig.tsbuildinfo`. |
| ZIP tree only | 82 | Files added in the ZIP compared with the current GIA folder. |

The 32 changed paths are `.env.example`, `.gitignore`, `GIA-VERIFY.ps1`, `RUN-GIA-VERIFY.md`, `frontend/vite.config.ts`, `frontend/src/api.ts`, `frontend/src/main.tsx`, `frontend/src/styles.css`, `backend/tests/test_approvals.py`, `backend/tests/test_execution_governance.py`, `backend/tests/test_persistence.py`, `backend/app/main.py`, `backend/app/tasks/store.py`, `backend/app/services/agent_router.py`, `backend/app/routes/agents.py`, `backend/app/routes/approvals.py`, `backend/app/routes/auth.py`, `backend/app/routes/conversation.py`, `backend/app/routes/execution.py`, `backend/app/routes/memory.py`, `backend/app/routes/orchestration.py`, `backend/app/routes/rag.py`, `backend/app/routes/tasks.py`, `backend/app/rag/store.py`, `backend/app/memory/store.py`, `backend/app/execution/runner.py`, `backend/app/db/store.py`, `backend/app/db/user_store.py`, `backend/app/auth/security.py`, `backend/app/approvals/store.py`, `backend/app/agents/registry.py`, and `.github/workflows/ci.yml`.

The existing Hermes source folder contains 12,808 source files after excluding dependency and cache trees. The ZIP has no `GIA-hermes-agent-main/` source subtree and no exact Hermes source-file matches in the archive comparison. Its GIA tree contains an adapter/integration boundary; that is not the Hermes runtime.

## Capabilities by component

| Component | What it can do | Boundary / caveat |
|---|---|---|
| **GIA v14 updated ZIP/candidate** | React/TypeScript/Vite workspace and FastAPI control plane: projects, task planning, approvals, agent orchestration, execution/status surfaces, audit, RAG and memory routes, voice integration, Studio Pods, and Hermes bridge/status UI. | Recommended user-facing shell. The updated ZIP stores users/projects/RAG documents/chunks/memory in SQLite when MongoDB is not configured. RAG and memory retrieval are lexical; no embedding/vector backend is implemented. The 21-Oct source folder predates this persistence work and keeps RAG/memory in process-local dictionaries. |
| **Hermes Agent 0.21.3** | Full standalone agent runtime: CLI/TUI and web dashboard, tools, skills, memory/session search, scheduled work, subagents and messaging gateways including Telegram, Discord, Slack, WhatsApp and Signal. | Keep it isolated behind a typed, authenticated bridge with tool permissions, timeouts and audit. `pyproject.toml` declares Python `>=3.11,<3.14`; the local Python 3.14 environment is outside that range. |
| **HRGen AI Studio slice** | Selected Studio/voice and agent-pod capabilities are represented in the GIA tree and its API/UI. | The complete standalone Studio application is not present as one ready-to-run app. Provider, telephony and messaging connections remain unverified/demo-only. |

The ZIP's `reports/PREVIOUS-MERGE-REPORT.md` says it was assembled from a 150-file GIA base and a 198-file Studio archive, selecting Studio files at shared-path conflicts. That historical merge describes GIA plus Studio. It does not mean the complete current GIA folder and the complete Hermes folder were combined into this ZIP.

## Login availability

No default/demo account or seeded login is documented in the candidate's non-secret source/docs. The original ZIP database has one user row on an `@example.com`/`.test` domain; it is test data, not a reusable login. The password is hashed and cannot be recovered. At the user's request, a separate local-only preview account was created in `local-preview-data`; its password was delivered in chat and is intentionally not recorded in this report. No account was added to either original source folder or the ZIP.

The candidate auth flow was verified through its Vite `/api` proxy: login, `/auth/me`, `/projects`, and `/events/recent` all returned HTTP 200. This verifies the frontend-origin API path, but is not a visual browser click-through or live provider test. The `example.com` address is a local placeholder, not a real mailbox or production identity.

The separate **My AI Studio — 12 Agents** drawer entry points to the user's Google AI Studio project in a new tab. The component is a static external link and makes no GIA API call. The Studio project's source/export is not present in this workspace, so its claimed 12-agent roster and runtime behavior have not been independently source-verified.

## Final build work and checks

The candidate at `GIA-v14-CANONICAL-WORKTREE/giav14-main` is a separate extracted working copy. I left the original source folders and ZIP untouched. In the candidate I added the responsive mobile drawer/navigation and bottom bar, keyboard-accessible project sheet, focus handling, Framer Motion transitions, Lucide icons, and a text-free Three.js hero visual. The visual defers its 132 kB gzip scene chunk until after sign-in and initial page paint, caps device pixel ratio at 2, falls back without WebGL, and is skipped for reduced-motion users. The app UI uses shadcn-inspired sheet/dialog styling; it does not vendor a generated shadcn component library. No words are baked into the visual, and this is responsive WebGL output rather than a fixed 8K image export.

Also fixed dependency advisories through the candidate lockfile update (Vite 6.4.5; `npm audit` reports zero vulnerabilities), added `requirements-test.txt` plus setup guidance so both Python test slices and the async test plugin are declared, and isolated release-test SQLite data in a temporary directory to avoid tests writing into the candidate's database.

Post-edit verification: 145 GIA backend tests passed, 8 HRGen voice tests passed, both Python compilation checks passed, the TypeScript/Vite production build passed, and npm audit found zero vulnerabilities. The mobile intro and sign-in screens were visually inspected at a 434 px viewport; no horizontal overflow was apparent. Vite still prints a warning for the deferred 523 kB uncompressed Three.js chunk (132 kB gzip); check it on slow mobile networks before public launch.

## Release gates still open

1. Add an optional embedding/vector retrieval backend to the ZIP's existing durable, project-scoped SQLite RAG source; preserve lexical fallback and verify restart durability, re-indexing, and cross-user/project isolation for vectors.
2. Run an authenticated dashboard/mobile end-to-end flow, including project sheet and mobile navigation, against the real local API.
3. Qualify Hermes in a supported Python 3.11–3.13 environment and verify the authenticated bridge, permissions and timeouts.
4. Verify real model, speech, Supabase, telephony and messaging connections only when configured; this audit did not exercise live services.
5. Run deployment, backup/restore and production reverse-proxy checks.

So the decision is **GIA candidate for the main build; Hermes remains a separate engine**. This is a build-verified candidate, not a claim that live integrations or production deployment are certified.
